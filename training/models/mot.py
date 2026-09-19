"""Language-free observation/action experts with shared attention and cached prefix K/V.

Each stream owns its projections and feed-forward parameters. Observation queries
never see action keys. Action queries see both streams in one attention operation.
"""

from dataclasses import dataclass

import torch
from torch import nn
from torch.nn import functional as F

from .common import ModelSpec, TimeEmbedding
from .vision import VisionEncoder


@dataclass
class Memory:
    layers: tuple
    valid: torch.Tensor


def split_heads(x, heads):
    return x.reshape(x.shape[0], x.shape[1], heads, -1).transpose(1, 2)


def attend(q, k, v, mask):
    # SDPA's boolean True means allowed, unlike MultiheadAttention's padding mask.
    value = F.scaled_dot_product_attention(q, k, v, attn_mask=mask)
    return value.transpose(1, 2).flatten(2)


class FeedForward(nn.Module):
    def __init__(self, width):
        super().__init__()
        self.input = nn.Linear(width, width * 8, bias=False)
        self.output = nn.Linear(width * 4, width, bias=False)

    def forward(self, x):
        gate, value = self.input(x).chunk(2, dim=-1)
        return self.output(F.silu(gate) * value)


class PrefixLayer(nn.Module):
    def __init__(self, width, attention_width, heads, advance):
        super().__init__()
        self.heads = heads
        self.norm = nn.RMSNorm(width)
        self.kv = nn.Linear(width, attention_width * 2, bias=False)
        # The final observation output has no consumer: do not allocate dead Q/FF parameters.
        self.advance = advance
        if advance:
            self.query = nn.Linear(width, attention_width, bias=False)
            self.output = nn.Linear(attention_width, width, bias=False)
            self.ff_norm = nn.RMSNorm(width)
            self.ff = FeedForward(width)

    def keys(self, x):
        normalized = self.norm(x)
        k, v = self.kv(normalized).chunk(2, dim=-1)
        return normalized, split_heads(k, self.heads), split_heads(v, self.heads)

    def update(self, x, attended):
        x = x + self.output(attended)
        return x + self.ff(self.ff_norm(x))


class AdaptiveNorm(nn.Module):
    def __init__(self, width):
        super().__init__()
        self.norm = nn.RMSNorm(width, elementwise_affine=False)
        self.modulation = nn.Linear(width, width * 3)
        nn.init.normal_(self.modulation.weight, std=0.01)
        nn.init.zeros_(self.modulation.bias)

    def forward(self, x, time):
        scale, shift, gate = self.modulation(time)[:, None].chunk(3, dim=-1)
        return self.norm(x) * (1 + scale) + shift, 1 + gate


class ActionLayer(nn.Module):
    def __init__(self, width, attention_width, heads):
        super().__init__()
        self.heads = heads
        self.norm = AdaptiveNorm(width)
        self.qkv = nn.Linear(width, attention_width * 3, bias=False)
        self.output = nn.Linear(attention_width, width, bias=False)
        self.ff_norm = AdaptiveNorm(width)
        self.ff = FeedForward(width)

    def prepare(self, x, time):
        normalized, gate = self.norm(x, time)
        q, k, v = self.qkv(normalized).chunk(3, dim=-1)
        return *(split_heads(t, self.heads) for t in (q, k, v)), gate

    def update(self, x, attended, time, gate):
        x = x + gate * self.output(attended)
        normalized, gate = self.ff_norm(x, time)
        return x + gate * self.ff(normalized)


class MoT(nn.Module):
    def __init__(self, spec: ModelSpec):
        super().__init__()
        self.spec = spec
        self.vision = VisionEncoder()
        obs_width, action_width = 2 * spec.width, spec.width
        self.visual_projection = nn.Linear(self.vision.output_dim, obs_width)
        self.state_projection = nn.Linear(spec.state_dim, obs_width)
        # Explicit spatial/camera/history identity, shared between cached and joint paths.
        cells = (spec.image_size // 32) ** 2
        self.visual_position = nn.Parameter(
            torch.randn(1, spec.observation_steps, len(spec.cameras), cells, obs_width) * 0.02
        )
        self.state_position = nn.Parameter(torch.randn(1, spec.observation_steps, obs_width) * 0.02)
        self.action_position = nn.Parameter(torch.randn(1, spec.horizon, action_width) * 0.02)
        self.action_input = nn.Linear(spec.action_dim, action_width)
        self.time = TimeEmbedding(action_width)
        self.prefix_layers = nn.ModuleList(
            [PrefixLayer(obs_width, obs_width, spec.heads, i < spec.depth - 1) for i in range(spec.depth)]
        )
        self.action_layers = nn.ModuleList(
            [ActionLayer(action_width, obs_width, spec.heads) for _ in range(spec.depth)]
        )
        self.final_norm = nn.RMSNorm(action_width)
        self.action_output = nn.Linear(action_width, spec.action_dim)

    def prefix(self, images, state, valid):
        visual = self.vision(images).flatten(-2).transpose(-1, -2)
        visual = self.visual_projection(visual) + self.visual_position
        state = self.state_projection(state) + self.state_position
        tokens = torch.cat((visual.flatten(1, 3), state), dim=1)
        mask = torch.cat((valid[:, :, None, None].expand(visual.shape[:4]).flatten(1), valid), dim=1)
        return tokens, mask

    def condition(self, images, state, valid):
        x, mask = self.prefix(images, state, valid)
        layers = []
        for block in self.prefix_layers:
            normalized, k, v = block.keys(x)
            layers.append((k, v))  # Retain the training graph; this is not a detached cache.
            if block.advance:
                q = split_heads(block.query(normalized), self.spec.heads)
                x = block.update(x, attend(q, k, v, mask[:, None, None]))
        return Memory(tuple(layers), mask)

    def predict(self, actions, time, condition, valid=None):
        x, time = self.action_input(actions) + self.action_position, self.time(time)
        if valid is None:
            valid = torch.ones(actions.shape[:2], dtype=torch.bool, device=actions.device)
        allowed = torch.cat((condition.valid, valid), dim=1)[:, None, None]
        for block, (prefix_k, prefix_v) in zip(self.action_layers, condition.layers, strict=True):
            q, k, v, gate = block.prepare(x, time)
            mixed = attend(q, torch.cat((prefix_k, k), dim=2), torch.cat((prefix_v, v), dim=2), allowed)
            x = block.update(x, mixed, time, gate)
        return self.action_output(self.final_norm(x))

    def forward(self, actions, time, images, state, observation_valid, action_valid=None):
        """Joint reference path: one masked attention over both streams at each layer."""
        prefix, prefix_valid = self.prefix(images, state, observation_valid)
        x, time = self.action_input(actions) + self.action_position, self.time(time)
        if action_valid is None:
            action_valid = torch.ones(actions.shape[:2], dtype=torch.bool, device=actions.device)
        allowed = torch.cat((prefix_valid, action_valid), dim=1)
        length = prefix.shape[1]
        for obs, action in zip(self.prefix_layers, self.action_layers, strict=True):
            normalized, pk, pv = obs.keys(prefix)
            q, k, v, gate = action.prepare(x, time)
            k, v = torch.cat((pk, k), dim=2), torch.cat((pv, v), dim=2)
            if obs.advance:
                q = torch.cat((split_heads(obs.query(normalized), self.spec.heads), q), dim=2)
                mask = allowed[:, None, None].expand(-1, 1, q.shape[2], -1).clone()
                mask[:, :, :length, length:] = False
                mixed = attend(q, k, v, mask)
                prefix = obs.update(prefix, mixed[:, :length])
                mixed = mixed[:, length:]
            else:
                mixed = attend(q, k, v, allowed[:, None, None])
            x = action.update(x, mixed, time, gate)
        return self.action_output(self.final_norm(x))

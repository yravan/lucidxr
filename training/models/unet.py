"""FiLM-conditioned temporal U-Net shared by diffusion and flow matching."""

import torch
from torch import nn
from torch.nn import functional as F

from .common import ModelSpec, TimeEmbedding
from .vision import VisionEncoder


class ResidualBlock(nn.Module):
    def __init__(self, source, target, condition):
        super().__init__()
        self.first = nn.Sequential(
            nn.Conv1d(source, target, 3, padding=1), nn.GroupNorm(8, target), nn.SiLU()
        )
        self.film = nn.Sequential(nn.SiLU(), nn.Linear(condition, target * 2))
        self.second = nn.Sequential(
            nn.Conv1d(target, target, 3, padding=1), nn.GroupNorm(8, target), nn.SiLU()
        )
        self.skip = nn.Conv1d(source, target, 1) if source != target else nn.Identity()

    def forward(self, x, condition):
        scale, shift = self.film(condition).unsqueeze(-1).chunk(2, dim=1)
        return self.skip(x) + self.second(self.first(x) * (1 + scale) + shift)


class UNet(nn.Module):
    """condition() runs once per observation; predict() runs per generative step."""

    def __init__(self, spec: ModelSpec):
        super().__init__()
        self.spec = spec
        self.vision = VisionEncoder()
        feature_dim = spec.observation_steps * (
            len(spec.cameras) * self.vision.output_dim + spec.state_dim + 1
        )
        self.observation = nn.Sequential(nn.Linear(feature_dim, spec.width), nn.SiLU())
        self.time = TimeEmbedding(spec.width)
        condition = spec.width * 2
        widths = (spec.width, spec.width * 2, spec.width * 4)
        self.input = nn.Conv1d(spec.action_dim, widths[0], 1)
        self.down = nn.ModuleList([ResidualBlock(w, w, condition) for w in widths])
        self.reduce = nn.ModuleList(
            [nn.Conv1d(a, b, 3, stride=2, padding=1) for a, b in zip(widths, widths[1:])]
        )
        self.middle = ResidualBlock(widths[-1], widths[-1], condition)
        self.up = nn.ModuleList(
            [ResidualBlock(a + b, b, condition) for a, b in zip(widths[:0:-1], widths[-2::-1])]
        )
        self.output = nn.Sequential(
            nn.GroupNorm(8, widths[0]), nn.SiLU(), nn.Conv1d(widths[0], spec.action_dim, 1)
        )

    def condition(self, images, state, valid):
        features = self.vision(images).mean(dim=(-1, -2)).flatten(2)
        observed = torch.cat((features, state), dim=-1) * valid[..., None]
        return self.observation(torch.cat((observed, valid[..., None]), dim=-1).flatten(1))

    def predict(self, actions, time, condition, valid=None):
        # Padding affects the loss; convolutions retain the fixed chunk geometry.
        context = torch.cat((self.time(time), condition), dim=-1)
        x, skips = self.input(actions.transpose(1, 2)), []
        for index, block in enumerate(self.down):
            x = block(x, context)
            if index < len(self.reduce):
                skips.append(x)
                x = self.reduce[index](x)
        x = self.middle(x, context)
        for block, skip in zip(self.up, reversed(skips), strict=True):
            x = F.interpolate(x, size=skip.shape[-1], mode="nearest")
            x = block(torch.cat((x, skip), dim=1), context)
        return self.output(x).transpose(1, 2)

    def forward(self, actions, time, images, state, observation_valid, action_valid=None):
        return self.predict(actions, time, self.condition(images, state, observation_valid), action_valid)

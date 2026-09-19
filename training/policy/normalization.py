"""Fixed affine transforms fitted only on training observations and targets."""

import torch
from torch import nn


class Normalizer(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        for key, size in (("state", state_dim), ("action", action_dim)):
            self.register_buffer(f"{key}_center", torch.zeros(size))
            self.register_buffer(f"{key}_scale", torch.ones(size))

    @torch.no_grad()
    def fit(self, state_min, state_max, action_min, action_max, rotation_indices=()):
        for key, low, high in (("state", state_min, state_max), ("action", action_min, action_max)):
            low, high = torch.as_tensor(low), torch.as_tensor(high)
            if low.shape != getattr(self, f"{key}_center").shape or low.shape != high.shape:
                raise ValueError("Normalization shape mismatch")
            if not torch.isfinite(low).all() or not torch.isfinite(high).all() or (high < low).any():
                raise ValueError("Invalid normalization bounds")
            scale = (high - low) / 2
            getattr(self, f"{key}_center").copy_((low + high) / 2)
            getattr(self, f"{key}_scale").copy_(torch.where(scale > 1e-6, scale, 1))
        if rotation_indices:
            self.action_center[list(rotation_indices)] = 0
            self.action_scale[list(rotation_indices)] = 1

    def normalize(self, key, value):
        return (value.float() - getattr(self, f"{key}_center")) / getattr(self, f"{key}_scale")

    def denormalize_actions(self, value):
        return value.float() * self.action_scale + self.action_center

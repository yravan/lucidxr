"""Tensor contracts shared by the two action networks."""

import math
from dataclasses import dataclass

import torch
from torch import nn


@dataclass(frozen=True)
class ModelSpec:
    state_dim: int
    action_dim: int
    cameras: tuple[str, ...] = ("wrist",)
    observation_steps: int = 2
    horizon: int = 16
    image_size: int = 128
    width: int = 128
    depth: int = 4
    heads: int = 4

    def __post_init__(self):
        object.__setattr__(self, "cameras", tuple(self.cameras))
        if not self.cameras or len(set(self.cameras)) != len(self.cameras):
            raise ValueError("Camera names must be nonempty and unique")
        if any(not isinstance(x, str) or not x for x in self.cameras):
            raise ValueError("Camera names must be nonempty strings")
        for name in (
            "state_dim",
            "action_dim",
            "observation_steps",
            "horizon",
            "image_size",
            "width",
            "depth",
            "heads",
        ):
            if type(getattr(self, name)) is not int or getattr(self, name) < 1:
                raise ValueError(f"{name} must be a positive integer")
        if self.image_size < 32 or self.image_size % 32:
            raise ValueError("Image size must be a multiple of 32")
        if self.width < 32 or self.width % 8 or self.width % self.heads:
            raise ValueError("Width must be >=32 and divisible by 8 and attention heads")


class TimeEmbedding(nn.Module):
    """Continuous sinusoidal features followed by a learned projection."""

    def __init__(self, width):
        super().__init__()
        self.register_buffer("frequency", torch.exp(torch.linspace(0, -math.log(10000), width // 2)))
        self.project = nn.Sequential(nn.Linear(width, width * 4), nn.SiLU(), nn.Linear(width * 4, width))

    def forward(self, time):
        angles = time.float()[:, None] * self.frequency[None] * 1000
        return self.project(torch.cat((angles.sin(), angles.cos()), dim=-1))

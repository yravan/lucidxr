"""A small explicit training configuration; unknown TOML keys are errors."""

import math
import tomllib
from dataclasses import dataclass
from pathlib import Path

from training.models import ModelSpec
from training.policy import PolicySpec


@dataclass(frozen=True)
class TrainConfig:
    policy: str = "flow"
    observation_steps: int = 2
    horizon: int = 16
    width: int = 128
    depth: int = 4
    heads: int = 4
    inference_steps: int = 16
    steps: int = 10000
    batch_size: int = 32
    learning_rate: float = 0.0001
    weight_decay: float = 0.000001
    warmup_steps: int = 500
    gradient_clip: float = 1.0
    ema_decay: float = 0.999
    seed: int = 0
    workers: int = 4
    cpu_threads: int = 2
    log_every: int = 10
    checkpoint_every: int = 1000
    validation_every: int = 1000
    validation_batches: int = 20
    device: str = "cuda"

    def __post_init__(self):
        positive = (
            "steps",
            "batch_size",
            "cpu_threads",
            "log_every",
            "checkpoint_every",
            "validation_every",
            "validation_batches",
        )
        if any(type(getattr(self, key)) is not int or getattr(self, key) < 1 for key in positive):
            raise ValueError("Training counts must be positive integers")
        if any(type(v) is not int or v < 0 for v in (self.workers, self.seed, self.warmup_steps)):
            raise ValueError("Workers, seed and warmup must be nonnegative integers")
        if not 0 <= self.warmup_steps < self.steps:
            raise ValueError("Warmup must be shorter than training")
        if (
            not all(
                math.isfinite(v)
                for v in (self.learning_rate, self.weight_decay, self.gradient_clip, self.ema_decay)
            )
            or self.learning_rate <= 0
            or self.weight_decay < 0
            or self.gradient_clip <= 0
            or not 0 <= self.ema_decay < 1
        ):
            raise ValueError("Invalid optimizer or EMA settings")
        if self.device not in ("cpu", "cuda"):
            raise ValueError("Training device must be cpu or cuda")

    def policy_spec(self, manifest):
        data, contract = manifest["data"], manifest["contract"]
        model = ModelSpec(
            contract["state_dim"],
            contract["action_dim"],
            cameras=tuple(data["cameras"]),
            observation_steps=self.observation_steps,
            horizon=self.horizon,
            image_size=data["image_size"],
            width=self.width,
            depth=self.depth,
            heads=self.heads,
        )
        return PolicySpec(self.policy, model, inference_steps=self.inference_steps)


def read_config(path):
    with Path(path).open("rb") as stream:
        return TrainConfig(**tomllib.load(stream))

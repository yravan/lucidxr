"""Validated, model-independent distributions shared by randomization wrappers."""

from dataclasses import dataclass

import numpy as np
from scipy.spatial.transform import Rotation


@dataclass(frozen=True)
class Uniform:
    low: float
    high: float

    def __post_init__(self):
        if not np.isfinite((self.low, self.high)).all() or self.low > self.high:
            raise ValueError("Uniform requires finite low <= high")

    def sample(self, rng, shape):
        return rng.uniform(self.low, self.high, shape)


@dataclass(frozen=True)
class PositionRandomization:
    """Local-coordinate offsets, or absolute local bounds, in meters."""

    offset: float | tuple[float, float, float] = 0.01
    bounds: tuple[tuple[float, float, float], tuple[float, float, float]] | None = None

    def __post_init__(self):
        value = np.asarray(self.offset)
        if value.shape not in ((), (3,)) or not np.isfinite(value).all() or np.any(value < 0):
            raise ValueError("Position offset must be nonnegative scalar or xyz tuple")
        if self.bounds is not None:
            values = np.asarray(self.bounds)
            if values.shape != (2, 3) or not np.isfinite(values).all() or np.any(values[0] > values[1]):
                raise ValueError("Position bounds must be finite xyz lower/upper tuples")

    def sample(self, rng, baseline):
        if self.bounds is not None:
            return rng.uniform(*self.bounds, size=baseline.shape)
        offset = np.asarray(self.offset)
        return baseline + rng.uniform(-offset, offset, baseline.shape)


@dataclass(frozen=True)
class RotationRandomization:
    """Uniform axis and signed angle bounded by max_angle radians."""

    max_angle: float = 0.087

    def __post_init__(self):
        if not np.isfinite(self.max_angle) or not 0 <= self.max_angle <= np.pi:
            raise ValueError("max_angle must be in [0, pi]")

    def sample(self, rng, count):
        axis = rng.normal(size=(count, 3))
        norm = np.linalg.norm(axis, axis=1, keepdims=True)
        axis = np.divide(axis, norm, out=np.zeros_like(axis), where=norm > 0)
        return Rotation.from_rotvec(axis * rng.uniform(-self.max_angle, self.max_angle, (count, 1)))


def select_ids(model, kind, names):
    if names is None:
        return np.arange(getattr(model, f"n{kind}"), dtype=int)
    if isinstance(names, str) or len(names) != len(set(names)):
        raise ValueError("names must be a sequence of distinct names")
    accessor = getattr(model, "camera" if kind == "cam" else kind)
    return np.array([accessor(name).id for name in names], dtype=int)


def check_range(value, *, low=0.0, high=np.inf, name="range"):
    if value is not None and (not isinstance(value, Uniform) or value.low < low or value.high > high):
        raise ValueError(f"{name} must be Uniform within [{low}, {high}]")

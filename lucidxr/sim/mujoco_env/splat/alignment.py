"""Similarity alignment between a splat reconstruction and simulation world."""

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation


@dataclass(frozen=True)
class SplatAlignment:
    scale: float = 1.0
    position: tuple[float, float, float] = (0.0, 0.0, 0.0)
    euler: tuple[float, float, float] = (0.0, 0.0, 0.0)  # intrinsic XYZ radians

    def __post_init__(self):
        if not np.isfinite(self.scale) or self.scale <= 0:
            raise ValueError("scale must be positive and finite")
        for name in ("position", "euler"):
            value = np.asarray(getattr(self, name))
            if value.shape != (3,) or not np.isfinite(value).all():
                raise ValueError(f"{name} must contain three finite values")

    @classmethod
    def from_json(cls, path):
        """Read legacy collision_tf.json using an explicit file path."""
        data = json.loads(Path(path).read_text())
        return cls(float(data["mesh_scale"]), tuple(data["mesh_pos"]), tuple(data["mesh_euler"]))

    def camera_transform(self):
        """Return inverse rotation and origin; camera rotations must remain orthonormal."""
        return Rotation.from_euler("XYZ", self.euler).as_matrix().T, np.asarray(self.position)

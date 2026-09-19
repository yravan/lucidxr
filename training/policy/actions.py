"""Native command layout and continuous 6D rotations, shared by data and rollout."""

from copy import deepcopy

import numpy as np
from scipy.spatial.transform import Rotation


def quaternion_to_6d(quaternion):
    """wxyz -> first two matrix columns, each stored as a contiguous 3-vector."""
    quaternion = np.asarray(quaternion)
    shape = quaternion.shape[:-1]
    flat = quaternion.reshape(-1, 4)
    matrix = Rotation.from_quat(flat[:, [1, 2, 3, 0]]).as_matrix()
    return matrix[:, :, :2].transpose(0, 2, 1).reshape(*shape, 6)


def rotation_6d_to_quaternion(rotation):
    """Gram-Schmidt with deterministic fallbacks for zero/parallel generated columns."""
    value = np.asarray(rotation, dtype=np.float64)
    first, second = value[..., :3], value[..., 3:]
    norm = np.linalg.norm(first, axis=-1, keepdims=True)
    first = np.where(norm > 1e-8, first / np.maximum(norm, 1e-8), np.array([1.0, 0, 0]))
    second = second - np.sum(first * second, axis=-1, keepdims=True) * first
    norm = np.linalg.norm(second, axis=-1, keepdims=True)
    axis = np.eye(3)[np.argmin(np.abs(first), axis=-1)]
    fallback = axis - np.sum(axis * first, axis=-1, keepdims=True) * first
    second = np.where(norm > 1e-8, second, fallback)
    second = second / np.linalg.norm(second, axis=-1, keepdims=True)
    matrix = np.stack((first, second, np.cross(first, second)), axis=-1)
    quat = Rotation.from_matrix(matrix.reshape(-1, 3, 3)).as_quat(canonical=True)
    return quat[:, [3, 0, 1, 2]].reshape(*value.shape[:-1], 4)


class ActionCodec:
    """ctrl followed by one [position, rotation-6D] block per named mocap body."""

    def __init__(self, controls):
        self.controls = deepcopy(controls)
        self.actuators = tuple(a["name"] for a in controls["actuators"])
        self.mocaps = tuple(controls["mocap_bodies"])
        for names in (self.actuators, self.mocaps):
            if any(not n for n in names) or len(set(names)) != len(names):
                raise ValueError("Policy controls require unique nonempty names")
        self.dimension = len(self.actuators) + 9 * len(self.mocaps)
        if not self.dimension:
            raise ValueError("Policy needs at least one actuator or mocap body")
        bounds = [a["range"] or [-np.inf, np.inf] for a in controls["actuators"]]
        self.bounds = np.asarray(bounds, dtype=np.float64).reshape(-1, 2)

    @property
    def rotation_indices(self):
        return [len(self.actuators) + 9 * i + j for i in range(len(self.mocaps)) for j in range(3, 9)]

    def encode(self, frame):
        ctrl = np.asarray(frame["ctrl"])
        if ctrl.shape[-1] != len(self.actuators):
            raise ValueError("Wrong actuator count")
        values = [ctrl]
        if self.mocaps:
            pos, quat = np.asarray(frame["mocap_pos"]), np.asarray(frame["mocap_quat"])
            if pos.shape != (*ctrl.shape[:-1], len(self.mocaps), 3) or quat.shape != (*pos.shape[:-1], 4):
                raise ValueError("Mocap shapes disagree with the named control layout")
            values.append(
                np.concatenate((pos, quaternion_to_6d(quat)), axis=-1).reshape(*ctrl.shape[:-1], -1)
            )
        value = np.concatenate(values, axis=-1).astype(np.float32)
        if not np.isfinite(value).all():
            raise ValueError("Commands must be finite")
        return value

    def decode(self, actions):
        value = np.asarray(actions, dtype=np.float64)
        if value.shape[-1] != self.dimension or not np.isfinite(value).all():
            raise ValueError("Invalid encoded actions")
        result = {}
        if self.actuators:
            # Hardware/model limits, not training-data clipping.
            result["ctrl"] = np.clip(value[..., : len(self.actuators)], self.bounds[:, 0], self.bounds[:, 1])
        if self.mocaps:
            poses = value[..., len(self.actuators) :].reshape(*value.shape[:-1], len(self.mocaps), 9)
            result.update(mocap_pos=poses[..., :3], mocap_quat=rotation_6d_to_quaternion(poses[..., 3:]))
        return result

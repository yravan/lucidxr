"""Action encodings, independent of episode rules and rendering."""

import numpy as np
from gymnasium import spaces
from scipy.spatial.transform import Rotation


def actuator_space(model):
    bounds = np.where(
        model.actuator_ctrllimited[:, None], model.actuator_ctrlrange, np.array([-np.inf, np.inf])
    )
    return spaces.Box(bounds[:, 0], bounds[:, 1], dtype=np.float64)


class ActuatorControl:
    """Actions are MuJoCo actuator ctrl values, in model actuator order."""

    def bind(self, model):
        return actuator_space(model)

    def encode(self, model, data):
        return data.ctrl.copy()

    def apply(self, model, data, action):
        data.ctrl[:] = action


class MocapControl:
    """Absolute target poses encoded as position + rotation6d, followed by ctrl.

    relative_to maps child mocap body names to parent mocap body names. A parent
    must itself be world-relative. This supports wrists/fingers without relying
    on their count or order in XML. The mapping changes action encoding only.
    """

    def __init__(self, *, relative_to=None):
        self.relative_to = dict(relative_to or {})

    def _parents(self, model):
        result = {}
        for child, parent in self.relative_to.items():
            if parent in self.relative_to or child == parent:
                raise ValueError("Relative targets require a world-relative parent")
            ids = [int(model.body_mocapid[model.body(name).id]) for name in (child, parent)]
            if min(ids) < 0:
                raise ValueError(f"Both {child!r} and {parent!r} must be mocap bodies")
            result[ids[0]] = ids[1]
        return result

    def bind(self, model):
        self._parents(model)
        ctrl = actuator_space(model)
        low = np.tile([-np.inf] * 3 + [-1.0] * 6, model.nmocap)
        high = np.tile([np.inf] * 3 + [1.0] * 6, model.nmocap)
        return spaces.Box(np.r_[low, ctrl.low], np.r_[high, ctrl.high], dtype=np.float64)

    def encode(self, model, data):
        if not model.nmocap:
            return data.ctrl.copy()
        rotation = Rotation.from_quat(data.mocap_quat, scalar_first=True).as_matrix()
        pos = data.mocap_pos.copy()
        local_rot = rotation.copy()
        for child, parent in self._parents(model).items():
            pos[child] = rotation[parent].T @ (pos[child] - data.mocap_pos[parent])
            local_rot[child] = rotation[parent].T @ rotation[child]
        sixd = local_rot[:, :, :2].transpose(0, 2, 1).reshape(-1, 6)
        return np.r_[np.c_[pos, np.clip(sixd, -1, 1)].ravel(), data.ctrl]

    def apply(self, model, data, action):
        count = model.nmocap
        poses = action[: 9 * count].reshape(count, 9)
        if count:
            x, y = poses[:, 3:6].copy(), poses[:, 6:9].copy()
            nx = np.linalg.norm(x, axis=1, keepdims=True)
            if np.any(nx < 1e-8):
                raise ValueError("rotation6d first column must be nonzero")
            x /= nx
            y -= (x * y).sum(axis=1, keepdims=True) * x
            ny = np.linalg.norm(y, axis=1, keepdims=True)
            if np.any(ny < 1e-8):
                raise ValueError("rotation6d columns must be linearly independent")
            y /= ny
            rotation = np.stack((x, y, np.cross(x, y)), axis=-1)
            pos = poses[:, :3].copy()
            for child, parent in self._parents(model).items():
                pos[child] = poses[parent, :3] + rotation[parent] @ poses[child, :3]
                rotation[child] = rotation[parent] @ rotation[child]
            quat = Rotation.from_matrix(rotation).as_quat(scalar_first=True)
            data.mocap_pos[:] = pos
            data.mocap_quat[:] = quat
        data.ctrl[:] = action[9 * count :]


def site_poses(model, data, names, *, relative_to=None):
    """Measured position + rotation6d, with optional named parent-site frames."""
    parents = dict(relative_to or {})
    if set(parents) - set(names):
        raise ValueError("Relative site mappings must refer to observed sites")
    result = []
    for name in names:
        site = model.site(name).id
        rotation = data.site_xmat[site].reshape(3, 3)
        pos = data.site_xpos[site].copy()
        if name in parents:
            parent = model.site(parents[name]).id
            parent_rotation = data.site_xmat[parent].reshape(3, 3)
            pos = parent_rotation.T @ (pos - data.site_xpos[parent])
            rotation = parent_rotation.T @ rotation
        result.extend((pos, rotation[:, :2].T.ravel()))
    return np.concatenate(result) if result else np.empty(0, dtype=np.float64)

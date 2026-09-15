"""Randomize camera calibration and local pose."""

import mujoco
import numpy as np
from scipy.spatial.transform import Rotation

from .randomization import RandomizationWrapper


class CameraRandomization(RandomizationWrapper):
    """Uniform local position (meters), rotation-vector (radians) and FOV (degrees).

    names=None selects all cameras. FOV randomization is supported for perspective
    fovy cameras; calibrated intrinsic/orthographic cameras require fovy=0.
    """

    def __init__(self, env, *, names=None, position=0.01, rotation=0.087, fovy=5.0):
        self.validate_scales(position=position, rotation=rotation, fovy=fovy)
        model = env.unwrapped.model
        self.ids = np.array(
            [model.camera(name).id for name in names] if names is not None else list(range(model.ncam)),
            dtype=int,
        )
        if fovy and (
            np.any(model.cam_sensorsize[self.ids, 1] > 0)
            or np.any(model.cam_projection[self.ids] != mujoco.mjtProjection.mjPROJ_PERSPECTIVE)
        ):
            raise ValueError("Use fovy=0 for intrinsic or orthographic cameras")
        self.position, self.rotation, self.fovy = position, rotation, fovy
        super().__init__(env, fields={name: self.ids for name in ("cam_pos", "cam_quat", "cam_fovy")})

    def sample(self, rng):
        self.perturb(rng, "cam_pos", self.position)
        if self.fovy:
            self.perturb(rng, "cam_fovy", self.fovy, bounds=(1, 179))
        if len(self.ids) and self.rotation:
            delta = Rotation.from_rotvec(rng.uniform(-self.rotation, self.rotation, (len(self.ids), 3)))
            baseline = Rotation.from_quat(self._defaults["cam_quat"], scalar_first=True)
            self.base.model.cam_quat[self.ids] = (baseline * delta).as_quat(scalar_first=True)

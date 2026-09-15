"""Camera pose and calibration randomization."""

from dataclasses import dataclass, field

import mujoco
import numpy as np
from scipy.spatial.transform import Rotation

from .randomization import RandomizationParams, RandomizationWrapper
from .sampling import PositionRandomization, RotationRandomization, Uniform, check_range, select_ids


@dataclass(frozen=True)
class CameraRandomizationParams(RandomizationParams):
    names: tuple[str, ...] | None = None
    position: PositionRandomization = field(default_factory=PositionRandomization)
    rotation: RotationRandomization = field(default_factory=RotationRandomization)
    fovy: float = 5.0  # symmetric offset in degrees, only for fovy cameras
    focal_scale: Uniform | None = None  # scale calibrated fx/fy together
    principal_offset: float = 0.0  # symmetric fraction of sensor width/height

    def __post_init__(self):
        super().__post_init__()
        RandomizationWrapper.validate_scales(fovy=self.fovy, principal_offset=self.principal_offset)
        check_range(self.focal_scale, low=np.finfo(float).eps, name="focal_scale")
        if not isinstance(self.position, PositionRandomization) or not isinstance(
            self.rotation, RotationRandomization
        ):
            raise TypeError("position/rotation require their sampling dataclasses")


class CameraRandomization(RandomizationWrapper):
    """Sample selected camera-local poses and projection-aware calibration."""

    def __init__(self, env, params: CameraRandomizationParams | None = None):
        self.params = params = self.parameters(params, CameraRandomizationParams)
        model = env.unwrapped.model
        self.ids = select_ids(model, "cam", params.names)
        self._intrinsic = model.cam_sensorsize[self.ids, 1] > 0
        self._perspective = model.cam_projection[self.ids] == mujoco.mjtProjection.mjPROJ_PERSPECTIVE
        if (params.focal_scale or params.principal_offset) and not np.all(
            self._intrinsic & self._perspective
        ):
            raise ValueError("Focal/principal sampling requires intrinsic perspective cameras")
        if params.rotation.max_angle and np.any(
            model.cam_mode[self.ids] >= int(mujoco.mjtCamLight.mjCAMLIGHT_TARGETBODY)
        ):
            raise ValueError("Target-tracking cameras derive orientation; set rotation.max_angle=0")
        super().__init__(
            env,
            params=self.params,
            fields={name: self.ids for name in ("cam_pos", "cam_quat", "cam_fovy", "cam_intrinsic")},
        )

    def sample(self, rng):
        params, model = self.params, self.base.model
        model.cam_pos[self.ids] = params.position.sample(rng, self._defaults["cam_pos"])
        if len(self.ids) and params.rotation.max_angle:
            baseline = Rotation.from_quat(self._defaults["cam_quat"], scalar_first=True)
            model.cam_quat[self.ids] = (baseline * params.rotation.sample(rng, len(self.ids))).as_quat(
                scalar_first=True
            )
        # Orthographic extents and explicit intrinsics are never treated as fovy.
        fovy_ids = np.flatnonzero(self._perspective & ~self._intrinsic)
        if params.fovy and len(fovy_ids):
            model.cam_fovy[self.ids[fovy_ids]] = np.clip(
                self._defaults["cam_fovy"][fovy_ids] + rng.uniform(-params.fovy, params.fovy, len(fovy_ids)),
                1,
                179,
            )
        intrinsic = self._defaults["cam_intrinsic"].copy()
        if params.focal_scale:
            intrinsic[:, :2] *= params.focal_scale.sample(rng, (len(self.ids), 1))
        if params.principal_offset:
            intrinsic[:, 2:] += (
                rng.uniform(-params.principal_offset, params.principal_offset, (len(self.ids), 2))
                * model.cam_sensorsize[self.ids]
            )
        model.cam_intrinsic[self.ids] = intrinsic

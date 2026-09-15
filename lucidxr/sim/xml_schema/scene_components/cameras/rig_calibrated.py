"""Measured stereo camera placement with optional pose overrides."""

from lucidxr.sim.xml_schema.schema import Group
from lucidxr.sim.xml_schema.simple_components.camera import make_camera, xyaxes
from lucidxr.sim.xml_schema.transforms.mujoco import Vector3

FOV = 42.5


class CalibratedCameraRig(Group):
    """Position overrides translate individual cameras while retaining calibration axes."""

    def __init__(
        self, pos=(0, 0, 0), *, positions=None, wrist_pos="-0.1 0.0 0.01", wrist_quat="-0.11 0.7 0.7 -0.11"
    ):
        origin = Vector3(*pos)
        positions = {} if positions is None else positions
        unknown = positions.keys() - {"left", "right"}
        if unknown:
            raise ValueError(f"Unknown calibrated cameras: {sorted(unknown)}")
        self._wrist_pos, self._wrist_quat = wrist_pos, wrist_quat
        cameras = []
        for name, offset in (("left", (0.44, 0.355, 0.325)), ("right", (0.375, -0.355, 0.325))):
            calibrated_position = origin + offset
            anchor = origin + (offset[0], 0, 0.167914592)
            camera = make_camera(
                name,
                pos=positions.get(name, calibrated_position),
                xyaxes=xyaxes(calibrated_position, anchor),
                fovy=FOV,
            )
            setattr(self, f"{name}_camera", camera)
            cameras.append(camera)
        super().__init__(*cameras)

    def get_cameras(self):
        return [self.left_camera, self.right_camera]

    def wrist_camera(self, name="wrist", pos=None, quat=None):
        return make_camera(
            name,
            pos=self._wrist_pos if pos is None else pos,
            quat=self._wrist_quat if quat is None else quat,
            fovy=FOV,
        )


def make_camera_rig(pos=(0, 0, 0), *_, **options) -> CalibratedCameraRig:
    return CalibratedCameraRig(pos, **options)

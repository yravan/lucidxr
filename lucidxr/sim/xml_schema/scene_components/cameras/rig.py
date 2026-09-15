"""One camera rig implementation with explicit, data-only calibration presets."""

from lucidxr.sim.xml_schema.schema import Group
from lucidxr.sim.xml_schema.simple_components.camera import make_camera
from lucidxr.sim.xml_schema.transforms.mujoco import Vector3

from .presets import PRESETS


class CameraRig(Group):
    """Independent cameras positioned relative to a common origin."""

    def __init__(self, origin=(0, 0, 0), *, preset="standard"):
        try:
            calibration = PRESETS[preset]
        except KeyError:
            raise ValueError(f"Unknown camera preset {preset!r}; choose from {tuple(PRESETS)}") from None
        self._cameras = []
        self._wrist_fovy = calibration["wrist_fovy"]
        origin = Vector3(*origin)
        for attribute, spec in calibration["cameras"].items():
            parameters = dict(spec)
            position = Vector3(*map(float, parameters.pop("pos").split())) + origin
            camera = make_camera(pos=position, **parameters)
            setattr(self, attribute, camera)
            self._cameras.append(camera)

        super().__init__(*self._cameras)

    def get_cameras(self):
        return list(self._cameras)

    def wrist_camera(self, name="wrist", pos="-0.1 0 0.0", quat="-0.15 0.7 0.7 -0.15"):
        return make_camera(name, pos=pos, quat=quat, fovy=self._wrist_fovy)


def make_camera_rig(pos=(0, 0, 0), *_, preset="standard") -> CameraRig:
    return CameraRig(pos, preset=preset)

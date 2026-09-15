"""Stereo and wider context cameras using rescaled COLMAP calibration."""

from lucidxr.sim.xml_schema.schema import Group
from lucidxr.sim.xml_schema.simple_components.camera import make_camera
from lucidxr.sim.xml_schema.transforms.mujoco import Vector3

INTRINSICS = {
    "resolution": "640 360",
    "focalpixel": f"{1874.6781 * 640 / 2815:.3f} {1874.6781 * 360 / 1583:.3f}",
    "sensorsize": "0.0098 0.00735",
}


class StereoCameraRig(Group):
    def __init__(self, pos=(0, 0, 0), *, height=0.50, baseline=0.06, lookat_x=0.7, lookat_z=0.0):
        origin = Vector3(*pos)
        target = origin + (lookat_x, 0, lookat_z)
        specifications = (
            ("stereo_left", (-0.3, baseline / 2, height)),
            ("stereo_right", (-0.3, -baseline / 2, height)),
            ("stereo_far_right", (-0.3, -0.6, height + 0.2)),
            ("stereo_far_left", (-0.3, 0.6, height + 0.2)),
        )
        self._cameras = []
        for name, offset in specifications:
            camera = make_camera(name, pos=origin + offset, lookat=target, **INTRINSICS)
            setattr(self, name, camera)
            self._cameras.append(camera)
        super().__init__(*self._cameras)

    def get_cameras(self):
        return list(self._cameras)

    @staticmethod
    def wrist_camera(name="wrist", pos_rel="-0.1 0 0.0", quat_rel="-0.15 0.7 0.7 -0.15"):
        return make_camera(name, pos=pos_rel, quat=quat_rel, **INTRINSICS)


def make_origin_stereo_rig(pos=(0, 0, 0), **options) -> StereoCameraRig:
    return StereoCameraRig(pos, **options)

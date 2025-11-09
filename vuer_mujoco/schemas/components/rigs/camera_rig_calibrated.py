from vuer_mujoco.schemas.robots.camera import make_camera
from vuer_mujoco.schemas.se3 import se3_mujoco as m

CAM_MODULE_W = 0.034

W, H = 640, 360
# FOV = 74.5
FOV = 42.5

print(f"the y-axis of FOV is {FOV} degrees")


class LEFT_CAM_POS:
    # x = 0.466
    # y = 0.46
    # height = 0.274
    x = 0.375
    y = 0.355
    height = 0.325


l = LEFT_CAM_POS()

def make_camera_rig(pos, *_):
    left_pos_r = m.Vector3(l.x + 0.065, l.y, l.height)
    left_anchor_r = m.Vector3(left_pos_r[0], 0, 0.167914592)

    right_pos = m.Vector3(l.x, -l.y, l.height)
    right_anchor = m.Vector3(right_pos[0], 0, 0.167914592)

    class rig:
        left_camera = make_camera(
            "left",
            pos=left_pos_r + pos,
            lookat=left_anchor_r + pos,
            fovy=FOV,
        )
        right_camera = make_camera(
            "right",
            pos=right_pos + pos,
            lookat=right_anchor + pos,
            fovy=FOV,
        )

        def wrist_camera(name="wrist", pos="-0.1 0.0 0.01", quat="-0.11 0.7 0.7 -0.11"):
            return make_camera(
                name,
                pos=pos,
                quat=quat,
                fovy=FOV,
            )

        @classmethod
        def get_cameras(cls):
            return [
                cls.left_camera,
                cls.right_camera,
            ]

    return rig

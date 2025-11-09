import numpy as np

from vuer_mujoco.schemas.robots.camera import make_camera
from vuer_mujoco.schemas.se3 import se3_mujoco as m

"""
Wrist + Stereo Camera Rig (origin-facing)

- The stereo cameras are centered at the origin in (x, y), raised by `height` in z.
- They are separated by ± baseline/2 along y, and point along +x.
- Wrist camera remains defined relative to the end-effector.
"""

# --- Image + Intrinsics setup (from COLMAP, rescaled to target resolution) ---
W, H = 640, 360

# Original COLMAP intrinsics:
train_w, train_h = 2815, 1583
fx_colmap, fy_colmap = 1874.6781, 1874.6781
cx_colmap, cy_colmap = 1407.5, 791.5

# Rescale to target resolution
fx = fx_colmap * (W / train_w)   # ≈ 426.5
fy = fy_colmap * (H / train_h)   # ≈ 426.5
cx = cx_colmap * (W / train_w)   # ≈ 320.0
cy = cy_colmap * (H / train_h)   # ≈ 180.0

intrinsics = dict(
    resolution=f"{W} {H}",
    focalpixel=f"{fx:.3f} {fy:.3f}",
    sensorsize="0.0098 0.00735"
)

def make_origin_stereo_rig(
    pos: m.Vector3 = m.Vector3(0, 0, 0),
    *,
    height: float = 0.50,
    baseline: float = 0.06,  # 60 mm
    lookat_x: float = 0.7,   # point down +x
    lookat_z: float = 0.0,
):
    """
    Create a stereo rig at the origin, looking in +x.
    - Cameras at (0, ± baseline/2, height).
    - Lookat target is (lookat_x, 0, lookat_z).
    - 'pos' translates the whole rig in world coordinates.
    """
    half_b = baseline / 2.0

    stereo_left_pos  = m.Vector3(-0.3, +half_b, height) + pos
    stereo_far_left_pos  = m.Vector3(-0.1, 0.6, height + 0.2) + pos
    stereo_right_pos = m.Vector3(-0.3, -half_b, height) + pos
    stereo_far_right_pos = m.Vector3(-0.1, -0.6, height + 0.2) + pos

    lookat_anchor = m.Vector3(lookat_x, 0.0, lookat_z) + pos

    class rig:
        # Wrist-attached camera
        @staticmethod
        def wrist_camera(
            name: str = "wrist",
            pos_rel: str = "-0.1 0 0.0",
            quat_rel: str = "-0.15 0.7 0.7 -0.15",
        ):
            return make_camera(
                name,
                pos=pos_rel,
                quat=quat_rel,
                **intrinsics,
            )

        # Stereo pair at origin
        stereo_left = make_camera(
            "stereo_left",
            pos=stereo_left_pos,
            lookat=lookat_anchor,
            **intrinsics,
        )
        stereo_far_left = make_camera(
            "stereo_far_left",
            pos=stereo_far_left_pos + m.Vector3(-0.2, 0, 0),
            lookat=lookat_anchor,
            **intrinsics,
        )
        stereo_right = make_camera(
            "stereo_right",
            pos=stereo_right_pos,
            lookat=lookat_anchor,
            **intrinsics,
        )
        stereo_far_right = make_camera(
            "stereo_far_right",
            pos=stereo_far_right_pos + m.Vector3(-0.2, 0, 0),
            lookat=lookat_anchor,
            **intrinsics,
        )

        @classmethod
        def get_cameras(cls):
            return [cls.stereo_left, cls.stereo_right, cls.stereo_far_right, cls.stereo_far_left]

    return rig
"""
Dual-UR5 pick-block experiment (real robot).

No XMLs are required - we only decide camera layout &
per-task reward shaping later.
"""
from vuer_mujoco.tasks import add_env
from vuer_mujoco.tasks.entrypoint import make_real_env, make_offline_env


def register():
    add_env(
        env_id="Dual_ur5_pick_block-v1",
        entrypoint=make_real_env,
        kwargs=dict(
            camera_indices={"cam0/rgb": 0, "cam1/rgb": 2},
            cam_width=640,
            cam_height=480,
            cam_fps=25,
        ),
    )

    add_env(
        env_id="Dual_ur5_pick_block-offline-v1",
        entrypoint=make_offline_env,
        kwargs=dict(
            camera_keys=["cam0/rgb", "cam1/rgb"],
        ),
    )

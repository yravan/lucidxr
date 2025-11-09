"""
Dual-UR5 pick-block experiment (real robot).

No XMLs are required - we only decide camera layout &
per-task reward shaping later.
"""
from vuer_mujoco.tasks import add_env
from vuer_mujoco.tasks.entrypoint import make_real_env, make_offline_env
from vuer_envs_real.robot_envs import SingleUR5Env
from vuer_mujoco.tasks.base.real_robot_task import RealRobotTask



def register():
    add_env(
        env_id="Single_ur5_ball_sorting-v1",
        entrypoint=make_real_env,
        kwargs=dict(
            camera_indices={"wrist/rgb": 2, "right/rgb": 0, "right_r/rgb": 4},
            cam_width=640,
            cam_height=480,
            cam_fps=25,
            robot_cls=SingleUR5Env,
            task_cls=RealRobotTask,
        ),
    )

    add_env(
        env_id="Single_ur5_ball_sorting-offline-v1",
        entrypoint=make_offline_env,
        kwargs=dict(
            camera_keys=["wrist/rgb", "right/rgb", "right_r/rgb"],
        ),
    )

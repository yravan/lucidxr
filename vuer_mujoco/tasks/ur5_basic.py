from pathlib import Path
from typing import Literal

from dm_control.rl import control

from vuer_mujoco.tasks import add_env, ChDir  # , INITIAL_POSITION_PREFIXES
from vuer_mujoco.tasks.base.lucidxr_env import LucidEnv
from vuer_mujoco.tasks.base.lucidxr_task import SimplePhysics
from vuer_mujoco.tasks.base.mocap_task import MocapTask
from vuer_mujoco.wrappers.old_info_wrappers.history_wrapper import HistoryWrapper
from vuer_mujoco.wrappers.old_info_wrappers.render_depth_wrapper import RenderDepthWrapper
from vuer_mujoco.wrappers.render_rgb_wrapper import RenderRGBWrapper

DEFAULT_TIME_LIMIT = 25
PHYSICS_TIMESTEP = 0.005  # in XML
DECIMATION = 4
CONTROL_TIMESTEP = PHYSICS_TIMESTEP * DECIMATION

UR5_SCENE_FILE = "ur5_basic.xml"
UR5_PNP_SCENE_FILE = "ur5_basic.xml"
INIT_DIR = "."


def entrypoint(
    xml_path,
    mode: Literal["heightmap", "vision", "depth", "segmentation", "heightmap_splat"],
    time_limit=DEFAULT_TIME_LIMIT,
    camera_id: int = -1,
    **wrapper_args,
):
    with ChDir(Path(xml_path).parent):
        physics = SimplePhysics.from_xml_path(xml_path)
        task = MocapTask()

        env = control.Environment(
            physics,
            task,
            time_limit=time_limit,
            control_timestep=CONTROL_TIMESTEP,
        )

    env = LucidEnv(env, height=480, width=270, camera_id=-1, skip_start=3)

    if mode == "depth":
        env = RenderDepthWrapper(
            env,
            width=640,
            height=360,
            camera_id=-1 if "camera_id" not in wrapper_args else wrapper_args["camera_id"],
        )
    elif mode == "vision":
        env = RenderRGBWrapper(
            env,
            width=480,
            height=270,
            camera_id=-1 if "camera_id" not in wrapper_args else wrapper_args["camera_id"],
        )

    if "history" in wrapper_args:
        env = HistoryWrapper(env, history_len=4)

    return env


add_env(
    env_id="ur5_basic-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path=UR5_SCENE_FILE,
        mode="vision",
    ),
)
add_env(
    env_id="ur5_basic-depth-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path=UR5_SCENE_FILE,
        mode="depth",
    ),
)
add_env(
    env_id="ur5_basic-pnp-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path=UR5_PNP_SCENE_FILE,
        mode="vision",
        camera_id=["table_pov", "overhead"],
    ),
)
add_env(
    env_id="ur5_basic-pnp-depth-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path=UR5_PNP_SCENE_FILE,
        mode="depth",
        camera_id=["table_pov", "overhead"],
    ),
)
add_env(
    env_id="ur5_basic-pnp-depth-history-v1",
    entrypoint=entrypoint,
    kwargs=dict(
        xml_path=UR5_PNP_SCENE_FILE,
        mode="depth",
        camera_id=["table_pov", "overhead"],
        history=True,
    ),
)
# INITIAL_POSITION_PREFIXES["ur5_basic-pnp-v1"] = INIT_DIR
# INITIAL_POSITION_PREFIXES["ur5_basic-pnp-depth-v1"] = INIT_DIR
# INITIAL_POSITION_PREFIXES["ur5_basic-pnp-depth-history-v1"] = INIT_DIR
# """
# [x] make a simple UR5 environment
# [x] render the depth image
# [] functionality for inputing the camera pose
# """

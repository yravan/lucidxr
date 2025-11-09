from pathlib import Path

import numpy as np

from vuer_mujoco.schemas.objects.mj_sdf import MjSDF
from vuer_mujoco.schemas.objects.vuer_mug import VuerMug
from vuer_mujoco.schemas.components.rigs.camera_rig_calibrated import make_camera_rig
from vuer_mujoco.tasks._floating_robotiq import UR5Robotiq2f85
from vuer_mujoco.tasks.base.lucidxr_task import get_site, init_states
from vuer_mujoco.tasks.base.mocap_task import MocapTask
from vuer_mujoco.vendors.robohive.robohive_object import RobohiveObj
from vuer_mujoco.tasks.mug_tree import Fixed, MugRandom


center = 0
x1, y1 = center - 0.05, -0.025
x2, y2 = center + 0.17, 0.0

def make_schema(**options):
    from vuer_mujoco.schemas.utils.file import Prettify

    table = RobohiveObj(
        otype="furniture",
        asset_key="simpleTable/simpleWoodTable",
        pos=[0, 0, 0],
        quat=[0.7071, 0, 0, 0.7071],
        local_robohive_root="robohive",
    )

    camera_rig = make_camera_rig(pos=[-0.4, 0, 0.77])

    mug = VuerMug(
        pos=[x1, y1, 0.85],
        quat=[0, 0, 0, 1],
        _attributes={
            "name": "mug",
        },
    )

    mug_tree = MjSDF(
        pos=[x2, y2, 1],
        assets="mug_tree",
        mass=0.3,
        _attributes={
            "name": "tree",
            "quat": "0.5 0.5 0.5 0.5",
        },
        additional_children_raw="""\t<site name="tree_goal_1" pos="-.03 0.076 -0.036" size="0.007" rgba="1 1 1 1"/>
                                              \t<site name="tree_goal_2" pos="-.03 0.066 -0.016" size="0.007" rgba="1 1 1 1"/>
                                              \t<site name="tree_goal_3" pos="-.03 0.071 -0.026" size="0.007" rgba="1 1 1 1"/>
                                              \t<site name="tree_goal_4" pos="-.03 0.081 -0.046" size="0.007" rgba="1 1 1 1"/>
                                              \t<site name="tree_goal_5" pos="-.03 0.086 -0.056" size="0.007" rgba="1 1 1 1"/>
                                              \t<site name="tree_goal_6" pos="-.03 0.091 -0.066" size="0.007" rgba="1 1 1 1"/>
                                                """,
        scale="0.17 0.2118 0.17",
    )

    children = [
        *camera_rig.get_cameras(),
        mug_tree,
        mug,
        table,
    ]

    scene = UR5Robotiq2f85(
        *children,
        pos=[-0.4, 0, 0.77],
        **options,
        camera_rig=camera_rig,
    )

    return scene._xml | Prettify()

def register(strict=True,**_):
    from vuer_mujoco.tasks import add_env
    from vuer_mujoco.tasks.entrypoint import make_env

    add_env(
        env_id="MugTreeUr-fixed-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=Fixed,
            camera_names=["left", "right", "wrist"],
            xml_path="mug_tree_ur.mjcf.xml",
            keyframe_file="mug_tree_ur.frame.yaml",
            workdir=Path(__file__).parent,
            mode="multiview",
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTreeUr-mug_rand-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=MugRandom,
            camera_names=["left", "right", "wrist"],
            xml_path="mug_tree_ur.mjcf.xml",
            keyframe_file="mug_tree_ur.frame.yaml",
            workdir=Path(__file__).parent,
            mode="multiview",
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTreeUr-mug_rand-domain_rand-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=MugRandom,
            camera_names=["right", "left", "wrist",],
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="domain_rand",
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTreeUr-mug_rand-domain_rand-eval-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=MugRandom,
            camera_names=["right", "left", "wrist",],
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="domain_rand",
            randomize_camera=False,
            randomize_every_n_steps=0,
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTreeUr-fixed-camera_rand-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=Fixed,
            camera_names=["left", "right", "wrist"],
            xml_path="mug_tree_ur.mjcf.xml",
            keyframe_file="mug_tree_ur.frame.yaml",
            workdir=Path(__file__).parent,
            mode="domain_rand",
            randomize_color=False,
            randomize_lighting=False,
            randomize_camera=True,
            randomize_every_n_steps=50,
            camera_randomization_args=dict(
                camera_names=["left", "right"],
            ),
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTreeUr-fixed-lucid-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=Fixed,
            camera_names=["left", "right", "wrist"],
            xml_renderer=make_schema,
            keyframe_file="mug_tree_ur.frame.yaml",
            workdir=Path(__file__).parent,
            mode="lucid",
            prefix_to_class_ids={"mug": 148, "table": 16, "tree": 41},
            object_keys=["mug", "tree"],
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTreeUr-mug_rand-lucid-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=MugRandom,
            camera_names=["left", "right", "wrist"],
            xml_renderer=make_schema,
            keyframe_file="mug_tree_ur.frame.yaml",
            workdir=Path(__file__).parent,
            mode="lucid",
            prefix_to_class_ids={"mug": 148, "table": 16, "tree": 41},
            object_keys=["mug", "tree"],
        ),
        strict=strict,
    )


if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Save

    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

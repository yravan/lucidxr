import os
from pathlib import Path
from dotvar import auto_load

import numpy as np

from vuer_mujoco.schemas.components.rigs.camera_rig_calibrated import make_camera_rig
from vuer_mujoco.schemas.objects.eval_sdf import EvalSDF
from vuer_mujoco.schemas.objects.mj_sdf import MjSDF
from vuer_mujoco.schemas.objects.vuer_mug import VuerMug
from vuer_mujoco.schemas.components.concrete_slab import ConcreteSlab
from vuer_mujoco.tasks._floating_robotiq import FloatingRobotiq2f85
from vuer_mujoco.tasks.mug_tree import Fixed, MugRandom

center = 0
x1, y1 = center - 0.05, -0.025
x2, y2 = center + 0.17, 0.0
x3, y3 = 0.5, 1

def make_schema(mode="cameraready", robot="panda", show_robot=False, **options):
    from vuer_mujoco.schemas.utils.file import Prettify

    table = ConcreteSlab(
        assets="model",
        pos=[0, 0, 0.76],
        group=4,
        rgba="0.8 0 0 0.0",
        _attributes={
            "name": "table",
        },
    )
    camera_rig = make_camera_rig(pos=[-0.4, 0, 0.77])

    if robot == "panda":
        from vuer_mujoco.schemas.robots.franka_panda import Panda
        from vuer_mujoco.schemas.robots.tomika_gripper import TomikaGripper

        gripper = TomikaGripper(
            name="test_gripper",
            mocap_pos="0.25 0.0 1.10",
            mocap_quat="0 0 1 0",
            wrist_mount=camera_rig.wrist_camera(),
        )
        panda = Panda(end_effector=gripper, name="test_panda", pos=(0, 0, 0.79), quat=(1, 0, 0, 0))
    else:
        raise ValueError(f"Unknown robot: {robot}")

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
    
    eval_scene = EvalSDF(
        pos=[0, 0, 0],
        env_name="cic_kitchen_v3",
        root_asset_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/mug_tree",
        _attributes={
            "name": "eval",
            # "quat": "0.707 0.707 0 0",
        },
        # quat=[0.7071, 0.0, 0.0,0.7071,]
    )
    
    slab = ConcreteSlab(pos=[0, 0, 0.643], rgba="0.8 0.8 0.8 1", roughness="0.2")

    children = [
        *camera_rig.get_cameras(),
        eval_scene,
        # slab,
        # table,
        mug_tree,
        mug,
    ]

    if mode == "demo":
        pass
    elif mode == "cameraready":
        # children += [optical_table]
        pass
    if show_robot:
        children.append(panda)
        children.append(gripper._mocaps)

    scene = FloatingRobotiq2f85(
        *children,
        pos=[-0.1, 0, 0.9],
        **options,
    )

    return scene._xml | Prettify()



def register(strict=True):
    from vuer_mujoco.tasks import add_env
    from vuer_mujoco.tasks.entrypoint import make_env

    add_env(
        env_id="RealMugTreeCicKitchenV3-fixed-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=Fixed,
            camera_names=["wrist", "left", "right"],
            xml_renderer=make_schema,
            keyframe_file="mug_tree.frame.yaml",
            workdir=Path(__file__).parent,
            mode="gsplat",
            dataset_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/mug_tree/cic_kitchen_v3",
            invisible_prefix=["mug", "tree", "gripper"],
            # width=1280,
            # height=720,
        ),
        strict=strict,
    )
    add_env(
        env_id="RealMugTreeCicKitchenV3-mug_rand-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=MugRandom,
            camera_names=["wrist", "left", "right"],
            xml_renderer=make_schema,
            keyframe_file="mug_tree.frame.yaml",
            workdir=Path(__file__).parent,
            mode="gsplat",
            dataset_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/mug_tree/cic_kitchen_v3",
            invisible_prefix=["mug", "tree", "gripper"],
            # width=1280,
            # height=720,
        ),
        strict=strict,
    )

if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Save

    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

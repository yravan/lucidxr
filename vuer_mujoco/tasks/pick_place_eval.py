import os
from pathlib import Path

from vuer_mujoco.schemas.objects.eval_sdf import EvalSDF
from vuer_mujoco.schemas.components.rigs.camera_rig_calibrated import make_camera_rig
from vuer_mujoco.tasks._floating_robotiq import UR5Robotiq2f85
from vuer_mujoco.schemas.schema import Body
from vuer_mujoco.schemas.components.force_plate import ForcePlate
from vuer_mujoco.tasks.pick_place_robot_room import SingleBoxRandom
from vuer_mujoco.vendors.robohive.robohive_object import RobohiveObj

# scene center is 0.41 + 0.2 / 2 = 0.50
x1, y1 = -0.08 + 0.4, 0.08
x2, y2 = 0.28 + 0.4, 0.38
x_bounds = [-0.08 + 0.4, 0.28 + 0.4]
y_bounds = [0.08, 0.38]
x_bounds_smaller = [-0.05 + 0.4, 0.15 + 0.4]
y_bounds_smaller = [0.08, 0.28]


goal_x, goal_y = 0.1 + 0.4, -0.30


def make_schema(**options):
    from vuer_mujoco.schemas.utils.file import Prettify
    from vuer_mujoco.schemas.objects.cylinder import Cylinder

    camera_rig = make_camera_rig(pos=[0, 0, 0.77])
    robohive_table = RobohiveObj(
        otype="furniture",
        asset_key="simpleTable/simpleWoodTable",
        pos=[0.4, 0, 0],
        quat=[0.7071, 0, 0, 0.7071],
        local_robohive_root="robohive",
    )
    box = Body(
        pos=(x1, y1, 0.8),
        attributes=dict(name="box-1"),
        _children_raw="""
        <joint type="free" name="{name}"/>
        <geom name="box-1" type="box" pos="0 0.0 0.0" rgba="0.13 0.55 0.13 1" size="0.02 0.02 0.02" density="1000"/>
        <site name="box-1" pos="0 0.0 0.0" size="0.005"/>
        """,
    )

    goal_area = ForcePlate(
        name="goal-area",
        pos=(goal_x, goal_y, 0.77),
        type="box",
        size="0.215 0.14 0.005",
        rgba="0.6 0.65 0.7 1",  # cooler bluish-gray
    )

    children = [
        *camera_rig.get_cameras(),
        robohive_table,
        box,
        goal_area,
    ]

    scene = UR5Robotiq2f85(
        *children,
        pos=[0, 0, 0.77],
        **options,
        camera_rig=camera_rig,
    )

    return scene._xml | Prettify()

def register(strict=True):
    from vuer_mujoco.tasks import add_env
    from vuer_mujoco.tasks.entrypoint import make_env

    add_env(
        env_id="PickPlaceEval-single_random-gsplat-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer =make_schema,
            task=SingleBoxRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist"],
            keyframe_file="pick_place_robot_room.frame.yaml",
            mode="gsplat",
            dataset_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/pick_place/cic_kitchen_v3",
            invisible_prefix=["box-1", "goal-area", "gripper", "ur5"],
        ),
        strict=strict,
    )


    add_env(
        env_id="PickPlaceEval-single_random-gsplat-v2",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer =make_schema,
            task=SingleBoxRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist"],
            keyframe_file="pick_place_robot_room.frame.yaml",
            mode="gsplat",
            dataset_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/pick_place/cic_lunette_bookshelf_3",
            invisible_prefix=["box-1", "goal-area", "gripper", "ur5"],
        ),
        strict=strict,
    )


if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Save

    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))
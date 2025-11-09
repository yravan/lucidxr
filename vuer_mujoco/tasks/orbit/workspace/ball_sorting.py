import random
from pathlib import Path

from vuer_mujoco.schemas.objects.mj_sdf import MjSDF
from vuer_mujoco.schemas.utils.file import Save
from vuer_mujoco.tasks._camera_rig_stereo import make_stereo_camera_rig
from vuer_mujoco.schemas.components.concrete_slab import ConcreteSlab
from vuer_mujoco.tasks._floating_robotiq import FloatingRobotiq2f85
from vuer_mujoco.schemas.components.force_plate import ForcePlate
from vuer_mujoco.schemas.components.rigs.lighting_rig import make_lighting_rig
from vuer_mujoco.schemas.objects.orbit_table import OpticalTable

x1, y1 = random.uniform(0.1, 0.4), random.uniform(-0.2, 0.2)
x2, y2 = random.uniform(0.1, 0.4), random.uniform(-0.2, 0.2)
x3, y3 = random.uniform(0.1, 0.4), random.uniform(-0.2, 0.2)
x4, y4 = random.uniform(0.1, 0.4), random.uniform(-0.2, 0.2)
x5, y5 = random.uniform(0.1, 0.4), random.uniform(-0.2, 0.2)


def make_schema(robot="panda", **options):
    from vuer_mujoco.schemas.utils.file import Prettify

    if robot == "panda":
        from vuer_mujoco.schemas.robots.franka_panda import Panda
        from vuer_mujoco.schemas.robots.tomika_gripper import TomikaGripper

        gripper = TomikaGripper(name="test_gripper", mocap_pos="0.25 0.0 1.10", mocap_quat="0 0 1 0")
        panda = Panda(end_effector=gripper, name="test_panda", pos=(0, 0, 0.79), quat=(1, 0, 0, 0))
    else:
        raise ValueError(f"Unknown robot: {robot}")

    optical_table = OpticalTable(
        pos=[0, 0, 0.79],
        assets="model",
        _attributes={"name": "table_optical"},
    )
    lighting = make_lighting_rig(optical_table._pos)
    camera_stereo_rig = make_stereo_camera_rig(optical_table)

    from vuer_mujoco.schemas.objects.ball import Ball

    box = MjSDF(pos=[x1, y1, 0.85], assets="ball_sorting_toy", _attributes={"name": "box", "quat": "0.707 0.707 0 0"}, scale=".1 .1 .1")

    ball_1 = Ball(
        size="0.015",
        pos=[x2, y2, 0.85],
        quat=[0, 0, 1, 0],
        rgba="1 0 0 1",
        _attributes={
            "name": "ball-1",
        },
    )
    ball_2 = Ball(
        size="0.02",
        pos=[x3, y3, 0.85],
        quat=[0, 0, 1, 0],
        rgba="0 0 1 1",
        _attributes={
            "name": "ball-2",
        },
    )

    table_slab = ConcreteSlab(
        assets="model",
        pos=[0, 0, 0.78],
        rgba="0.8 0.8 0.8 0",
        _attributes={
            "name": "table",
        },
    )

    work_area = ForcePlate(
        name="start-area",
        pos=(0.3, 0, 0.605),
        quat=(0, 1, 0, 0),
        type="box",
        size="0.15 0.15 0.01",
        rgba="1 0 0 0.1",
    )

    # scene = Mjcf(
    #     camera_stereo_rig.front_camera,
    #     camera_stereo_rig.front_stereo_left,
    #     camera_stereo_rig.front_stereo_right,
    #     camera_stereo_rig.top_camera,
    #     camera_stereo_rig.left_camera,
    #     camera_stereo_rig.left_stereo_left,
    #     camera_stereo_rig.left_stereo_right,
    #     camera_stereo_rig.right_camera,
    #     camera_stereo_rig.right_stereo_left,
    #     camera_stereo_rig.right_stereo_right,
    #     camera_stereo_rig.back_camera,
    #     camera_stereo_rig.back_stereo_left,
    #     camera_stereo_rig.back_stereo_right,
    #     lighting.key,
    #     lighting.fill,
    #     lighting.back,
    #     optical_table,
    #     box,
    #     panda,
    #     gripper._mocaps,
    #     table_slab
    # )

    scene = FloatingRobotiq2f85(
        camera_stereo_rig.front_camera,
        camera_stereo_rig.front_stereo_left,
        camera_stereo_rig.front_stereo_right,
        camera_stereo_rig.top_camera,
        camera_stereo_rig.left_camera,
        camera_stereo_rig.left_stereo_left,
        camera_stereo_rig.left_stereo_right,
        camera_stereo_rig.right_camera,
        camera_stereo_rig.right_stereo_left,
        camera_stereo_rig.right_stereo_right,
        camera_stereo_rig.back_camera,
        camera_stereo_rig.back_stereo_left,
        camera_stereo_rig.back_stereo_right,
        optical_table,
        work_area,
        box,
        ball_1,
        ball_2,
        table_slab,
        pos=[0, 0, 1.0],
        **options,
    )

    return scene._xml | Prettify()


def register():
    from vuer_mujoco.tasks import add_env
    from vuer_mujoco.tasks.entrypoint import make_env

    add_env(
        env_id="IsaacOrbit_ball_sorting-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="isaacorbit_ball_sorting.mjcf.xml",
            workdir=Path(__file__).parent,
            mode="render",
        ),
    )
    add_env(
        env_id="IsaacOrbit_ball_sorting-lucid-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="isaacorbit_ball_sorting.mjcf.xml",
            workdir=Path(__file__).parent,
            mode="lucid",
            prefix_to_class_ids={"mug": 148, "table": 100, "mug-tree": 41},
            object_prefix="mug",
        ),
    )


if __name__ == "__main__":
    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

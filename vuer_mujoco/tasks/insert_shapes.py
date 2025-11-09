import random
import warnings
from pathlib import Path
import numpy as np

from vuer_mujoco.tasks.base.mocap_task import MocapTask
from vuer_mujoco.schemas.objects.sort_shapes import SquareBlock, HexBlock, TriangleBlock, CircleBlock, LeBox
from vuer_mujoco.schemas.components.rigs.camera_rig import make_camera_rig
from vuer_mujoco.schemas.components.concrete_slab import ConcreteSlab
from vuer_mujoco.tasks._floating_robotiq import FloatingRobotiq2f85
from vuer_mujoco.schemas.objects.orbit_table import OpticalTable


def make_schema(mode="cameraready", robot="panda", show_robot=False, **options):
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

    table_slab = ConcreteSlab(
        assets="model",
        pos=[0, 0, 0.777],
        group=4,
        rgba="0.8 0 0 0.0",
        _attributes={
            "name": "table",
        },
    )
    camera_rig = make_camera_rig(table_slab.surface_origin)

    scale = 0.075

    lebox = LeBox(pos=[0.5, 0, 0.85], assets="sort_shape", _attributes={"name": "lebox", "quat": "1 0 0 0"}, scale=1.1 * scale)
    hexblock = HexBlock(pos=[0.25, -0.05, 0.85], assets="sort_shape", _attributes={"name": "block_hex", "quat": "1 0 0 0"}, scale=scale)
    squareblock = SquareBlock(
        pos=[0.25, 0.05, 0.85], assets="sort_shape", _attributes={"name": "block_square", "quat": "1 0 0 0"}, scale=scale
    )
    triangleblock = TriangleBlock(
        pos=[0.35, -0.05, 0.85], assets="sort_shape", _attributes={"name": "block_triangle", "quat": "1 0 0 0"}, scale=scale
    )
    circleblock = CircleBlock(
        pos=[0.35, 0.05, 0.85], assets="sort_shape", _attributes={"name": "block_circle", "quat": "1 0 0 0"}, scale=scale
    )

    # work_area = ForcePlate(
    #     name="start-area",
    #     pos=(0.3, 0, 0.605),
    #     quat=(0, 1, 0, 0),
    #     type="box",
    #     size="0.15 0.15 0.01",
    #     rgba="1 0 0 0.1",
    # )
    children = [
        *camera_rig.get_cameras(),
        # work_area,
        table_slab,
        # objects
        lebox,
        hexblock,
        squareblock,
        triangleblock,
        circleblock,
    ]

    if mode == "demo":
        pass
    elif mode == "cameraready":
        children += [optical_table]

    if show_robot:
        children.append(panda)
        children.append(gripper._mocaps)

    scene = FloatingRobotiq2f85(
        *children,
        pos=[0, 0, 1.0],
        **options,
    )

    return scene._xml | Prettify()


class Insert(MocapTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from vuer_mujoco.tasks.base.lucidxr_task import get_site

        self.hexblock = get_site(self.physics, "block_hex")
        self.squareblock = get_site(self.physics, "block_square")
        self.circleblock = get_site(self.physics, "block_circle")
        self.triangleblock = get_site(self.physics, "block_triangle")

        self.lebox_hex = get_site(self.physics, "lebox-hexblock")
        self.lebox_square = get_site(self.physics, "lebox-squareblock")
        self.lebox_circle = get_site(self.physics, "lebox-circleblock")
        self.lebox_triangle = get_site(self.physics, "lebox-triangleblock")

    def get_reward(self, physics):
        reward = 0.0
        hexblock_pos = physics.data.site_xpos[self.hexblock.id]
        squareblock_pos = physics.data.site_xpos[self.squareblock.id]
        circleblock_pos = physics.data.site_xpos[self.circleblock.id]
        triangleblock_pos = physics.data.site_xpos[self.triangleblock.id]

        hexblock_goal_pos = physics.data.site_xpos[self.lebox_hex.id]
        squareblock_goal_pos = physics.data.site_xpos[self.lebox_square.id]
        circleblock_goal_pos = physics.data.site_xpos[self.lebox_circle.id]
        triangleblock_goal_pos = physics.data.site_xpos[self.lebox_triangle.id]

        # Check if the blocks are close to their respective goal positions
        if (
            np.linalg.norm(hexblock_pos - hexblock_goal_pos) < 0.03
            and np.linalg.norm(squareblock_pos - squareblock_goal_pos) < 0.03
            and np.linalg.norm(circleblock_pos - circleblock_goal_pos) < 0.03
            and np.linalg.norm(triangleblock_pos - triangleblock_goal_pos) < 0.03
        ):
            reward = 1.0
        warnings.warn("Reward is untested for this env, bc we had no working policy")

        return reward


hexblock_qpos_addr = 7
squareblock_qpos_addr = 14
circleblock_qpos_addr = 28
triangleblock_qpos_addr = 21
lebox_qpos_addr = 0


class InsertShapesRand(Insert):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def randomize_state(qpos=None, quat=None, **kwargs):
        new_qpos = qpos.copy()

        x1, y1 = random.uniform(0.45, 0.65), random.uniform(-0.2, 0.2)
        x2, y2 = random.uniform(0.45, 0.65), random.uniform(-0.2, 0.2)
        x3, y3 = random.uniform(0.45, 0.65), random.uniform(-0.2, 0.2)
        x4, y4 = random.uniform(0.45, 0.65), random.uniform(-0.2, 0.2)

        new_pos_hexblock = np.array([x1, y1, qpos[hexblock_qpos_addr + 2]])
        new_pos_squareblock = np.array([x2, y2, qpos[squareblock_qpos_addr + 2]])
        new_pos_circleblock = np.array([x3, y3, qpos[circleblock_qpos_addr + 2]])
        new_pos_triangleblock = np.array([x4, y4, qpos[triangleblock_qpos_addr + 2]])

        new_qpos[hexblock_qpos_addr : hexblock_qpos_addr + 3] = new_pos_hexblock
        new_qpos[squareblock_qpos_addr : squareblock_qpos_addr + 3] = new_pos_squareblock
        new_qpos[circleblock_qpos_addr : circleblock_qpos_addr + 3] = new_pos_circleblock
        new_qpos[triangleblock_qpos_addr : triangleblock_qpos_addr + 3] = new_pos_triangleblock
        return dict(qpos=new_qpos, quat=quat, **kwargs)


class InsertGoalRand(Insert):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def randomize_state(qpos=None, quat=None, **kwargs):
        new_qpos = qpos.copy()
        x5, y5 = random.uniform(0.27, 0.35), random.uniform(-0.1, 0.1)
        new_pos_lebox = np.array([x5, y5, qpos[lebox_qpos_addr + 2]])
        new_qpos[lebox_qpos_addr : lebox_qpos_addr + 3] = new_pos_lebox
        return dict(qpos=new_qpos, quat=quat, **kwargs)


def register():
    from vuer_mujoco.tasks import add_env
    from vuer_mujoco.tasks.entrypoint import make_env

    add_env(
        env_id="InsertShapes-fixed-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=Insert,
            camera_names=["front", "right", "wrist"],
            xml_path="insert_shapes.mjcf.xml",
            workdir=Path(__file__).parent,
        ),
    )
    add_env(
        env_id="InsertShapes-shapes_rand-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=InsertShapesRand,
            camera_names=["front", "right", "wrist", "top"],
            xml_renderer=make_schema,
            keyframe_file="insert_shapes.frame.yaml",
            workdir=Path(__file__).parent,
        ),
    )
    add_env(
        env_id="InsertShapes-box_rand-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=InsertGoalRand,
            camera_names=["front", "right", "wrist", "top"],
            xml_renderer=make_schema,
            keyframe_file="insert_shapes.frame.yaml",
            workdir=Path(__file__).parent,
        ),
    )
    add_env(
        env_id="InsertShapes-lucid-v1",
        entrypoint=make_env,
        kwargs=dict(
            tasks=Insert,
            camera_names=["right", "right_r", "wrist", "front"],
            xml_path="insert_shapes.mjcf.xml",
            workdir=Path(__file__).parent,
            mode="lucid",
            prefix_to_class_ids={},
            object_keys=["block", "lebox"],
        ),
    )


if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Save

    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

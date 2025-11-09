from pathlib import Path

import numpy as np

from vuer_mujoco.schemas.objects.eval_sdf import EvalSDF
from vuer_mujoco.schemas.objects.mj_sdf import MjSDF
from vuer_mujoco.schemas.objects.vuer_mug import VuerMug
from vuer_mujoco.schemas.components.rigs.camera_rig import make_camera_rig
from vuer_mujoco.schemas.components.concrete_slab import ConcreteSlab
from vuer_mujoco.tasks._floating_robotiq import FloatingRobotiq2f85, UR5Robotiq2f85
from vuer_mujoco.tasks.base.lucidxr_task import get_site, init_states
from vuer_mujoco.tasks.base.mocap_task import MocapTask
from vuer_mujoco.schemas.objects.orbit_table import OpticalTable
from vuer_mujoco.vendors.robohive.robohive_object import RobohiveObj


# x1, y1 = random.uniform(0.15, 0.2), random.uniform(-0.1, 0.1)
# x2, y2 = random.uniform(0.2, 0.4), random.uniform(-0.2, 0.2)

# scene center is 0.41 + 0.2 / 2 = 0.50
center = 0
x1, y1 = center - 0.05, -0.025
x2, y2 = center + 0.17, 0.0


def make_schema(mode="cameraready", robot="panda", show_robot=False, **options):
    from vuer_mujoco.schemas.utils.file import Prettify

    optical_table = OpticalTable(
        pos=[0, 0, 0.79],
        assets="model",
        _attributes={"name": "table_optical"},
    )
    # camera_rig = make_camera_rig(optical_table._pos)

    table = RobohiveObj(
        otype="furniture",
        asset_key="simpleTable/simpleWoodTable",
        pos=[0, 0, 0],
        quat=[0.7071, 0, 0, 0.7071]
    )

    # table_slab = ConcreteSlab(
    #     assets="model",
    #     pos=[0, 0, 0.777],
    #     group=4,
    #     rgba="0.8 0 0 0.0",
    #     _attributes={
    #         "name": "table",
    #     },
    # )
    camera_rig = make_camera_rig(pos=[-0.7, 0, 0.777])

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

    # work_area = ForcePlate(
    #     name="start-area",
    #     pos=(0.3, 0, 0.777 + 0.025 - 0.01),
    #     quat=(0, 1, 0, 0),
    #     type="box",
    #     size="0.15 0.15 0.01",
    #     rgba="1 0 0 0.1",
    # )
    
    eval_scene = EvalSDF(
        pos=[0, 0, -0.08],
        env_name="cic_lunette_bookshelf_3",
        _attributes={
            "name": "eval",
            # "quat": "0.707 0.707 0 0",
        },
    )
    
    mug_tree = MjSDF(
        pos=[x2, y2, 0.95],
        assets="mug_tree",
        mass=0.3,
        _attributes={
            "name": "tree",
            "quat": "0.707 0.707 0 0",
        },
        additional_children_raw="""\t<site name="tree_goal" pos="-.03 0.055 0.025" size="0.01" rgba="1 1 1 0"/>""",
        scale="0.17 0.17 0.17",
    )

    children = [
        *camera_rig.get_cameras(),
        # now add the setup
        eval_scene,
        # table_slab,
        # work_area,
        mug_tree,
        mug,
    ]

    if mode == "demo":
        pass
    elif mode == "cameraready":
        # children += [table]
        pass

    if show_robot:
        children.append(panda)
        children.append(gripper._mocaps)

    scene = UR5Robotiq2f85(
        *children,
        pos=[-0.4, 0, 0.77],
        **options,
    )

    return scene._xml | Prettify()

    return None


class Fixed(MocapTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mug_site = None
        self.tree_site = None
        self.gripper_site = None
        self.set_sites()

    def set_sites(self):
        self.mug_site = get_site(self.physics, "mug")
        self.tree_site = get_site(self.physics, "tree")
        self.gripper_site = get_site(self.physics, "gripper-pinch")

    def get_reward(self, physics):
        reward = 0.0
        mug_pos = physics.data.site_xpos[self.mug_site.id]
        tree_pos = physics.data.site_xpos[self.tree_site.id]
        gripper_pos = physics.data.site_xpos[self.gripper_site.id]
        if np.linalg.norm(mug_pos - tree_pos) < 0.025 and np.linalg.norm(gripper_pos - tree_pos) > 0.2:
            reward = 1.0
        return reward


class MugRandom(Fixed):
    mug_qpos_addr = 7
    d = 0.08
    xy_limits = [center - 0.3, center + 0.1], [-0.1, 0.1]
    xy_reject = [x2 - 0.11, x2 + 0.11], [y2 - 0.11, y2 + 0.11]

    xy_poses = init_states(xy_limits, d, xy_reject)
    print("the length is", len(xy_poses))
    pose_buffer = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def random_state(
        cls,
        qpos=None,
        quat=None,
        addr=mug_qpos_addr,
        index=None,
        mocap_pos=None,
        **kwargs,
    ):
        import random
        from copy import copy

        if index is None:
            if not cls.pose_buffer:
                cls.pose_buffer = copy(cls.xy_poses)
                random.shuffle(cls.pose_buffer)

            x, y = cls.pose_buffer.pop(0)
        else:
            x, y = cls.xy_poses[index]

        new_qpos = qpos.copy()

        new_qpos[addr : addr + 2] = x, y
        # Add Gaussian noise to mocap position
        if mocap_pos is not None:
            mocap_pos = mocap_pos.copy()
            noise = np.random.normal(loc=0.0, scale=0.05, size=mocap_pos.shape)  # std=5mm
            mocap_pos += noise

        return dict(qpos=new_qpos, quat=quat, mocap_pos=mocap_pos, **kwargs)


def register():
    from vuer_mujoco.tasks import add_env
    from vuer_mujoco.tasks.entrypoint import make_env

    add_env(
        env_id="RealMugTreeUrCicLunetteBookshelfV3-fixed-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=Fixed,
            camera_names=["left", "right", "wrist"],
            xml_path="real_mug_tree_ur_cic_lunette_bookshelf_v3.mjcf.xml",
            keyframe_file="mug_tree_ur.frame.yaml",
            workdir=Path(__file__).parent,
            mode="gsplat",
            dataset_path=f"{Path(__file__).parent}/assets/eval_envs/cic_lunette_bookshelf_3",
            invisible_prefix=["mug", "tree", "gripper", "ur5"],
        ),
    )

if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Save

    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

import os
from pathlib import Path

import numpy as np

from vuer_mujoco.schemas.components.rigs.camera_rig_calibrated import make_camera_rig
from vuer_mujoco.schemas.objects.mj_sdf import MjSDF
from vuer_mujoco.schemas.objects.vuer_mug import VuerMug
# from vuer_mujoco.schemas.components.rigs.camera_rig_calibrated import make_camera_rig
from vuer_mujoco.schemas.components.rigs.camera_rig_stereo import make_origin_stereo_rig
from vuer_mujoco.schemas.components.concrete_slab import ConcreteSlab
from vuer_mujoco.tasks._floating_robotiq import FloatingRobotiq2f85, UR5Robotiq2f85
from vuer_mujoco.tasks.base.lucidxr_task import get_site, init_states
from vuer_mujoco.tasks.base.mocap_task import MocapTask
from vuer_mujoco.schemas.objects.orbit_table import OpticalTable
from vuer_mujoco.vendors.robohive.robohive_object import RobohiveObj

center = 0
x1, y1 = center - 0.05, -0.025
x2, y2 = center + 0.17, 0.0

def make_schema(mode="cameraready", robot="panda", show_robot=False, **options):
    from vuer_mujoco.schemas.utils.file import Prettify


    optical_table = OpticalTable(
        pos=[-0.4, 0, 0.77],
        assets="model",
        _attributes={"name": "table_optical"},
    )

    table = RobohiveObj(otype="furniture", asset_key="simpleTable/simpleWoodTable", pos=[0, 0, 0], quat=[0.7071, 0, 0, 0.7071])
    table = ConcreteSlab(
        assets="model",
        pos=[0, 0, 0.76],
        group=4,
        rgba="0.8 0 0 0.0",
        _attributes={
            "name": "table",
        },
    )
    stereo_cameras = make_origin_stereo_rig(pos=[-0.4, 0, 0.77])
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


    children = [
        *camera_rig.get_cameras(),
        *stereo_cameras.get_cameras(),
        mug_tree,
        mug,
        table,
    ]

    if mode == "demo":
        pass
    elif mode == "cameraready":
        children += [optical_table]

    if show_robot:
        scene = UR5Robotiq2f85(
            *children,
            pos=[-0.4, 0, 0.77],
            **options,
            camera_rig=camera_rig,
        )
    else:
        scene = FloatingRobotiq2f85(
            *children,
            pos=[-0.1, 0, 0.9],
            **options,
            camera_rig=camera_rig,
        )

    return scene._xml | Prettify()



class Fixed(MocapTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mug_site = None
        self.tree_site = None
        self.gripper_site = None
        self.set_sites()

    def set_sites(self):
        self.mug_site_1 = get_site(self.physics, "mug_handle_1")
        self.mug_site_2 = get_site(self.physics, "mug_handle_2")
        self.mug_site_3 = get_site(self.physics, "mug_handle_3")
        self.tree_site_1 = get_site(self.physics, "tree_goal_1")
        self.tree_site_2 = get_site(self.physics, "tree_goal_2")
        self.tree_site_3 = get_site(self.physics, "tree_goal_3")
        self.tree_site_4 = get_site(self.physics, "tree_goal_4")
        self.tree_site_5 = get_site(self.physics, "tree_goal_5")
        self.tree_site_6 = get_site(self.physics, "tree_goal_6")

        self.gripper_site = get_site(self.physics, "gripper-pinch")

    def get_reward(self, physics):
        reward = 0.0
        mug_pos_1 = physics.data.site_xpos[self.mug_site_1.id]
        mug_pos_2 = physics.data.site_xpos[self.mug_site_2.id]
        mug_pos_3 = physics.data.site_xpos[self.mug_site_3.id]
        tree_pos_1 = physics.data.site_xpos[self.tree_site_1.id]
        tree_pos_2 = physics.data.site_xpos[self.tree_site_2.id]
        tree_pos_3 = physics.data.site_xpos[self.tree_site_3.id]
        tree_pos_4 = physics.data.site_xpos[self.tree_site_4.id]
        tree_pos_5 = physics.data.site_xpos[self.tree_site_5.id]
        tree_pos_6 = physics.data.site_xpos[self.tree_site_6.id]

        gripper_pos = physics.data.site_xpos[self.gripper_site.id]
        if  ((np.linalg.norm(mug_pos_1 - tree_pos_1) < 0.013
                or np.linalg.norm(mug_pos_2 - tree_pos_1) < 0.02
                or np.linalg.norm(mug_pos_3 - tree_pos_1) < 0.013 ) and np.linalg.norm(gripper_pos - tree_pos_1) > 0.1)\
            or ((np.linalg.norm(mug_pos_1 - tree_pos_2) < 0.013
                or np.linalg.norm(mug_pos_2 - tree_pos_2) < 0.02
                or np.linalg.norm(mug_pos_3 - tree_pos_2) < 0.013 ) and np.linalg.norm(gripper_pos - tree_pos_2) > 0.1)\
            or ((np.linalg.norm(mug_pos_1 - tree_pos_3) < 0.013
                or np.linalg.norm(mug_pos_2 - tree_pos_3) < 0.02
                or np.linalg.norm(mug_pos_3 - tree_pos_3) < 0.013 ) and np.linalg.norm(gripper_pos - tree_pos_3) > 0.1)\
            or ((np.linalg.norm(mug_pos_1 - tree_pos_4) < 0.013
                or np.linalg.norm(mug_pos_2 - tree_pos_4) < 0.02
                or np.linalg.norm(mug_pos_3 - tree_pos_4) < 0.013 ) and np.linalg.norm(gripper_pos - tree_pos_4) > 0.1)\
            or ((np.linalg.norm(mug_pos_1 - tree_pos_5) < 0.013
                or np.linalg.norm(mug_pos_2 - tree_pos_5) < 0.02
                or np.linalg.norm(mug_pos_3 - tree_pos_5) < 0.013 ) and np.linalg.norm(gripper_pos - tree_pos_5) > 0.1)\
            or ((np.linalg.norm(mug_pos_1 - tree_pos_6) < 0.013
                or np.linalg.norm(mug_pos_2 - tree_pos_6) < 0.02
                or np.linalg.norm(mug_pos_3 - tree_pos_6) < 0.013 ) and np.linalg.norm(gripper_pos - tree_pos_6) > 0.1):
            reward = 1.0
        return reward


class MugRandom(Fixed):
    mug_qpos_addr = 7
    d = 0.08
    xy_limits = [center - 0.2, center], [-0.1, 0.1]
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
            # if not cls.pose_buffer:
            #     cls.pose_buffer = copy(cls.xy_poses)
            #     random.shuffle(cls.pose_buffer)
            #
            # x, y = cls.pose_buffer.pop(0)
            x,y = random.choice(cls.xy_poses)
        else:
            x, y = cls.xy_poses[index]

        new_qpos = qpos.copy()

        new_qpos[addr : addr + 2] = x, y
        # Add Gaussian noise to mocap position
        if mocap_pos is not None:
            mocap_pos = mocap_pos.copy()
            noise = np.random.normal(loc=0.0, scale=0.005, size=mocap_pos.shape)  # std=5mm
            mocap_pos += noise

        return dict(qpos=new_qpos, quat=quat, mocap_pos=mocap_pos, **kwargs)


def register(strict=True):
    from vuer_mujoco.tasks import add_env
    from vuer_mujoco.tasks.entrypoint import make_env

    add_env(
        env_id="MugTree-fixed-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=Fixed,
            camera_names=["right", "wrist", "left", "stereo_far_left", "stereo_far_right"],
            xml_renderer=make_schema,
            keyframe_file="mug_tree.frame.yaml",
            workdir=Path(__file__).parent,
            mode="multiview",
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTree-mug_rand-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=MugRandom,
            # the top is used for debug, will need to figure out how to render this in the future.
            camera_names=["right", "wrist", "left", "stereo_far_left", "stereo_far_right"],
            xml_renderer=make_schema,
            keyframe_file="mug_tree.frame.yaml",
            workdir=Path(__file__).parent,
            mode="multiview",
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTree-ur-mug_rand-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=MugRandom,
            # the top is used for debug, will need to figure out how to render this in the future.
            camera_names=["right", "wrist", "left", "stereo_far_left", "stereo_far_right"],
            xml_renderer=make_schema,
            keyframe_file=None,
            workdir=Path(__file__).parent,
            mode="multiview",
            show_robot=True,
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTree-fixed-domain_rand-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=Fixed,
            camera_names=["right", "left", "wrist", "stereo_far_left", "stereo_far_right", ],
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="domain_rand",
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTree-mug_rand-domain_rand-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=MugRandom,
            camera_names=["right", "left", "wrist", "stereo_far_left", "stereo_far_right",],
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="domain_rand",
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTree-mug_rand-domain_rand-eval-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=MugRandom,
            camera_names=[
                "right",
                "left",
                "wrist",
            ],
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="domain_rand",
            randomize_every_n_steps=0,
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTree-fixed-gsplat-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=Fixed,
            camera_names=["right", "left", "wrist", "stereo_far_left", "stereo_far_right", ],
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="gsplat",
            dataset_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/mug_tree/cic_kitchen_v3",
            invisible_prefix=["mug", "tree", "gripper"],
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTree-mug_rand-gsplat-cic_kitchen_4th_night",
        entrypoint=make_env,
        kwargs=dict(
            task=MugRandom,
            camera_names=["right", "left", "wrist", "stereo_far_left", "stereo_far_right",],
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="gsplat",
            gsplat_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_kitchen_4th_night",
            transform_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/mug_tree/cic_kitchen_4th_night",
            invisible_prefix=["mug", "tree", "gripper"],
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTree-ur-mug_rand-gsplat-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=MugRandom,
            camera_names=["right", "left", "wrist", "stereo_far_left", "stereo_far_right",],
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="gsplat",
            dataset_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/mug_tree/cic_kitchen_v3",
            invisible_prefix=["mug", "tree", "gripper"],
            show_robot=True,
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTree-fixed-gsplat-v2",
        entrypoint=make_env,
        kwargs=dict(
            task=Fixed,
            camera_names=["right", "left", "wrist", "stereo_far_left", "stereo_far_right", ],
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="gsplat",
            gsplat_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_11th_kitchen",
            transform_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/mug_tree/cic_11th_kitchen",
            invisible_prefix=["mug", "tree", "gripper"],
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTree-mug_rand-gsplat-cic_11th_kitchen",
        entrypoint=make_env,
        kwargs=dict(
            task=MugRandom,
            camera_names=["stereo_far_right", "stereo_far_left", "wrist",],
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="gsplat",
            gsplat_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_11th_kitchen",
            transform_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/mug_tree/cic_11th_kitchen",
            invisible_prefix=["mug", "tree", "gripper"],
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTree-mug_rand-gsplat-cic_kitchen_4th_day",
        entrypoint=make_env,
        kwargs=dict(
            task=MugRandom,
            camera_names=["stereo_far_left", "stereo_far_right", "wrist", "left", "right"],
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="gsplat",
            gsplat_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_kitchen_4th_day",
            transform_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/mug_tree/cic_kitchen_4th_day",
            invisible_prefix=["mug", "tree", "gripper"],
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTree-mug_rand-gsplat-mit_medical_wood_chair",
        entrypoint=make_env,
        kwargs=dict(
            task=MugRandom,
            camera_names=["stereo_far_left", "stereo_far_right", "wrist", "left", "right"],
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="gsplat",
            gsplat_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/mit_medical_wood_chair",
            transform_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/mug_tree/mit_medical_wood_chair",
            invisible_prefix=["mug", "tree", "gripper"],
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTree-mug_rand-gsplat-cic_11th_kitchen_back",
        entrypoint=make_env,
        kwargs=dict(
            task=MugRandom,
            camera_names=["stereo_far_left", "stereo_far_right", "wrist", "left", "right"],
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="gsplat",
            gsplat_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_11th_kitchen_back",
            transform_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/mug_tree/cic_11th_kitchen_back",
            invisible_prefix=["mug", "tree", "gripper"],
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTree-mug_rand-gsplat-cic_4th_nook",
        entrypoint=make_env,
        kwargs=dict(
            task=MugRandom,
            camera_names=["stereo_far_left", "stereo_far_right", "wrist", "left", "right"],
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="gsplat",
            gsplat_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_4th_nook",
            transform_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/mug_tree/cic_4th_nook",
            invisible_prefix=["mug", "tree", "gripper"],
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTree-mug_rand-gsplat-google_building_table",
        entrypoint=make_env,
        kwargs=dict(
            task=MugRandom,
            camera_names=["stereo_far_left", "stereo_far_right", "wrist", "left", "right"],
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="gsplat",
            gsplat_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/google_building_table",
            transform_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/mug_tree/google_building_table",
            invisible_prefix=["mug", "tree", "gripper"],
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTree-mug_rand-gsplat-cic_12th_coffee_table",
        entrypoint=make_env,
        kwargs=dict(
            task=MugRandom,
            camera_names=["stereo_far_left", "stereo_far_right", "wrist", "left", "right"],
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="gsplat",
            gsplat_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_12th_coffee_table",
            transform_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/mug_tree/cic_12th_coffee_table",
            invisible_prefix=["mug", "tree", "gripper"],
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTree-mug_rand-gsplat-cic_bench",
        entrypoint=make_env,
        kwargs=dict(
            task=MugRandom,
            camera_names=["stereo_far_left", "stereo_far_right", "wrist", "left", "right"],
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="gsplat",
            gsplat_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_bench",
            transform_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/mug_tree/cic_bench",
            invisible_prefix=["mug", "tree", "gripper"],
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTree-mug_rand-gsplat-cic_11th_stationary",

        entrypoint=make_env,
        kwargs=dict(
            task=MugRandom,
            camera_names=["stereo_far_left", "stereo_far_right", "wrist", "left", "right"],
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="gsplat",
            gsplat_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_11th_stationary",
            transform_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/mug_tree/cic_11th_stationary",
            invisible_prefix=["mug", "tree", "gripper"],
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTree-ur-mug_rand-gsplat-v2",
        entrypoint=make_env,
        kwargs=dict(
            task=MugRandom,
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="gsplat",
            gsplat_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_11th_kitchen",
            camera_names=["right", "left", "wrist", "stereo_far_left", "stereo_far_right",],
            transform_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/mug_tree/cic_11th_kitchen",
            invisible_prefix=["mug", "tree", "gripper"],
            show_robot=True,
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTree-fixed-lucid-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=Fixed,
            camera_names=["right", "left", "wrist", "stereo_far_left", "stereo_far_right"],
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="lucid",
            prefix_to_class_ids={"mug": 148, "table": 16, "tree": 41},
            object_keys=["mug", "tree"],
        ),
        strict=strict,
    )
    add_env(
        env_id="MugTree-mug_rand-lucid-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=MugRandom,
            camera_names=["left", "right", "wrist"],
            xml_renderer=make_schema,
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

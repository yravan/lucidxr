import os
import random
from pathlib import Path

import numpy as np

from vuer_mujoco.schemas.components.rigs.camera_rig_stereo import make_origin_stereo_rig
from vuer_mujoco.schemas.objects.mj_sdf import MjSDF
from vuer_mujoco.schemas.components.rigs.camera_rig_calibrated import make_camera_rig
from vuer_mujoco.tasks._floating_robotiq import UR5Robotiq2f85
from vuer_mujoco.tasks.base.lucidxr_task import get_site, get_geom_id
from vuer_mujoco.tasks.base.mocap_task import MocapTask
from vuer_mujoco.schemas.objects.mj_obj import MjObj
from vuer_mujoco.vendors.robohive.robohive_object import RobohiveObj
from vuer_mujoco.schemas.schema import Body
from vuer_mujoco.schemas.components.force_plate import ForcePlate
from vuer_mujoco.wrappers.domain_randomization_wrapper import DEFAULT_COLOR_ARGS

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

    robohive_table = RobohiveObj(
        otype="furniture",
        asset_key="simpleTable/simpleWoodTable",
        pos=[0.4, 0, 0],
        quat=[0.7071, 0, 0, 0.7071],
        local_robohive_root="robohive",
    )
    robot_room = MjObj(
        geom_quat="0 0 0.7071 0.7071",
        geom_pos="-1.2 0.8 1.5",
        assets="45_robot_room",
        free=False,
        collision=False,
    )

    camera_rig = make_camera_rig(pos=[0, 0, 0.77])
    stereo_cameras = make_origin_stereo_rig(pos=[0, 0, 0.77])

    box = Body(
        pos=(x1, y1, 0.8),
        attributes=dict(name="box-1"),
        _children_raw="""
        <joint type="free" name="{name}"/>
        <geom name="box-1" type="box" pos="0 0.0 0.0"  rgba="0 1 0 1" size="0.02 0.02 0.02" density="1000"/>
        <site name="box-1" pos="0 0.0 0.0" size="0.005"/>
        """,
    )

    goal_area = ForcePlate(
        name="goal-area",
        pos=(goal_x, goal_y, 0.77),
        # quat=(0, 1, 0, 0),
        type="box",
        size="0.215 0.14 0.005",
        rgba="1. 1. 1. 1.",
    )

    children = [
        *camera_rig.get_cameras(),
        *stereo_cameras.get_cameras(),
        robohive_table,
        # robot_room,
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


class Fixed(MocapTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gripper_site = get_site(self.physics, "gripper-pinch")
        self.box = get_site(self.physics, "box-1")

    def get_reward(self, physics):
        box_pos = physics.data.site_xpos[self.box.id]
        gripper_pos = physics.data.site_xpos[self.gripper_site.id]

        # Goal area is centered at goal_x, goal_y and has size 0.215 x 0.14
        goal_center_x = goal_x
        goal_center_y = goal_y
        goal_half_width = 0.215
        goal_half_height = 0.14

        # Bounds of goal area
        goal_x_min = goal_center_x - goal_half_width
        goal_x_max = goal_center_x + goal_half_width
        goal_y_min = goal_center_y - goal_half_height
        goal_y_max = goal_center_y + goal_half_height

        # Check if box is inside goal area
        inside_x = goal_x_min <= box_pos[0] <= goal_x_max
        inside_y = goal_y_min <= box_pos[1] <= goal_y_max

        # print(inside_y, inside_x, gripper_pos[2] - box_pos[2])

        return float(inside_x and inside_y and gripper_pos[2] > 0.05 + box_pos[2])  # Ensure gripper is above the table


class SingleBoxRandom(Fixed):
    box_qpos_addr = 0
    ball_qpos_addrs = [0]
    rand_range_x = x_bounds_smaller
    rand_range_y = y_bounds_smaller

    @classmethod
    def random_state(
        cls,
        qpos=None,
        quat=None,
        addr=box_qpos_addr,
        index=None,
        mocap_pos=None,
        **kwargs,
    ):
        """Return a new randomized state for a single ball.

        The ball starts at the reference location (``x4``, ``y4``, 0.8) and we
        add a small uniform offset (\pm2 cm) on *x* and *y* every reset.  The
        *z*-coordinate remains unchanged so the ball still sits on the table.
        """

        new_qpos = qpos.copy()

        new_x = np.random.uniform(cls.rand_range_x[0], cls.rand_range_x[1])
        new_y = np.random.uniform(cls.rand_range_y[0], cls.rand_range_y[1])
        new_pos = [new_x, new_y, 0.8]

        # Write the new position back to the qpos vector.
        ball_addr = cls.ball_qpos_addrs[0]
        new_qpos[ball_addr] = new_pos[0]  # x
        new_qpos[ball_addr + 1] = new_pos[1]  # y
        new_qpos[ball_addr + 2] = new_pos[2]  # z (unchanged)

        if mocap_pos is not None:
            mocap_pos = mocap_pos.copy()
            mocap_pos += np.random.normal(0.0, 0.005, mocap_pos.shape)

        return dict(qpos=new_qpos, quat=quat, mocap_pos=mocap_pos, **kwargs)


DEFAULT_COLOR_ARGS["randomize_local_geom_prefixes"] = ["box", "goal-area"]
DEFAULT_COLOR_ARGS["local_rgb_interpolation"] = 0.3
def register(strict=True):
    from vuer_mujoco.tasks import add_env
    from vuer_mujoco.tasks.entrypoint import make_env

    add_env(
        env_id="PickPlaceRobotRoom-fixed-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist","stereo_far_left","stereo_far_right"],
            keyframe_file="pick_place_robot_room.frame.yaml",
            task=Fixed,
        ),
        strict=strict,
    )

    add_env(
        env_id="PickPlaceRobotRoom-single_random-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer=make_schema,
            task=SingleBoxRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist","stereo_far_left","stereo_far_right"],
            keyframe_file="pick_place_robot_room.frame.yaml",
        ),
        strict=strict,
    )
    add_env(
        env_id="PickPlaceRobotRoom-single_random-depth-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer=make_schema,
            task=SingleBoxRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist","stereo_far_left","stereo_far_right"],
            keyframe_file="pick_place_robot_room.frame.yaml",
            mode="depth",
        ),
        strict=strict,
    )

    add_env(
        env_id="PickPlaceRobotRoom-single_random-lucid-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer=make_schema,
            task=SingleBoxRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist","stereo_far_left","stereo_far_right"],
            keyframe_file="pick_place_robot_room.frame.yaml",
            mode="lucid",
            object_keys=["box", "goal-area"],
        ),
        strict=strict,
    )

    add_env(
        env_id="PickPlaceRobotRoom-single_random-domain_rand-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer=make_schema,
            task=SingleBoxRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist","stereo_far_left","stereo_far_right"],
            keyframe_file="pick_place_robot_room.frame.yaml",
            mode="domain_rand",
            color_randomization_args=DEFAULT_COLOR_ARGS,
        ),
        strict=strict,
    )

    add_env(
        env_id="PickPlaceRobotRoom-single_random-gsplat-cic_4th_nook",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer=make_schema,
            task=SingleBoxRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist","stereo_far_left","stereo_far_right"],
            keyframe_file="pick_place_robot_room.frame.yaml",
            mode="gsplat",
            gsplat_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_4th_nook",
            transform_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/pick_place_robot_room/cic_4th_nook",
            invisible_prefix=["box", "goal-area", "gripper", "ur5"],
        ),
        strict=strict,
    )


    add_env(
        env_id="PickPlaceRobotRoom-single_random-gsplat-cic_11th_kitchen",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer=make_schema,
            task=SingleBoxRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist","stereo_far_left","stereo_far_right"],
            keyframe_file="pick_place_robot_room.frame.yaml",
            mode="gsplat",
            gsplat_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_11th_kitchen",
            transform_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/pick_place_robot_room/cic_11th_kitchen",
            invisible_prefix=["box", "goal-area", "gripper", "ur5"],
        ),
        strict=strict,
    )
    add_env(
        env_id="PickPlaceRobotRoom-single_random-gsplat-cic_11th_kitchen_back",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer=make_schema,
            task=SingleBoxRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist","stereo_far_left","stereo_far_right"],
            keyframe_file="pick_place_robot_room.frame.yaml",
            mode="gsplat",
            gsplat_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_11th_kitchen_back",
            transform_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/pick_place_robot_room/cic_11th_kitchen_back",
            invisible_prefix=["box", "goal-area", "gripper", "ur5"],
        ),
        strict=strict,
    )
    add_env(
        env_id="PickPlaceRobotRoom-single_random-gsplat-cic_11th_stationary",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer=make_schema,
            task=SingleBoxRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist","stereo_far_left","stereo_far_right"],
            keyframe_file="pick_place_robot_room.frame.yaml",
            mode="gsplat",
            gsplat_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_11th_stationary",
            transform_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/pick_place_robot_room/cic_11th_stationary",
            invisible_prefix=["box", "goal-area", "gripper", "ur5"],
        ),
        strict=strict,
    )
    add_env(
        env_id="PickPlaceRobotRoom-single_random-gsplat-cic_12th_coffee_table",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer=make_schema,
            task=SingleBoxRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist","stereo_far_left","stereo_far_right"],
            keyframe_file="pick_place_robot_room.frame.yaml",
            mode="gsplat",
            gsplat_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_12th_coffee_table",
            transform_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/pick_place_robot_room/cic_12th_coffee_table",
            invisible_prefix=["box", "goal-area", "gripper", "ur5"],
        ),
        strict=strict,
    )
    add_env(
        env_id="PickPlaceRobotRoom-single_random-gsplat-cic_bench",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer=make_schema,
            task=SingleBoxRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist","stereo_far_left","stereo_far_right"],
            keyframe_file="pick_place_robot_room.frame.yaml",
            mode="gsplat",
            gsplat_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_bench",
            transform_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/pick_place_robot_room/cic_bench",
            invisible_prefix=["box", "goal-area", "gripper", "ur5"],
        ),
        strict=strict,
    )
    add_env(
        env_id="PickPlaceRobotRoom-single_random-gsplat-cic_kitchen_4th_day",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer=make_schema,
            task=SingleBoxRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist","stereo_far_left","stereo_far_right"],
            keyframe_file="pick_place_robot_room.frame.yaml",
            mode="gsplat",
            gsplat_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_kitchen_4th_day",
            transform_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/pick_place_robot_room/cic_kitchen_4th_day",
            invisible_prefix=["box", "goal-area", "gripper", "ur5"],
        ),
        strict=strict,
    )
    add_env(
        env_id="PickPlaceRobotRoom-single_random-gsplat-cic_kitchen_4th_night",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer=make_schema,
            task=SingleBoxRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist","stereo_far_left","stereo_far_right"],
            keyframe_file="pick_place_robot_room.frame.yaml",
            mode="gsplat",
            gsplat_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_kitchen_4th_night",
            transform_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/pick_place_robot_room/cic_kitchen_4th_night",
            invisible_prefix=["box", "goal-area", "gripper", "ur5"],
        ),
        strict=strict,
    )
    add_env(
        env_id="PickPlaceRobotRoom-single_random-gsplat-google_building_table",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer=make_schema,
            task=SingleBoxRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist","stereo_far_left","stereo_far_right"],
            keyframe_file="pick_place_robot_room.frame.yaml",
            mode="gsplat",
            gsplat_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/google_building_table",
            transform_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/pick_place_robot_room/google_building_table",
            invisible_prefix=["box", "goal-area", "gripper", "ur5"],
        ),
        strict=strict,
    )
    add_env(
        env_id="PickPlaceRobotRoom-single_random-gsplat-mit_medical_wood_chair",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer=make_schema,
            task=SingleBoxRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist","stereo_far_left","stereo_far_right"],
            keyframe_file="pick_place_robot_room.frame.yaml",
            mode="gsplat",
            gsplat_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/mit_medical_wood_chair",
            transform_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/pick_place_robot_room/mit_medical_wood_chair",
            invisible_prefix=["box", "goal-area", "gripper", "ur5"],
        ),
        strict=strict,
    )

    add_env(
        env_id="PickPlaceRobotRoom-single_random-domain_rand-v2",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer =make_schema,
            task=SingleBoxRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist","stereo_far_left","stereo_far_right"],
            keyframe_file="pick_place_robot_room.frame.yaml",
            mode="domain_rand",
            randomize_color=True,
            randomize_lighting=True,
            randomize_camera=False,
        ),
        strict=strict,
    )


    add_env(
        env_id="PickPlaceRobotRoom-single_random-domain_rand-v3",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer =make_schema,
            task=SingleBoxRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist","stereo_far_left","stereo_far_right"],
            keyframe_file="pick_place_robot_room.frame.yaml",
            mode="domain_rand",
            randomize_color=False,
            randomize_lighting=True,
            randomize_camera=False,
        ),
        strict=strict,
    )


if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Save

    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))
    #
    # from vuer_mujoco.tasks import make
    #
    #
    # env = make("TheFinalCalibrationEval-fixed-v1")
    #
    # obs = env.reset()
    # from matplotlib import pyplot as plt
    #
    # # plt.imshow(obs["left/rgb"])
    # plt.imsave("left_rgb.png", obs["left/rgb"])
    # plt.imsave("right_rgb.png", obs["right/rgb"])
    # plt.imsave("wrist_rgb.png", obs["wrist/rgb"])
    # save without the borders and keep the resolution the same
    # plt.axis("off")
    # plt.imshow(obs["left/rgb"])
    # plt.show()

    # plt.axis("off")
    # plt.imshow(obs["right/rgb"])
    # plt.show()
    # plt.savefig("right_rgb.png", bbox_inches='tight', pad_inches=0)
    # plt.show()

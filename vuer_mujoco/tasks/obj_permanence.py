import warnings
from pathlib import Path

import numpy as np

from vuer_mujoco.schemas.objects.mj_sdf import MjSDF
from vuer_mujoco.tasks._floating_robotiq import FloatingRobotiq2f85
from vuer_mujoco.schemas.components.rigs.camera_rig import make_camera_rig
from vuer_mujoco.schemas.components.concrete_slab import ConcreteSlab
from vuer_mujoco.tasks.base.lucidxr_task import get_site, init_states
from vuer_mujoco.tasks.base.mocap_task import MocapTask
from vuer_mujoco.schemas.objects.orbit_table import OpticalTable

# x1, y1 = random.uniform(0.15, 0.2), random.uniform(-0.1, 0.1)
# x2, y2 = random.uniform(0.2, 0.4), random.uniform(-0.2, 0.2)

# scene center is 0.41 + 0.2 / 2 = 0.50
center = 0.5
x1, y1 = center - 0.07, 0.09
x2, y2 = center - 0.10, -0.05
x3, y3 = center - 0.00, -0.15
x4, y4 = center - 0.15, -0.14


def make_schema(mode="cameraready", robot="panda", show_robot=False, **options):
    from vuer_mujoco.schemas.utils.file import Prettify
    from vuer_mujoco.schemas.objects.ball import Ball

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
    # camera_rig = make_camera_rig(optical_table._pos)

    table_slab = ConcreteSlab(
        assets="model",
        pos=[0, 0, 0.777],
        group=4,
        rgba="0.8 0 0 0.9",
        _attributes={
            "name": "table",
        },
    )

    camera_rig = make_camera_rig(table_slab.surface_origin)

    box = MjSDF(
        mass=0.3,
        pos=[x1, y1, 0.85],
        quat=[0.607299, 0.606557, -0.360798, -0.364831],
        assets="ball_sorting_toy",
        _attributes={"name": "ball-sorting-toy", "quat": "0.707 0.707 0 0"},
        additional_children_raw="""
        <!-- Approximated square corners for circle in XZ plane -->
        <site name="ball-sorting-toy_corner1" pos="0.03 0.035 -0.08" size="0.01" rgba="1 1 0 0"/>
        <site name="ball-sorting-toy_corner2" pos="-0.03 0.035 -0.08" size="0.01" rgba="1 1 0 0"/>
        <site name="ball-sorting-toy_corner3" pos="0.0 0.035 -0.05" size="0.01" rgba="1 1 0 0"/>
        <site name="ball-sorting-toy_corner4" pos="0.0 0.035 -0.11" size="0.01" rgba="1 1 0 0"/>
        """,
        scale="0.12 0.12 0.12",
    )
    ball_1 = Ball(
        size="0.022",
        pos=[x2, y2, 0.85],
        quat=[0, 0, 1, 0],
        rgba="1 0 0 1",
        _attributes={
            "name": "ball-1",
        },
    )
    ball_2 = Ball(
        size="0.022",
        pos=[x3, y3, 0.85],
        quat=[0, 0, 1, 0],
        rgba="0 0 1 1",
        _attributes={
            "name": "ball-2",
        },
    )
    ball_3 = Ball(
        size="0.022",
        pos=[x4, y4, 0.85],
        quat=[0, 0, 1, 0],
        rgba="0 1 0 1",
        _attributes={
            "name": "ball-3",
        },
    )

    children = [
        *camera_rig.get_cameras(),
        table_slab,
        box,
        ball_1,
        ball_2,
        ball_3,
    ]

    if mode == "demo":
        pass
    elif mode == "cameraready":
        children += [optical_table]

    if show_robot:
        children.append(panda)
        children.append(gripper._mocaps)
        pass

    scene = FloatingRobotiq2f85(*children, pos=[0, 0, 1.0], **options)

    return scene._xml | Prettify()


class ObjPermanence(MocapTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.red_ball = get_site(self.physics, "ball-1")
        self.blue_ball = get_site(self.physics, "ball-2")
        self.green_ball = get_site(self.physics, "ball-3")

        self.goal_corners = [get_site(self.physics, f"ball-sorting-toy_corner{i}") for i in range(1, 5)]

    def point_in_box(self, point, corners, tol_z=0.01):
        positions = [corner.pos for corner in corners]
        x_vals = [p[0] for p in positions]
        y_vals = [p[1] for p in positions]
        z_avg = np.mean([p[2] for p in positions])

        x_min, x_max = min(x_vals), max(x_vals)
        y_min, y_max = min(y_vals), max(y_vals)

        return x_min <= point[0] <= x_max and y_min <= point[1] <= y_max and abs(point[2] - z_avg) < tol_z

    def get_reward(self, physics):
        reward = 0.0
        warnings.warn("Reward is untested for this env, bc we had no working policy")

        self.green_success = False
        self.red_success = False
        self.blue_success = False

        if self.point_in_box(physics.data.site_xpos[self.red_ball.id], self.goal_corners):
            self.red_success = True
        if self.point_in_box(physics.data.site_xpos[self.blue_ball.id], self.goal_corners):
            self.blue_success = True
        if self.point_in_box(physics.data.site_xpos[self.green_ball.id], self.goal_corners):
            self.green_success = True

        if self.red_success and self.blue_success and self.green_success:
            reward = 1.0
        return reward


class BallRand(ObjPermanence):
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
        return dict(qpos=new_qpos, quat=quat, **kwargs)


def register():
    from vuer_mujoco.tasks import add_env
    from vuer_mujoco.tasks.entrypoint import make_env

    add_env(
        env_id="ObjPermanence-fixed-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=ObjPermanence,
            camera_names=["front", "right", "wrist"],
            xml_renderer=make_schema,
            keyframe_file="obj_permanence.frame.yaml",
            workdir=Path(__file__).parent,
            mode="render",
        ),
    )
    add_env(
        env_id="ObjPermanence-ball_rand-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=ObjPermanence,
            # include top for visualization, will remove later after figuring out a better pattern.
            camera_names=["front", "right", "wrist", "top"],
            xml_renderer=make_schema,
            keyframe_file=None,
            workdir=Path(__file__).parent,
            mode="render",
        ),
    )
    add_env(
        env_id="ObjPermanence-lucid-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=ObjPermanence,
            camera_names=["right", "right_r", "wrist", "front"],
            xml_renderer=make_schema,
            keyframe_file="obj_permanence.frame.xml",
            workdir=Path(__file__).parent,
            mode="lucid",
            prefix_to_class_ids={"ball-1": 148, "table": 100, "ball-2": 148, "ball-sorting-toy": 41},
            object_prefix="mug",
        ),
    )


if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Save

    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

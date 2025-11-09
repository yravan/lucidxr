import random
from pathlib import Path

import numpy as np

from vuer_mujoco.schemas.objects.mj_sdf import MjSDF
from vuer_mujoco.schemas.components.rigs.camera_rig_calibrated import make_camera_rig
from vuer_mujoco.tasks._floating_robotiq import UR5Robotiq2f85
from vuer_mujoco.tasks.base.lucidxr_task import get_site, get_geom_id
from vuer_mujoco.tasks.base.mocap_task import MocapTask
from vuer_mujoco.vendors.robohive.robohive_object import RobohiveObj


# scene center is 0.41 + 0.2 / 2 = 0.50
x1, y1 = -0.08, 0.08
x2, y2 = 0.1, 0.05
x3, y3 = 0.05, -0.2
x4, y4 = -0.08, -0.11


def make_schema(**options):
    from vuer_mujoco.schemas.utils.file import Prettify
    from vuer_mujoco.schemas.objects.cylinder import Cylinder

    table = RobohiveObj(
        otype="furniture",
        asset_key="simpleTable/simpleWoodTable",
        pos=[0, 0, 0],
        quat=[0.7071, 0, 0, 0.7071],
        local_robohive_root="robohive",
    )

    camera_rig = make_camera_rig(pos=[-0.4, 0, 0.77])

    box = MjSDF(
        pos=[x2, y2, 0.85],
        quat=[0.677739, 0.682136, -0.201568, -0.186361],
        assets="ball_sorting_toy",
        _attributes={"name": "ball-sorting-toy", "quat": "0.707 0.707 0 0"},
        mass=0.5,
        # scale="0.0972099048 0.0936407778 0.0908795652",
        scale="0.113 0.113 0.113",
    )
    ball_1 = Cylinder(
        pos=[x1, y1, 0.8],
        quat=[0, 0, 1, 0],
        rgba="0.7421875 0.25 0.2656 1",
        _attributes={
            "name": "cylinder-1",
        },
    )
    ball_2 = Cylinder(
        pos=[x3, y3, 0.8],
        quat=[0, 0, 1, 0],
        rgba="0.1953125 0.3203125 0.54296875 1",
        _attributes={
            "name": "cylinder-2",
        },
    )
    ball_3 = Cylinder(
        pos=[x4, y4, 0.8],
        quat=[0, 0, 1, 0],
        rgba="0.4765625 0.68359375 0.29296875 1",
        _attributes={
            "name": "cylinder-3",
        },
    )

    children = [
        *camera_rig.get_cameras(),
        box,
        table,
        ball_1,
        ball_2,
        ball_3,
    ]

    scene = UR5Robotiq2f85(
        *children,
        pos=[-0.4, 0, 0.77],
        **options,
        camera_rig=camera_rig,
    )

    return scene._xml | Prettify()

class Fixed(MocapTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # … your existing site/geom setup …
        self.set_sites()

        # define the order you want: red → green → blue
        self.color_order_ids = [
            self.red_ball_id,
            self.green_ball_id,
            self.blue_ball_id,
        ]
        # how many in-sequence contacts we’ve already seen (0..3)
        self.order_progress = 0

    def set_sites(self):
        self.gripper_site = get_site(self.physics, "gripper-pinch")

        self.box_geom_id = get_geom_id(self.physics, "ball-sorting-toy")
        self.red_ball_id = get_geom_id(self.physics, "cylinder-1")
        self.blue_ball_id = get_geom_id(self.physics, "cylinder-2")
        self.green_ball_id = get_geom_id(self.physics, "cylinder-3")

    def get_reward(self, physics):
        # scan all current contacts
        for i in range(physics.data.ncon):
            c = physics.data.contact[i]
            geoms = {c.geom1, c.geom2}

            # if the box is involved, and we still have more in our target list…
            if self.box_geom_id in geoms and self.order_progress < len(self.color_order_ids):
                # check if the *next* required ball is in this contact
                target_id = self.color_order_ids[self.order_progress]
                if target_id in geoms:
                    # advance progress exactly once per ball
                    self.order_progress += 1

        # reward is fraction of the sequence completed
        print(f"Order progress: {self.order_progress}/{len(self.color_order_ids)}")
        return self.order_progress / len(self.color_order_ids)


class ColorRandom(Fixed):
    box_qpos_addr = 0
    ball_qpos_addrs = [7, 14, 21]

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
        new_qpos = qpos.copy()
        # randomly swap the balls positions
        positions = [
            [x1, y1, 0.8],
            [x3, y3, 0.8],
            [x4, y4, 0.8],
        ]
        random.shuffle(positions)
        for i, ball_addr in enumerate(cls.ball_qpos_addrs):
            new_qpos[ball_addr] = positions[i][0]
            new_qpos[ball_addr + 1] = positions[i][1]
            new_qpos[ball_addr + 2] = positions[i][2]
        if mocap_pos is not None:
            mocap_pos = mocap_pos.copy()
            mocap_pos += np.random.normal(0.0, 0.005, mocap_pos.shape)

        return dict(qpos=new_qpos, quat=quat, mocap_pos=mocap_pos, **kwargs)


def register(strict=True):
    from vuer_mujoco.tasks import add_env
    from vuer_mujoco.tasks.entrypoint import make_env

    add_env(
        env_id="BallSortingToyCalibrated-fixed-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="ball_sorting_toy_calibrated.mjcf.xml",
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist"],
            keyframe_file="ball_sorting_toy_calibrated.frame.yaml",
        ),
        strict=strict,
    )

    add_env(
        env_id="BallSortingToyCalibrated-color_random-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="ball_sorting_toy_calibrated.mjcf.xml",
            task=ColorRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist"],
            keyframe_file="ball_sorting_toy_calibrated.frame.yaml",
        ),
        strict=strict,
    )

    add_env(
        env_id="BallSortingToyCalibrated-color_random-lucid-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="ball_sorting_toy_calibrated.mjcf.xml",
            task=ColorRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist"],
            keyframe_file="ball_sorting_toy_calibrated.frame.yaml",
            mode="lucid",
            object_keys=["ball-sorting-toy", "cylinder-1", "cylinder-2", "cylinder-3"],
            invisible_prefix=["ball-sorting-toy", "cylinder-1", "cylinder-2", "cylinder-3", "gripper", "ur5"],
        ),
        strict=strict,
    )

    add_env(
        env_id="BallSortingToyCalibrated-color_random-dr-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="ball_sorting_toy_calibrated.mjcf.xml",
            task=ColorRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist"],
            keyframe_file="ball_sorting_toy_calibrated.frame.yaml",
            mode="domain_rand",
            color_randomization_args=dict(
                ignore_geom_names=["ur5*", "gripper*", "ball-sorting-toy*", "cylinder-1*", "cylinder-2*", "cylinder-3*"],
            ),
            camera_randomization_args=dict(
                camera_names=["left", "right"],
            ),
        ),
        strict=strict,
    )


if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Save

    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

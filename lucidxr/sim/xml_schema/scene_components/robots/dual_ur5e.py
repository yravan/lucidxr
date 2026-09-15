from lucidxr.sim.xml_schema.robots.arms.ur5e import UR5e
from lucidxr.sim.xml_schema.robots.grippers.robotiq_2f85 import Robotiq2F85
from lucidxr.sim.xml_schema.schema import Group
from lucidxr.sim.xml_schema.transforms.mujoco import z_rot, π


class DualUR5e(Group):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        left_gripper = Robotiq2F85(
            assets="robots/robotiq_2f85",
            attributes={"name": "left-gripper"},
            mocap_pos=self._pos + [0, 0, -0.15] + [-0.15, 0, 0],
        )
        right_gripper = Robotiq2F85(
            assets="robots/robotiq_2f85",
            attributes={"name": "right-gripper"},
            mocap_pos=self._pos + [0, 0, -0.15] + [0.15, 0, 0],
        )

        self._children = (
            UR5e(
                assets="robots/ur5e",
                pos=self._pos + [-0.25, 0.5, 0],
                quat=z_rot(-π / 2),
                attributes={"name": "left_arm"},
                end_effector=left_gripper,
            ),
            UR5e(
                assets="robots/ur5e",
                pos=self._pos + [0.25, 0.5, 0],
                quat=z_rot(-π / 2),
                attributes={"name": "right_arm"},
                end_effector=right_gripper,
            ),
            *self._children,
            left_gripper._mocaps,
            right_gripper._mocaps,
        )

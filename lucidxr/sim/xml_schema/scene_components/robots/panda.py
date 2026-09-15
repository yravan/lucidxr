"""Panda arm with a Tomika gripper and its world-level control target."""

from lucidxr.sim.xml_schema.base import attribute_value
from lucidxr.sim.xml_schema.robots.arms.franka_panda import Panda
from lucidxr.sim.xml_schema.robots.grippers.tomika_gripper import TomikaGripper
from lucidxr.sim.xml_schema.schema import Group


class PandaTomika(Group):
    def __init__(
        self,
        *,
        pos=(0, 0, 0.79),
        quat=(1, 0, 0, 0),
        name="panda",
        gripper_name="gripper",
        mocap_pos=(0.25, 0, 1.1),
        mocap_quat=(0, 0, 1, 0),
        wrist_mount="",
    ):
        self.gripper = TomikaGripper(
            name=gripper_name, mocap_pos=mocap_pos, mocap_quat=attribute_value(mocap_quat), wrist_mount=wrist_mount
        )
        self.robot = Panda(end_effector=self.gripper, name=name, pos=pos, quat=quat)
        super().__init__(self.robot, self.gripper._mocaps)

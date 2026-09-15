from lucidxr.sim.xml_schema.robots.grippers.robotiq_2f85 import Robotiq2F85
from lucidxr.sim.xml_schema.schema import FreeBody, Group


class DualRobotiq(Group):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        left_gripper = Robotiq2F85(
            assets="robots/robotiq_2f85",
            attributes={"name": "left-gripper"},
            mocap_pos=self._pos + [-0.5, 0.8, 1.6],
        )
        right_gripper = Robotiq2F85(
            assets="robots/robotiq_2f85",
            attributes={"name": "right-gripper"},
            mocap_pos=self._pos + [0.5, 0.8, 1.6],
        )

        self._children = (
            *self._children,
            FreeBody(
                left_gripper,
                joint_name="left-gripper-float-floating-base",
                attributes={"name": "left-gripper-float"},
            ),
            FreeBody(
                right_gripper,
                joint_name="right-gripper-float-floating-base",
                attributes={"name": "right-gripper-float"},
            ),
            left_gripper._mocaps,
            right_gripper._mocaps,
        )

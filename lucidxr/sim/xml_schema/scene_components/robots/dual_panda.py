from lucidxr.sim.xml_schema.robots.arms.franka_panda import Panda
from lucidxr.sim.xml_schema.robots.grippers.tomika_gripper import TomikaGripper
from lucidxr.sim.xml_schema.schema import Group
from lucidxr.sim.xml_schema.transforms.mujoco import z_rot, π


class DualPanda(Group):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        left_gripper = TomikaGripper(assets="robots/tomika_gripper", attributes={"name": "left-gripper"})
        right_gripper = TomikaGripper(assets="robots/tomika_gripper", attributes={"name": "right-gripper"})

        self._children = (
            Panda(
                assets="robots/franka_panda",
                pos=self._pos + [-0.25, 0.5, 0],
                quat=z_rot(π / 2),
                attributes={"name": "left_panda"},
                end_effector=left_gripper,
            ),
            Panda(
                assets="robots/franka_panda",
                pos=self._pos + [0.25, 0.5, 0],
                quat=z_rot(π / 2),
                attributes={"name": "right_panda"},
                end_effector=right_gripper,
            ),
            *self._children,
            left_gripper._mocaps,
            right_gripper._mocaps,
        )

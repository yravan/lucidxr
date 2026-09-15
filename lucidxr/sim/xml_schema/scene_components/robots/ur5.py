from lucidxr.sim.xml_schema.robots.arms.ur5e import UR5e
from lucidxr.sim.xml_schema.robots.grippers.robotiq_2f85 import Robotiq2F85
from lucidxr.sim.xml_schema.robots.hands.shadow_hand import ShadowHandRight
from lucidxr.sim.xml_schema.scene_components.cameras.rig import make_camera_rig
from lucidxr.sim.xml_schema.schema import Group


class UR5Robotiq2f85(Group):
    """A class that combines UR5 robot with Robotiq gripper."""

    name = "ur5-robotiq-2f85"

    def __init__(self, *, dual_robot=False, camera_rig=None, **kwargs):
        super().__init__(**kwargs)

        if camera_rig is None:
            camera_rig = make_camera_rig(self._pos)
        robot = UR5e(
            name="ur5",
            assets="robots/ur5e",
            pos=self._pos,
            quat=[1, 0, 0, 1],  # Aligned with table scene
            end_effector=Robotiq2F85(
                assets="robots/robotiq_2f85",
                attributes={"name": "gripper"},
                gripper_mass=0.05,
                pos=[0, 0, 0],  # Position at the end of UR5
                quat=[1, 0, 0, 1],  # Aligned with table scene
                wrist_mount=camera_rig.wrist_camera(name="wrist"),
                mocap_pos=f"{self._pos[0]} {self._pos[1] + 0.3} {self._pos[2] + 0.2}",
            ),
        )
        _children = (robot, robot.end_effector._mocaps)

        if dual_robot:
            robot_2 = UR5e(
                name="ur5-2",
                assets="robots/ur5e",
                pos=self._pos + [0, -0.3, 0],
                quat=[1, 0, 0, 1],  # Aligned with table scene
                end_effector=Robotiq2F85(
                    assets="robots/robotiq_2f85",
                    attributes={"name": "gripper-2"},
                    gripper_mass=0.05,
                    pos=[0, 0, 0],  # Position at the end of UR5
                    quat=[1, 0, 0, 1],  # Aligned with table scene
                    wrist_mount=camera_rig.wrist_camera(name="wrist_2"),
                    mocap_pos=f"{self._pos[0]} {self._pos[1] - 0.3} {self._pos[2] + 0.1}",  # Position mocap at robot's end effector
                ),
            )
            _children = (robot, robot_2, robot.end_effector._mocaps, robot_2.end_effector._mocaps)

        self._children = tuple(_children)


class UR5ShadowHand(Group):
    """A class that combines UR5 robot with Robotiq gripper."""

    name = "ur5-shadowhand"

    def __init__(self, *, dual_robot=False, camera_rig=None, **kwargs):
        super().__init__(**kwargs)

        if camera_rig is None:
            camera_rig = make_camera_rig(self._pos)
        robot = UR5e(
            name="ur5",
            assets="robots/ur5e",
            pos=self._pos,
            quat=[1, 0, 0, 1],  # Aligned with table scene
            end_effector=ShadowHandRight(
                free_joint=False,
                assets="robots/shadow_hand",
                pos=[0, -0.01, -0.2],  # Position at the end of UR5
                quat=[1, 0, 0, 1],  # Aligned with table scene
                wrist_mount=camera_rig.wrist_camera(name="wrist"),
            ),
        )
        _children = (robot, robot.end_effector._mocaps)

        self._children = tuple(_children)

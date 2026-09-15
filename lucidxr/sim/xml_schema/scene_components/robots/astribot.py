from lucidxr.sim.xml_schema.robots.arms.astribot import Astribot
from lucidxr.sim.xml_schema.robots.grippers.robotiq_2f85 import Robotiq2F85
from lucidxr.sim.xml_schema.robots.hands.shadow_hand import ShadowHandLeft
from lucidxr.sim.xml_schema.scene_components.cameras.rig import make_camera_rig
from lucidxr.sim.xml_schema.schema import Group


class AstribotRobotiq2f85(Group):
    """A class that combines UR5 robot with Robotiq gripper."""

    name = "ur5-robotiq-2f85"

    def __init__(
        self,
        dual_robot=False,
        camera_rig=None,
        head_quat=None,
        mocap_pos=None,
        mocap_quat=None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        if camera_rig is None:
            camera_rig = make_camera_rig(self._pos)
        robot = Astribot(
            name="astribot_s1",
            assets="robots/astribot",
            pos=self._pos,
            head_mocap_quat=head_quat,
            quat=[1, 0, 0, 0],  # Aligned with table scene
            end_effector=Robotiq2F85(
                assets="robots/robotiq_2f85",
                attributes={"name": "gripper"},
                gripper_mass=0.05,
                pos=[0, 0, 0],  # Position at the end of UR5
                quat=[1, 0, 0, 0],  # Aligned with table scene
                wrist_mount=camera_rig.wrist_camera(name="wrist"),
                mocap_pos=mocap_pos,
                mocap_quat=mocap_quat,
            ),
        )
        _children = (
            robot,
            robot.end_effector._mocaps,
            robot._mocaps,
        )

        self._children = tuple(_children)


class AstribotHand(Group):
    """A class that combines UR5 robot with Robotiq gripper."""

    name = "ur5-robotiq-2f85"

    def __init__(
        self,
        dual_robot=False,
        camera_rig=None,
        head_quat=None,
        mocap_pos=None,
        mocap_quat=None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        if camera_rig is None:
            camera_rig = make_camera_rig(self._pos)
        robot = Astribot(
            name="astribot_s1",
            assets="robots/astribot",
            pos=self._pos,
            head_mocap_quat=head_quat,
            quat=[1, 0, 0, 0],  # Aligned with table scene
            end_effector=ShadowHandLeft(
                free_joint=False,
                assets="robots/shadow_hand",
                attributes={"name": "shadow_hand_left"},
                pos=[0, 0, 0],  # Position at the end of UR5
                wrist_mount=camera_rig.wrist_camera(name="wrist"),
                mocap_pos=mocap_pos,
                mocap_quat=mocap_quat,
            ),
        )
        _children = (
            robot,
            robot.end_effector._mocaps,
            robot._mocaps,
        )

        self._children = tuple(_children)

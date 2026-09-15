from lucidxr.sim.xml_schema.robots.arms.ur5e import UR5e
from lucidxr.sim.xml_schema.robots.grippers.robotiq_2f85 import Robotiq2F85
from lucidxr.sim.xml_schema.scene_components.cameras.rig import make_camera_rig
from lucidxr.sim.xml_schema.schema import FreeBody, Group
from lucidxr.sim.xml_schema.simple_components.motion import XYBody


class FloatingRobotiq2f85(Group):
    name = "floating-robotiq-2f85"

    def __init__(
        self,
        dual_gripper=False,
        include_ur5=False,
        camera_rig=None,
        free_joint=True,
        quat=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if camera_rig is None:
            camera_rig = make_camera_rig(self._pos)

        quat_input = quat if quat is not None else [0, 0, 1, 0]

        if include_ur5:
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
                    mocap_pos=f"{self._pos[0]} {self._pos[1] + 0.3} {self._pos[2] + 0.2}",  # Position mocap at robot's end effector
                ),
            )
            base_1 = FreeBody(
                robot, joint_name="robot-float-floating-base", attributes={"name": "robot-float"}
            )
            _children = (base_1, robot.end_effector._mocaps)

            if dual_gripper:
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
                base_2 = FreeBody(
                    robot_2, joint_name="robot-2-float-floating-base", attributes={"name": "robot-2-float"}
                )
                _children = (base_1, base_2, robot.end_effector._mocaps, robot_2.end_effector._mocaps)
        else:
            gripper = Robotiq2F85(
                assets="robots/robotiq_2f85",
                attributes={"name": "gripper"},
                gripper_mass=0.05,
                pos=self._pos + [0, 0, 0.3] if not dual_gripper else self._pos + [0, 0.15, 0.3],
                quat=quat_input,
                wrist_mount=camera_rig.wrist_camera(name="wrist"),
            )
            base_1 = (
                FreeBody(
                    gripper, joint_name="gripper-float-floating-base", attributes={"name": "gripper-float"}
                )
                if free_joint
                else XYBody(gripper, attributes={"name": "gripper-float"})
            )
            _children = (base_1, gripper._mocaps)

            if dual_gripper:
                gripper_2 = Robotiq2F85(
                    assets="robots/robotiq_2f85",
                    attributes={"name": "gripper-2"},
                    gripper_mass=0.05,
                    pos=self._pos + [0, -0.15, 0.3],
                    quat=[0, 0, 1, 0],
                    wrist_mount=camera_rig.wrist_camera(name="wrist_2"),
                )
                base_2 = (
                    FreeBody(
                        gripper_2,
                        joint_name="gripper-2-float-floating-base",
                        attributes={"name": "gripper-2-float"},
                    )
                    if free_joint
                    else XYBody(gripper_2, attributes={"name": "gripper-2-float"})
                )
                _children = (base_1, base_2, gripper._mocaps, gripper_2._mocaps)

        self._children = tuple(_children)

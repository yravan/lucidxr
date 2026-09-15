"""Object permanence: composed from the shared XML schema library."""

from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.objects.mj_sdf import MjSDF
from lucidxr.sim.xml_schema.objects.orbit_table import OpticalTable
from lucidxr.sim.xml_schema.scene_components.cameras.rig import make_camera_rig
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.floating_robotiq import FloatingRobotiq2f85
from lucidxr.sim.xml_schema.scene_components.robots.panda import PandaTomika
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.schema import Mjcf
from lucidxr.sim.xml_schema.simple_components.concrete_slab import ConcreteSlab


class ObjectPermanence(Scene):
    def build(self) -> Mjcf:
        options = dict(self.options)
        mode = options.pop("mode", "cameraready")
        robot = options.pop("robot", "panda")
        show_robot = options.pop("show_robot", False)
        center = 0.5
        x1, y1 = (center - 0.07, 0.09)
        x2, y2 = (center - 0.1, -0.05)
        x3, y3 = (center - 0.0, -0.15)
        x4, y4 = (center - 0.15, -0.14)
        from lucidxr.sim.xml_schema.objects.ball import Ball

        if robot != "panda":
            raise ValueError(f"Unknown robot: {robot}")
        panda = PandaTomika(name="test_panda", gripper_name="test_gripper", wrist_mount="")
        optical_table = OpticalTable(
            pos=[0, 0, 0.79], assets="objects/optical_table", _attributes={"name": "table_optical"}
        )
        table_slab = ConcreteSlab(
            assets="objects/optical_table",
            pos=[0, 0, 0.777],
            group=4,
            rgba="0.8 0 0 0.9",
            _attributes={"name": "table"},
        )
        camera_rig = make_camera_rig(table_slab.surface_origin)
        box = MjSDF(
            mass=0.3,
            pos=[x1, y1, 0.85],
            quat=[0.607299, 0.606557, -0.360798, -0.364831],
            assets="objects/ball_sorting_toy",
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
            _attributes={"name": "ball-1"},
        )
        ball_2 = Ball(
            size="0.022",
            pos=[x3, y3, 0.85],
            quat=[0, 0, 1, 0],
            rgba="0 0 1 1",
            _attributes={"name": "ball-2"},
        )
        ball_3 = Ball(
            size="0.022",
            pos=[x4, y4, 0.85],
            quat=[0, 0, 1, 0],
            rgba="0 1 0 1",
            _attributes={"name": "ball-3"},
        )
        children = [*camera_rig.get_cameras(), table_slab, box, ball_1, ball_2, ball_3]
        if mode == "demo":
            pass
        elif mode == "cameraready":
            children += [optical_table]
        if show_robot:
            children.append(panda)
            pass
        scene = Mjcf(
            WorldSettings("pastel"),
            LightingRig([0, 0, 1.0]),
            *children,
            FloatingRobotiq2f85(pos=[0, 0, 1.0], **options),
        )
        return scene

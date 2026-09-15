"""Insert shapes: composed from the shared XML schema library."""

from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.objects.orbit_table import OpticalTable
from lucidxr.sim.xml_schema.objects.sort_shapes import (
    CircleBlock,
    HexBlock,
    LeBox,
    SquareBlock,
    TriangleBlock,
)
from lucidxr.sim.xml_schema.scene_components.cameras.rig import make_camera_rig
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.floating_robotiq import FloatingRobotiq2f85
from lucidxr.sim.xml_schema.scene_components.robots.panda import PandaTomika
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.schema import Mjcf
from lucidxr.sim.xml_schema.simple_components.concrete_slab import ConcreteSlab


class InsertShapes(Scene):
    def build(self) -> Mjcf:
        options = dict(self.options)
        mode = options.pop("mode", "cameraready")
        robot = options.pop("robot", "panda")
        show_robot = options.pop("show_robot", False)
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
            rgba="0.8 0 0 0.0",
            _attributes={"name": "table"},
        )
        camera_rig = make_camera_rig(table_slab.surface_origin)
        scale = 0.075
        lebox = LeBox(
            pos=[0.5, 0, 0.85],
            assets="objects/sort_shape",
            _attributes={"name": "lebox", "quat": "1 0 0 0"},
            scale=1.1 * scale,
        )
        hexblock = HexBlock(
            pos=[0.25, -0.05, 0.85],
            assets="objects/sort_shape",
            _attributes={"name": "block_hex", "quat": "1 0 0 0"},
            scale=scale,
        )
        squareblock = SquareBlock(
            pos=[0.25, 0.05, 0.85],
            assets="objects/sort_shape",
            _attributes={"name": "block_square", "quat": "1 0 0 0"},
            scale=scale,
        )
        triangleblock = TriangleBlock(
            pos=[0.35, -0.05, 0.85],
            assets="objects/sort_shape",
            _attributes={"name": "block_triangle", "quat": "1 0 0 0"},
            scale=scale,
        )
        circleblock = CircleBlock(
            pos=[0.35, 0.05, 0.85],
            assets="objects/sort_shape",
            _attributes={"name": "block_circle", "quat": "1 0 0 0"},
            scale=scale,
        )
        children = [
            *camera_rig.get_cameras(),
            table_slab,
            lebox,
            hexblock,
            squareblock,
            triangleblock,
            circleblock,
        ]
        if mode == "demo":
            pass
        elif mode == "cameraready":
            children += [optical_table]
        if show_robot:
            children.append(panda)
        scene = Mjcf(
            WorldSettings("pastel"),
            LightingRig([0, 0, 1.0]),
            *children,
            FloatingRobotiq2f85(pos=[0, 0, 1.0], **options),
        )
        return scene

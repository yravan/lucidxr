"""Sort shape: composed from the shared XML schema library."""

from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.floating_robotiq import FloatingRobotiq2f85
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.schema import Mjcf
from lucidxr.sim.xml_schema.simple_components.concrete_slab import ConcreteSlab
from lucidxr.sim.xml_schema.simple_components.force_plate import ForcePlate


class SortShapes(Scene):
    def build(self) -> Mjcf:
        options = dict(self.options)
        from lucidxr.sim.xml_schema.objects import CircleBlock, LeBox, SquareBlock, TriangleBlock
        from lucidxr.sim.xml_schema.objects.sort_shapes import HexBlock

        table = ConcreteSlab(pos=[0, 0, 0.6], rgba="0.8 0.8 0.8 1")
        ibox = LeBox(attributes={"name": "insertion-box"}, assets="objects/sort_shape", pos=[0, 0, 0.7])
        square_block = SquareBlock(
            attributes={"name": "square"}, assets="objects/sort_shape", pos=[0.2, -0.1, 0.7]
        )
        triangle_block = TriangleBlock(
            attributes={"name": "triangle"}, assets="objects/sort_shape", pos=[0.4, -0.1, 0.7]
        )
        hex_block = HexBlock(attributes={"name": "hex"}, assets="objects/sort_shape", pos=[0.2, 0.1, 0.7])
        circle_block = CircleBlock(
            attributes={"name": "circle"}, assets="objects/sort_shape", pos=[0.4, 0.1, 0.7]
        )
        work_area = ForcePlate(
            name="start-area",
            pos=(0.3, 0, 0.605),
            quat=(0, 1, 0, 0),
            type="box",
            size="0.15 0.15 0.01",
            rgba="1 0 0 0.1",
        )
        scene = Mjcf(
            WorldSettings("pastel"),
            LightingRig([0, 0, 0.8]),
            table,
            ibox,
            square_block,
            triangle_block,
            hex_block,
            circle_block,
            work_area,
            FloatingRobotiq2f85(pos=[0, 0, 0.8], **options),
        )
        return scene

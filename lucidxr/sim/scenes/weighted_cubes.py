"""Weighted cubes: composed from the shared XML schema library."""

from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.objects.cube import Cube
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.floating_robotiq import FloatingRobotiq2f85
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.scene_components.tables import Tabletop
from lucidxr.sim.xml_schema.schema import Mjcf


class WeightedCubes(Scene):
    def build(self) -> Mjcf:
        table = Tabletop(name="concrete-slab")
        cubes = [
            Cube(name=f"box-{i}", pos=(x, 0, 0.7), rgba=color, half_size=0.015, mass=1)
            for i, (x, color) in enumerate(((-0.1, "1 0 0 1"), (0, "0 1 0 1"), (0.1, "0 0 1 1")), 1)
        ]
        scene = Mjcf(
            WorldSettings("pastel"),
            LightingRig([0, 0, 0.8]),
            table,
            *cubes,
            FloatingRobotiq2f85(pos=[0, 0, 0.8]),
        )
        return scene

"""Robosuite door: composed from the shared XML schema library."""

from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.adapters.robosuite.robosuite_door import RobosuiteDoor as DoorObject
from lucidxr.sim.xml_schema.adapters.robosuite.robosuite_tablearena import RobosuiteTableArena
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.floating_robotiq import FloatingRobotiq2f85
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.schema import Mjcf


class RobosuiteDoor(Scene):
    def build(self) -> Mjcf:
        options = dict(self.options)
        rng = self.rng
        x, y = (rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2))
        arena = RobosuiteTableArena(table_pos=f"{x} {y} 0.775")
        door = DoorObject(
            _attributes=dict(name="door-1", pos=f"{x + 0.1} {y - 0.002} 1.1", quat="0.618783 0 0 -0.785562")
        )
        scene = Mjcf(
            WorldSettings("pastel"),
            LightingRig([0, 0, 0.8]),
            arena,
            door,
            FloatingRobotiq2f85(pos=[0, 0, 0.8], **options),
        )
        return scene

"""Pick block: composed from the shared XML schema library."""

from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.adapters.robohive.robohive_object import RobohiveObj
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.floating_robotiq import FloatingRobotiq2f85
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.schema import Body, Mjcf
from lucidxr.sim.xml_schema.simple_components.tile_floor import TileFloor


class PickBlock(Scene):
    def build(self) -> Mjcf:
        rng = self.rng
        r, g, b = (rng.uniform(0, 1), rng.uniform(0, 1), rng.uniform(0, 1))
        x, y = (rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2))
        table = RobohiveObj(
            local_robohive_root=self.assets / "adapters/robohive",
            otype="furniture",
            asset_key="simpleTable/simpleWoodTable",
            pos=[0, 0, 0],
        )
        floor = TileFloor()
        box = Body(
            attributes=dict(name="box-1", pos=f"{x} {y} 0.8"),
            rgba=f"{r} {g} {b} 1.0",
            _children_raw="""
        <joint type="free" name="{name}"/>
        <geom name="box-1" type="box" size="0.015 0.015 0.015" mass="0.1" rgba="{rgba}" density="1000"/>
        """,
        )
        scene = Mjcf(
            WorldSettings("pastel"),
            LightingRig([0, 0, 0.8]),
            table,
            floor,
            box,
            FloatingRobotiq2f85(pos=[0, 0, 0.8]),
        )
        return scene

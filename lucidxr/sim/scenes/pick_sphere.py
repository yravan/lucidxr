"""Pick sphere: composed from the shared XML schema library."""

from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.objects.mj_sdf import MjSDF
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.floating_robotiq import FloatingRobotiq2f85
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.schema import Body, Mjcf
from lucidxr.sim.xml_schema.simple_components.table_slab import Table


class PickSphere(Scene):
    def build(self) -> Mjcf:
        rng = self.rng
        x1, y1 = (rng.uniform(-0.2, 0.2), rng.uniform(-0.5, -0.1))
        x2, y2 = (rng.uniform(-0.2, 0.2), rng.uniform(-0.5, -0.1))
        basket = MjSDF(pos=[0, 0.2, 0.67], assets="objects/black_basket", _attributes={"name": "basket"})
        table = Table(pos=[0, 0, 0.6], rgba="0.7 0.65 0.57 1")
        ball = Body(
            attributes=dict(name="ball-1", pos=f"{x1} {y1} 0.7"),
            _children_raw="""
        <joint type="free" name="{name}"/>
        <geom name="sphere-1" type="sphere" size="0.03" rgba="0.5 0.5 0.5 1" mass="0.1" solref="0.003 1" solimp="0.95 0.99 0.001" friction="2 0.01 0.002"/>
        """,
        )
        can = Body(
            attributes=dict(name="can-1", pos=f"{x2} {y2} 0.7"),
            _children_raw="""
        <joint type="free" name="{name}"/>
        <geom name="can-1" type="cylinder" size="0.03 0.05" rgba="0.5 0.5 0.5 1" mass="0.1" solref="0.003 1" solimp="0.95 0.99 0.001" friction="2 0.01 0.002"/>
        """,
        )
        ground = Body(
            attributes=dict(name="ground"),
            _children_raw="""
        <geom name="ground" type="plane" pos="0 0 0" size="10 10 0.1" rgba="0.2 0.3 0.4 1"/>
        """,
        )
        scene = Mjcf(
            WorldSettings("pastel"),
            LightingRig([0, 0, 0.8]),
            table,
            ball,
            can,
            basket,
            ground,
            FloatingRobotiq2f85(pos=[0, 0, 0.8]),
        )
        return scene

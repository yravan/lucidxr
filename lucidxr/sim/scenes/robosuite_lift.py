"""Robosuite lift: composed from the shared XML schema library."""

from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.adapters.robosuite.robosuite_tablearena import RobosuiteTableArena
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.floating_robotiq import FloatingRobotiq2f85
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.schema import Body, Mjcf


class RobosuiteLift(Scene):
    def build(self) -> Mjcf:
        options = dict(self.options)
        rng = self.rng
        r, g, b = (rng.uniform(0, 1), rng.uniform(0, 1), rng.uniform(0, 1))
        x, y = (rng.uniform(-0.5, 0.5), rng.uniform(-0.2, 0.2))
        arena = RobosuiteTableArena()
        box = Body(
            rgba=f"{r} {g} {b} 1.0",
            _attributes={"name": "box-1", "pos": f"{x} {y} 0.8"},
            _preamble="""
          <asset>
            <texture type="cube" name="cube_redwood" file="textures/red-wood.png"/>
            <material name="cube_redwood_mat" texture="cube_redwood" specular="0.4" shininess="0.1"/>
          </asset>
        """,
            _children_raw="""
          <joint name="{name}-cube_joint0" type="free" limited="false" actuatorfrclimited="false"/>
          <geom name="{name}-cube_g0" size="0.021556 0.0218909 0.02073" type="box" rgba="0.5 0 0 1"/>
          <geom name="{name}-cube_g0_vis" size="0.021556 0.0218909 0.02073" type="box" contype="0" conaffinity="0" group="1" mass="0" material="cube_redwood_mat"/>
          <site name="{name}-cube_default_site" pos="0 0 0" size="0.002" rgba="1 0 0 -1"/>
        """,
        )
        scene = Mjcf(
            WorldSettings("pastel"),
            LightingRig([0, 0, 0.8]),
            arena,
            box,
            FloatingRobotiq2f85(pos=[0, 0, 0.8], **options),
        )
        return scene

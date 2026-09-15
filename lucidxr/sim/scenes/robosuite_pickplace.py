"""Robosuite pickplace: composed from the shared XML schema library."""

from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.adapters.robosuite.robosuite_bin import RobosuiteBin
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.floating_robotiq import FloatingRobotiq2f85
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.schema import Body, Mjcf
from lucidxr.sim.xml_schema.simple_components.tile_floor import TileFloor


class RobosuitePickPlace(Scene):
    def build(self) -> Mjcf:
        options = dict(self.options)
        rng = self.rng
        r, g, b = (rng.uniform(0, 1), rng.uniform(0, 1), rng.uniform(0, 1))
        x1, y1 = (rng.uniform(0, 0.01), rng.uniform(-0.45, -0.4))
        x2, y2 = (rng.uniform(0.1, 0.101), rng.uniform(-0.35, -0.3))
        x3, y3 = (rng.uniform(0.15, 0.151), rng.uniform(-0.25, -0.2))
        x4, y4 = (rng.uniform(0.01, 0.2), rng.uniform(-0.15, -0.1))
        floor = TileFloor()
        bin1 = RobosuiteBin(attributes=dict(name="bin1", pos="0.1 -0.25 0.6"))
        bin2 = RobosuiteBin(attributes=dict(name="bin2", pos="0.1 0.28 0.6"))
        milk = Body(
            attributes=dict(name="milk-1", pos=f"{x1} {y1} 0.8"),
            rgba=f"{r} {g} {b} 1.0",
            _preamble="""
        <asset>
            <texture type="2d" name="Milk_tex-ceramic" file="textures/ceramic.png"/>
            <mesh name="Milk_milk_mesh" file="adapters/robosuite/meshes/milk.msh" scale="1.5 1.5 1.5"/>
            <material name="Milk_ceramic" texture="Milk_tex-ceramic" texuniform="true" reflectance="0.5"/>
        </asset>
        """,
            _children_raw="""
          <joint name="{name}-Milk_joint0" type="free" limited="false" actuatorfrclimited="false" damping="0.0005"/>
          <geom name="{name}-Milk_g0" type="mesh" mass="0.4" condim="4" friction="0.95 0.3 0.1" solref="0.001" solimp="0.998 0.998" density="100" rgba="0.5 0 0 1" mesh="Milk_milk_mesh"/>
          <geom name="{name}-Milk_g0_visual" type="mesh" contype="0" conaffinity="0" condim="4" group="1" friction="0.95 0.3 0.1" solref="0.001" solimp="0.998 0.998" mass="0" material="Milk_ceramic" mesh="Milk_milk_mesh"/>
          <site name="{name}-Milk_default_site" pos="0 0 0" size="0.002" rgba="1 0 0 0"/>
        """,
        )
        bread = Body(
            attributes=dict(name="bread-1", pos=f"{x2} {y2} 0.85"),
            rgba=f"{r} {g} {b} 1.0",
            _preamble="""
        <asset>
            <texture type="2d" name="Bread_tex-bread" file="textures/bread.png"/>
            <material name="Bread_bread" texture="Bread_tex-bread" texuniform="true" texrepeat="15 15" reflectance="0.7"/>
            <mesh name="Bread_bread_mesh" file="adapters/robosuite/meshes/bread.stl" scale="1.5 1.5 1.5"/>
        </asset>
        """,
            _children_raw="""
          <joint name="{name}-Bread_joint0" type="free" limited="false" actuatorfrclimited="false" damping="0.0005"/>
          <geom name="{name}-Bread_g0" type="mesh" mass="0.1" condim="4" friction="0.95 0.3 0.1" solref="0.001" solimp="0.998 0.998" density="50" rgba="0.5 0 0 1" mesh="Bread_bread_mesh"/>
          <geom name="{name}-Bread_g0_visual" type="mesh" contype="0" conaffinity="0" condim="4" group="1" friction="0.95 0.3 0.1" solref="0.001" solimp="0.998 0.998" mass="0" material="Bread_bread" mesh="Bread_bread_mesh"/>
          <site name="{name}-Bread_default_site" pos="0 0 0" size="0.002" rgba="1 0 0 0"/>
         """,
        )
        cereal = Body(
            attributes=dict(name="cereal-1", pos=f"{x3} {y3} 0.9"),
            rgba=f"{r} {g} {b} 1.0",
            _preamble="""
        <asset>
            <texture type="2d" name="Cereal_tex-cereal" file="textures/cereal.png"/>
            <material name="Cereal_cereal" texture="Cereal_tex-cereal" reflectance="0.5"/>
            <mesh name="Cereal_cereal_mesh" file="adapters/robosuite/meshes/cereal.msh" scale="1.5 1.5 1.5"/>
        </asset>
        """,
            _children_raw="""
          <joint name="{name}-Cereal_joint0" type="free" limited="false" actuatorfrclimited="false" damping="0.0005"/>
          <geom name="{name}-Cereal_g0" type="mesh" mass="0.4" condim="4" friction="0.95 0.3 0.1" solref="0.001" solimp="0.998 0.998" density="150" rgba="0.5 0 0 1" mesh="Cereal_cereal_mesh"/>
          <geom name="{name}-Cereal_g0_visual" type="mesh" contype="0" conaffinity="0" condim="4" group="1" friction="0.95 0.3 0.1" solref="0.001" solimp="0.998 0.998" mass="0" material="Cereal_cereal" mesh="Cereal_cereal_mesh"/>
          <site name="{name}-Cereal_default_site" pos="0 0 0" size="0.002" rgba="1 0 0 0"/>
        """,
        )
        can = Body(
            attributes=dict(name="can-1", pos=f"{x4} {y4} 0.86"),
            rgba=f"{r} {g} {b} 1.0",
            _preamble="""
        <asset>
            <texture type="2d" name="Can_tex-can" file="textures/soda.png"/>
            <material name="Can_coke" texture="Can_tex-can" texuniform="true" texrepeat="5 5" reflectance="0.7"/>
            <mesh name="Can_can_mesh" file="adapters/robosuite/meshes/can.msh" scale="1.25 1.25 1.25"/>
        </asset>
        """,
            _children_raw="""
          <joint name="{name}-Can_joint0" type="free" limited="false" actuatorfrclimited="false" damping="0.0005"/>
          <geom name="{name}-Can_g0" type="mesh" mass="0.3" condim="4" friction="0.95 0.3 0.1" solref="0.001" solimp="0.998 0.998" density="100" rgba="0.5 0 0 1" mesh="Can_can_mesh"/>
          <geom name="{name}-Can_g0_visual" type="mesh" contype="0" conaffinity="0" condim="4" group="1" friction="0.95 0.3 0.1" solref="0.001" solimp="0.998 0.998" mass="0" material="Can_coke" mesh="Can_can_mesh"/>
          <site name="{name}-Can_default_site" pos="0 0 0" size="0.002" rgba="1 0 0 0"/>
         """,
        )
        scene = Mjcf(
            WorldSettings("pastel"),
            LightingRig([0, 0, 0.8]),
            floor,
            bin1,
            bin2,
            milk,
            bread,
            cereal,
            can,
            FloatingRobotiq2f85(pos=[0, 0, 0.8], **options),
        )
        return scene

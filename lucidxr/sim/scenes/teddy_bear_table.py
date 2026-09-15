"""Teddy bear table: composed from the shared XML schema library."""

from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.scene_components.cameras.rig import make_camera_rig
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.floating_hands import FloatingShadowHand
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.scene_components.tables import OpticalTabletop
from lucidxr.sim.xml_schema.schema import Body, Mjcf


class TeddyBearTable(Scene):
    def build(self) -> Mjcf:
        workspace = OpticalTabletop()
        camera_rig = make_camera_rig(workspace.surface_origin)
        bear = Body(
            attributes=dict(name="bear", pos="0 0 0.85", quat="0.7071 0.7071 0.0 0.0"),
            _preamble="""
        <option solver="CG" tolerance="1e-6" timestep=".001" integrator="implicitfast"/>
        <size memory="100M"/>
        """,
            _children_raw="""
        <flexcomp name="bear" type="gmsh" file="objects/basic_teddy/low-poly_teddy_bear.msh" radius="0.005" dim="2" scale="0.01 0.01 0.01">
            <contact internal="false" selfcollide="none" /> 
            <edge equality="true" />
        </flexcomp>        
        """,
        )
        scene = Mjcf(
            WorldSettings("pastel"),
            LightingRig([0, 0, 0.8]),
            workspace,
            camera_rig.right_camera,
            camera_rig.right_camera_r,
            camera_rig.front_camera,
            camera_rig.top_camera,
            camera_rig.left_camera,
            camera_rig.back_camera,
            bear,
            FloatingShadowHand(pos=[0, 0, 0.8]),
        )
        return scene

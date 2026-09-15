"""Basketball shot: composed from the shared XML schema library."""

from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.objects.decomposed_obj import ObjMujocoObject
from lucidxr.sim.xml_schema.scene_components.cameras.rig_zoomed_out import make_camera_rig
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.floating_hands import FloatingShadowHand
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.scene_components.tables import OpticalTabletop
from lucidxr.sim.xml_schema.schema import Mjcf


class BasketballShot(Scene):
    def build(self) -> Mjcf:
        workspace = OpticalTabletop()
        camera_rig = make_camera_rig(workspace.surface_origin)
        basketball_hoop = ObjMujocoObject(
            name="basketball_hoop",
            assets="objects/basketball_hoop",
            prefix="hoop",
            visual_count=1,
            pos=[-0.7, 0, 0.85],
            quat=[0.7071068, 0.7071068, 0, 0],
            scale=0.5,
            collision_count=12,
            textures=["DefaultMaterial_baseColor"],
            free=False,
            randomize_colors=True,
            _additional_children_raw="""
        <site name="{prefix}_corner1" pos="0.425 0.45 -0.09" size="0.01" rgba="1 1 0 0"/>
        <site name="{prefix}_corner2" pos="0.605 0.45 -0.09" size="0.01" rgba="1 1 0 0"/>
        <site name="{prefix}_corner3" pos="0.605 0.45  0.09" size="0.01" rgba="1 1 0 0"/>
        <site name="{prefix}_corner4" pos="0.425 0.45  0.09" size="0.01" rgba="1 1 0 0"/>
        """,
        )
        basketball = ObjMujocoObject(
            name="basketball",
            assets="objects/basketball",
            visual_count=1,
            pos=[0, 0, 0.85],
            scale=0.0215,
            collision_count=1,
            textures=["Basketball_size6_baseColor"],
            randomize_colors=True,
            _additional_children_raw="""
        <site name="{name}" pos="0 0.07 0" size="0.0215" rgba="1 1 0 0"/>
        """,
        )
        scene = Mjcf(
            WorldSettings("pastel"),
            LightingRig([0, 0, 0.8]),
            workspace,
            *camera_rig.get_cameras(),
            basketball_hoop,
            basketball,
            FloatingShadowHand(pos=[0, 0, 0.8]),
        )
        return scene

"""Poncho table: composed from the shared XML schema library."""

from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.objects.poncho import Poncho
from lucidxr.sim.xml_schema.scene_components.cameras.rig import make_camera_rig
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.floating_hands import FloatingShadowHand
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.scene_components.tables import OpticalTabletop
from lucidxr.sim.xml_schema.schema import Mjcf


class PonchoTable(Scene):
    def build(self) -> Mjcf:
        workspace = OpticalTabletop()
        asset_directory = self.assets
        camera_rig = make_camera_rig(workspace.surface_origin)
        poncho = Poncho(
            asset_directory=asset_directory, pos=[0.3, 0, 0.9], name="poncho", rgba="0.3 0.3 1 1", scale=0.3
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
            poncho,
            FloatingShadowHand(pos=[0, 0, 0.8]),
        )
        scene._preamble = '<option integrator="discrete"/>'
        return scene

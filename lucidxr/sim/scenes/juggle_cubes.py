"""Juggle cubes: composed from the shared XML schema library."""

from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.objects.cube import Cube
from lucidxr.sim.xml_schema.scene_components.cameras.rig import make_camera_rig
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.floating_hands import FloatingDexHand
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.scene_components.tables import OpticalTabletop
from lucidxr.sim.xml_schema.schema import Mjcf


class JuggleCubes(Scene):
    def build(self) -> Mjcf:
        workspace = OpticalTabletop()
        camera_rig = make_camera_rig(workspace.surface_origin)
        cubes = [
            Cube(name=f"box-{i}", pos=(x, 0, 0.9), rgba=color)
            for i, (x, color) in enumerate(((-0.1, "1 0 0 1"), (0, "0 1 0 1"), (0.1, "0 0 1 1")), 1)
        ]
        scene = Mjcf(
            WorldSettings("dexterous"),
            LightingRig([-0.5, 0, 0.8]),
            *cubes,
            workspace,
            camera_rig.right_camera,
            camera_rig.right_camera_r,
            camera_rig.front_camera,
            camera_rig.top_camera,
            camera_rig.left_camera,
            camera_rig.back_camera,
            FloatingDexHand(pos=[-0.5, 0, 0.8], bimanual=False),
        )
        return scene

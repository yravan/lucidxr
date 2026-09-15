"""Particle sweep: composed from the shared XML schema library."""

from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.objects.bin import Bin
from lucidxr.sim.xml_schema.objects.cup import Cup
from lucidxr.sim.xml_schema.scene_components.cameras.rig import make_camera_rig
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.floating_hands import FloatingShadowHand
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.scene_components.tables import OpticalTabletop
from lucidxr.sim.xml_schema.schema import Mjcf
from lucidxr.sim.xml_schema.simple_components.particles import particle_grid


class ParticleSweep(Scene):
    def build(self) -> Mjcf:
        workspace = OpticalTabletop()
        camera_rig = make_camera_rig(workspace.surface_origin)
        cup = Cup(
            assets="rooms/kitchen/cup",
            pos=[0.3, 0, 0.87],
            name="cup",
            scale=0.1,
            collision_count=32,
            randomize_colors=False,
        )
        bin = Bin(attributes=dict(name="bin", pos="0 0 0.8"))
        particles = particle_grid()
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
            bin,
            particles,
            cup,
            FloatingShadowHand(pos=[0, 0, 0.8]),
        )
        return scene

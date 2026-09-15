"""Flip mug: composed from the shared XML schema library."""

from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.scene_components.cameras.rig_hand import make_camera_rig
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.floating_hands import FloatingShadowHand
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.schema import Mjcf
from lucidxr.sim.xml_schema.simple_components.concrete_slab import ConcreteSlab
from lucidxr.sim.xml_schema.simple_components.force_plate import ForcePlate
from lucidxr.sim.xml_schema.transforms.mujoco import Vector3


class FlipMug(Scene):
    def build(self) -> Mjcf:
        from lucidxr.sim.xml_schema.objects.vuer_mug import VuerMug

        table = ConcreteSlab(pos=[0, 0, 0.6], rgba="0.8 0.8 0.8 1", roughness="0.2")
        rig_origin = table.surface_origin + Vector3(x=-0.55, y=0, z=0)
        camera_rig = make_camera_rig(rig_origin)
        mug = VuerMug(pos=[0, -0.1, 0.8], quat=[0, 0, 1, 0])
        work_area = ForcePlate(
            name="start-area",
            pos=(0, 0, 0.6052),
            quat=(0, 1, 0, 0),
            type="box",
            size="0.35 0.35 0.005",
            rgba="0.5 0 0 1.0",
        )
        scene = Mjcf(
            WorldSettings("pastel"),
            LightingRig([0, 0, 0.8]),
            mug,
            table,
            work_area,
            *camera_rig.get_cameras(),
            FloatingShadowHand(bimanual=False, camera_rig=camera_rig, pos=[0, 0, 0.8]),
        )
        return scene

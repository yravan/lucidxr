"""Mug drawer: composed from the shared XML schema library."""

from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.objects.mimicgen_drawer import MimicGenDrawer
from lucidxr.sim.xml_schema.objects.vuer_mug import VuerMug
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.floating_robotiq import FloatingRobotiq2f85
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.schema import Mjcf
from lucidxr.sim.xml_schema.simple_components.concrete_slab import ConcreteSlab


class MugDrawer(Scene):
    def build(self) -> Mjcf:
        table = ConcreteSlab(pos=[0, 0, 0.6], rgba="0.8 0.8 0.8 1", roughness="0.2")
        drawer = MimicGenDrawer(pos=[0.1, 0, 0.63], quat=[1, 0, 0, 0])
        mug = VuerMug(pos=[-0.2, -0.3, 0.65], quat=[0, 0, 1, 0])
        scene = Mjcf(
            WorldSettings("pastel"),
            LightingRig([0, 0, 0.8]),
            drawer,
            mug,
            table,
            FloatingRobotiq2f85(pos=[0, 0, 0.8]),
        )
        return scene

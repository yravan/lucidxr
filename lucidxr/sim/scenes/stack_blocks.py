"""Stack blocks: composed from the shared XML schema library."""

from lucidxr.sim.scenes._sampling import random_quat
from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.objects.block import StackingBlock
from lucidxr.sim.xml_schema.scene_components.cameras.rig import make_camera_rig
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.floating_robotiq import FloatingRobotiq2f85
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.scene_components.tables import Tabletop
from lucidxr.sim.xml_schema.schema import Mjcf


class StackBlocks(Scene):
    def build(self) -> Mjcf:
        options = dict(self.options)
        rng = self.rng
        x1, y1 = (rng.uniform(-0.4, 0.4), rng.uniform(-0.2, 0.2))
        x2, y2 = (rng.uniform(-0.4, 0.4), rng.uniform(-0.2, 0.2))
        quat1 = random_quat(rng)
        q1 = f"{quat1[0]} 0 0 {quat1[3]}"
        table = Tabletop()
        camera_rig = make_camera_rig([-0.5, 0, 0.6])
        box_1 = StackingBlock(
            attributes=dict(name="box-1", pos=f"{x1} {y1} 0.8", quat=q1), rgba="0 1 0 1.0", top_rgba="0 0 1 1"
        )
        box_2 = StackingBlock(
            attributes=dict(name="box-2", pos=f"{x2} {y2} 0.8"), rgba="1 0 0 1.0", top_rgba="0 1 1 1"
        )
        scene = Mjcf(
            WorldSettings("pastel"),
            LightingRig([0, 0, 0.8]),
            *camera_rig.get_cameras(),
            table,
            box_1,
            box_2,
            FloatingRobotiq2f85(pos=[0, 0, 0.8], **options),
        )
        return scene

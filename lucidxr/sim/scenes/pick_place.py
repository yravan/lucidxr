"""Pick place: composed from the shared XML schema library."""

from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.scene_components.cameras.rig import make_camera_rig
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.floating_robotiq import FloatingRobotiq2f85
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.schema import Body, Mjcf
from lucidxr.sim.xml_schema.simple_components.concrete_slab import ConcreteSlab
from lucidxr.sim.xml_schema.simple_components.force_plate import ForcePlate
from lucidxr.sim.xml_schema.transforms.mujoco import Vector3


class PickPlace(Scene):
    def build(self) -> Mjcf:
        table = ConcreteSlab(pos=[0, 0, 0.6], rgba="0.8 0.8 0.8 1")
        box = Body(
            pos=(0, 0.24, 0.7),
            attributes=dict(name="box-1"),
            _children_raw="""
        <joint type="free" name="{name}"/>
        <geom name="box-1" type="box" pos="0 0.0 0.0"  rgba="0 1 0 1" size="0.025 0.025 0.025" density="1000"/>
        <site name="box-1" pos="0 0.0 0.0" size="0.025"/>
        """,
        )
        start_area = ForcePlate(
            name="start-area",
            pos=(0, 0.24, 0.6052),
            quat=(0, 1, 0, 0),
            type="box",
            size="0.2 0.2 0.005",
            rgba="1 0 0 1",
        )
        rig_origin = table.surface_origin + Vector3(x=-0.55, y=0, z=0)
        camera_rig = make_camera_rig(rig_origin)
        goal_area = ForcePlate(
            name="goal-area",
            pos=(0, -0.24, 0.6052),
            quat=(0, 1, 0, 0),
            type="box",
            size="0.2 0.2 0.005",
            rgba="0.137 0.667 1. 1.",
        )
        scene = Mjcf(
            WorldSettings("pastel"),
            LightingRig([0, 0, 0.8]),
            table,
            start_area,
            goal_area,
            box,
            *camera_rig.get_cameras(),
            FloatingRobotiq2f85(pos=[0, 0, 0.8]),
        )
        return scene

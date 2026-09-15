"""Move plate: composed from the shared XML schema library."""

from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.objects.bigym_dishdrainer import BigymDishDrainer
from lucidxr.sim.xml_schema.objects.bigym_plate import BigymPlate
from lucidxr.sim.xml_schema.objects.bigym_table import BigymTable
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.floating_robotiq import FloatingRobotiq2f85
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.schema import Mjcf
from lucidxr.sim.xml_schema.simple_components.mj_ground_plane import GroundPlane


class MovePlate(Scene):
    def build(self) -> Mjcf:
        ground = GroundPlane()
        table = BigymTable(pos=[0.7, 0, 0], quat=[0.7071, 0, 0, -0.7071])
        drainer1 = BigymDishDrainer(
            pos=[0.7, 0.3, 0.95], quat=[1, 0, 0, 0], prefix="drainer1", _attributes={"name": "drainer1"}
        )
        drainer2 = BigymDishDrainer(
            pos=[0.7, -0.3, 0.95], quat=[1, 0, 0, 0], prefix="drainer2", _attributes={"name": "drainer2"}
        )
        plate = BigymPlate(
            pos=[0.7, -0.18, 1.1],
            quat=[0.7071, 0.7071, 0, 0],
            prefix="plate1",
            _attributes={"name": "plate1"},
        )
        scene = Mjcf(
            WorldSettings("pastel"),
            LightingRig([0, 0, 0.8]),
            ground,
            table,
            drainer1,
            drainer2,
            plate,
            FloatingRobotiq2f85(pos=[0, 0, 0.8]),
        )
        return scene

"""Kitchen room: composed from the shared XML schema library."""

import numpy as np

from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.objects.bowl import Bowl
from lucidxr.sim.xml_schema.objects.cup import Cup
from lucidxr.sim.xml_schema.scene_components.cameras.rig import make_camera_rig
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.floating_robotiq import FloatingRobotiq2f85
from lucidxr.sim.xml_schema.scene_components.rooms.kitchen import KitchenLayout
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.schema import Mjcf


class KitchenRoom(Scene):
    def build(self) -> Mjcf:
        import lucidxr.sim.xml_schema.transforms.mujoco as m

        origin = m.Vector3(-1, -1, 0)
        quat = m.WXYZ(0.7071068, 0, 0, -0.7071068)
        bowl_pos = list(np.array([-0.4, -1.25, 1]) - origin)
        bowl = Bowl(assets="rooms/kitchen/bowl", collision_count=32, scale=0.2, pos=bowl_pos, name="bowl")
        cup_pos = list(np.array([-0.4, -1.45, 1.3]) - origin)
        cup = Cup(
            assets="rooms/kitchen/cup", pos=cup_pos, name="cup", collision_count=32, randomize_colors=False
        )
        cameras = make_camera_rig(pos=[0.1, -0.15, 1])
        scene = Mjcf(
            WorldSettings("pastel"),
            LightingRig([0.6, -0.15, 1.1]),
            KitchenLayout(pos=-1 * origin, quat=quat),
            bowl,
            cup,
            *cameras.get_cameras(),
            FloatingRobotiq2f85(pos=[0.6, -0.15, 1.1]),
        )
        return scene

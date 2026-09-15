"""Pour liquid: composed from the shared XML schema library."""

import numpy as np

import lucidxr.sim.xml_schema.transforms.mujoco as m
from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.objects.bowl import Bowl
from lucidxr.sim.xml_schema.objects.cup import Cup
from lucidxr.sim.xml_schema.objects.fixtures.dishwasher import KitchenDishwasher
from lucidxr.sim.xml_schema.objects.fixtures.drawer_stack import DrawerStack
from lucidxr.sim.xml_schema.objects.fixtures.granite_countertop import GraniteCountertop
from lucidxr.sim.xml_schema.objects.fixtures.room_wall import RoomWall
from lucidxr.sim.xml_schema.objects.fixtures.sink_wide import KitchenSinkWide
from lucidxr.sim.xml_schema.objects.mug import ObjaverseMujocoMug
from lucidxr.sim.xml_schema.objects.spoon_7 import ObjaverseMujocoSpoon
from lucidxr.sim.xml_schema.scene_components.cameras.rig import make_camera_rig
from lucidxr.sim.xml_schema.scene_components.cameras.rig_stereo import make_origin_stereo_rig
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.floating_hands import FloatingShadowHand
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.schema import Body, Mjcf, Replicate


class PourLiquid(Scene):
    def build(self) -> Mjcf:
        x1, y1 = (0.2, -1)
        origin = m.Vector3(0, 0, 0)
        nx, ny, nz = (2, 2, 6)
        quat = m.WXYZ(0.7071068, 0, 0, -0.7071068)
        front_wall = RoomWall(
            panel_sz=(1.8, 0.5425, 0.02),
            pos=(0.65, 0.02, 0.5425),
            quat=(-0.707107, 0.707107, 0, 0),
            name="wall_room",
            assets="rooms/kitchen/wall",
            backing=False,
        )
        stack_B = DrawerStack(base_pos="0.51 -0.3 0.00", name="stack_B", assets="rooms/kitchen", visual=True)
        stack_C = DrawerStack(base_pos="1.02 -0.3 0.00", name="stack_C", assets="rooms/kitchen", visual=True)
        table_A = GraniteCountertop(
            assets="rooms/kitchen/counter",
            size="0.35 0.325 0.015",
            attributes={"pos": "0.075 -0.325 0.905", "name": "table_A"},
        )
        table_B = GraniteCountertop(
            assets="rooms/kitchen/counter",
            size="0.36 0.0345 0.015",
            attributes={"pos": "0.77 -0.616 0.905", "name": "table_B"},
        )
        table_C = GraniteCountertop(
            assets="rooms/kitchen/counter",
            size="0.36 0.0345 0.015",
            attributes={"pos": "0.77 -0.01 0.905", "name": "table_C"},
        )
        table_D = GraniteCountertop(
            assets="rooms/kitchen/counter",
            size="0.35 0.325 0.015",
            attributes={"pos": "1.41 -0.325 0.905", "name": "table_D"},
        )
        countertop = GraniteCountertop(
            assets="rooms/kitchen/counter",
            size="1.06 0.325 0.015",
            attributes={"pos": "0.75 0.325 1.1", "name": "countertop"},
        )
        sink = KitchenSinkWide(assets="rooms/kitchen/sink_wide", attributes={"pos": "0.75 -0.31 0.94"})
        dw = KitchenDishwasher(
            assets="rooms/kitchen/dishwasher",
            attributes={"pos": "-0.1 -0.075 0.00", "name": "dishwasher", "childclass": "dw"},
        )
        dw2 = KitchenDishwasher(
            assets="rooms/kitchen/dishwasher",
            prefix="dw2",
            attributes={"pos": "1.6 -0.075 0.00", "name": "dishwasher2", "childclass": "dw"},
        )
        mug_pos = list(np.array([-0.4, -1.25, 1]) - origin)
        mug = ObjaverseMujocoMug(assets="rooms/kitchen/mug", pos=mug_pos, collision_count=32, visual_count=2)
        bowl_pos = list(np.array([-0.2, -1.25, 1]) - origin)
        bowl = Bowl(assets="rooms/kitchen/bowl", collision_count=32, scale=0.2, pos=bowl_pos, name="bowl")
        spoon_pos = list(np.array([-0.4, -1.45, 1.2]) - origin)
        spoon = ObjaverseMujocoSpoon(
            assets="rooms/kitchen/spoon",
            pos=spoon_pos,
            name="spoon",
            scale=0.3,
            collision_count=32,
            randomize_colors=False,
        )
        cup_pos = list(np.array([x1, y1, 1.2]) - origin)
        cup = Cup(
            assets="rooms/kitchen/cup", pos=cup_pos, name="cup", collision_count=32, randomize_colors=False
        )
        particles_pos = list(np.array([x1 - 0.01, y1 - 0.01, 1.18]) - origin)
        particles = Replicate(
            Replicate(
                Replicate(
                    Body(
                        pos=particles_pos,
                        _attributes={"name": "particle"},
                        _children_raw="""
                            <freejoint/>
                            <geom size=".007" rgba=".8 .2 .1 1" condim="1" solref="0.001 1" solimp="0.99 0.99 0.001"/>
                        """,
                    ),
                    _attributes=dict(count=nz, offset="0.0 0.0 0.014"),
                ),
                _attributes=dict(count=ny, offset="0.0 0.014 0.0"),
            ),
            _attributes=dict(count=nx, offset="0.014 0.0 0.0"),
        )
        cameras = make_camera_rig(pos=[x1 - 0.6, y1, 1.2])
        stereo_cameras = make_origin_stereo_rig(pos=[x1 - 0.8, y1, 1.0])
        scene = Mjcf(
            WorldSettings("pastel"),
            LightingRig([-0.8, -1.15, 1.1]),
            Body(
                front_wall,
                stack_B,
                stack_C,
                table_A,
                table_B,
                table_C,
                table_D,
                countertop,
                sink,
                dw,
                dw2,
                attributes=dict(name="room", pos=-1 * origin, quat=quat),
            ),
            mug,
            bowl,
            spoon,
            cup,
            particles,
            *cameras.get_cameras(),
            *stereo_cameras.get_cameras(),
            FloatingShadowHand(pos=[-0.8, -1.15, 1.1]),
        )
        return scene

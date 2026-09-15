"""Microwave muffin: composed from the shared XML schema library."""

import lucidxr.sim.xml_schema.transforms.mujoco as m
from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.objects.fixtures.cabinet import KitchenCabinet
from lucidxr.sim.xml_schema.objects.fixtures.cupcake import Cupcake
from lucidxr.sim.xml_schema.objects.fixtures.dishwasher import KitchenDishwasher
from lucidxr.sim.xml_schema.objects.fixtures.drawer_stack import DrawerStack
from lucidxr.sim.xml_schema.objects.fixtures.granite_countertop import GraniteCountertop
from lucidxr.sim.xml_schema.objects.fixtures.microwave_scaled import KitchenMicrowave
from lucidxr.sim.xml_schema.objects.fixtures.room_wall import RoomWall
from lucidxr.sim.xml_schema.objects.vuer_mug import VuerMug
from lucidxr.sim.xml_schema.scene_components.cameras.rig_lower_fov import make_camera_rig
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.floating_robotiq import FloatingRobotiq2f85
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.schema import Body, Mjcf


class MicrowaveMuffin(Scene):
    def build(self) -> Mjcf:
        options = dict(self.options)
        mode = options.pop("mode", "production")
        origin = m.Vector3(-0.7, -0.2, 0.2)
        quat = m.WXYZ(0.7071068, 0, 0, -0.7071068)
        front_wall = RoomWall(
            panel_sz=(1.1, 1.6, 0.02),
            pos=(0.035, 0.02, 0.89),
            quat=(-0.707107, 0.707107, 0, 0),
            name="wall_room",
            assets="rooms/kitchen/wall",
            backing=False,
        )
        side_wall = RoomWall(
            panel_sz=(0.02, 1.6, 1.385),
            pos=(-1.005, -1.385, 0.89),
            quat=(-0.707107, 0.707107, 0, 0),
            name="wall_room_side",
            assets="rooms/kitchen/wall",
            backing=False,
        )
        start_indicator = Body(
            pos=(-0.2, 0.1, 0.8),
            attributes=dict(name="start_indicator-1"),
            _children_raw="""
        <site name="start_indicator-1" pos="0 0.0 0.0" size="0.025"/>
        """,
        )
        table_A = GraniteCountertop(
            assets="rooms/kitchen/counter",
            size="1.06 0.325 0.015",
            attributes={"pos": "0.075 -0.325 0.905", "name": "table_A"},
        )
        table_B = GraniteCountertop(
            assets="rooms/kitchen/counter",
            size="0.325 1.06 0.015",
            attributes={"pos": "-0.66 -1.71 0.905", "name": "table_B"},
        )
        cameras = make_camera_rig(pos=[-1, 0.1, 1])
        microwave = KitchenMicrowave(pos=[0.035, -0.3, 1.09], quat=[1, 0, 0, 0])
        cabinet_B = KitchenCabinet(
            assets="rooms/kitchen/cabinet",
            attributes={"pos": "0.5 -0.20 2.0", "name": "cabinet_B"},
            remove_joints=True,
        )
        mug = VuerMug(
            pos=[0.45, -0.3, 0.8],
            quat=[0, 0, 0, 1],
            scale="0.0186 0.0284 0.0186",
            _attributes={"name": "mug"},
            remove_joints=True,
        )
        cupcake = Cupcake(pos=[0.4, 0.225, 0.82], scale="0.05 0.05 0.05")
        dw = KitchenDishwasher(
            assets="rooms/kitchen/dishwasher",
            attributes={"pos": "-0.27 -0.075 0.00", "name": "dishwasher", "childclass": "dw"},
            remove_joints=True,
        )
        stack_D = DrawerStack(
            base_pos="0.3 -0.3 0.00", name="stack_D", assets="rooms/kitchen", remove_joints=True
        )
        stack_E = DrawerStack(
            base_pos="0.81 -0.3 0.00", name="stack_E", assets="rooms/kitchen", remove_joints=True
        )
        if mode == "production":
            extra_children = [
                Body(
                    dw,
                    stack_D,
                    stack_E,
                    cabinet_B,
                    attributes=dict(name="furniture", pos=-1 * origin, quat=quat),
                    remove_joints=True,
                ),
                mug,
            ]
            extra_extra_children = [front_wall, side_wall]
        else:
            extra_extra_children = []
            extra_children = []
        scene = Mjcf(
            WorldSettings("pastel"),
            LightingRig([-0.2, 0.1, 0.8]),
            Body(
                *extra_extra_children,
                table_A,
                table_B,
                microwave,
                attributes=dict(name="room", pos=-1 * origin, quat=quat),
            ),
            start_indicator,
            cupcake,
            *extra_children,
            *cameras.get_cameras(),
            FloatingRobotiq2f85(camera_rig=cameras, pos=[-0.2, 0.1, 0.8]),
        )
        return scene

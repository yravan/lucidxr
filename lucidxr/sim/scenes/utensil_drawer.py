"""Utensil drawer: composed from the shared XML schema library."""

import lucidxr.sim.xml_schema.transforms.mujoco as m
from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.objects.bagel import Bagel
from lucidxr.sim.xml_schema.objects.bowl import Bowl
from lucidxr.sim.xml_schema.objects.cup import Cup
from lucidxr.sim.xml_schema.objects.fixtures.cabinet import KitchenCabinet
from lucidxr.sim.xml_schema.objects.fixtures.cupcake import Cupcake
from lucidxr.sim.xml_schema.objects.fixtures.dishwasher import KitchenDishwasher
from lucidxr.sim.xml_schema.objects.fixtures.drawer_stack import DrawerStack
from lucidxr.sim.xml_schema.objects.fixtures.granite_countertop import GraniteCountertop
from lucidxr.sim.xml_schema.objects.fixtures.room_wall import RoomWall
from lucidxr.sim.xml_schema.objects.spoon_7 import ObjaverseMujocoSpoon
from lucidxr.sim.xml_schema.objects.vuer_mug import VuerMug
from lucidxr.sim.xml_schema.scene_components.cameras.rig_lower_fov import make_camera_rig
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.floating_robotiq import FloatingRobotiq2f85
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.schema import Body, Mjcf


class UtensilDrawer(Scene):
    def build(self) -> Mjcf:
        options = dict(self.options)
        mode = options.pop("mode", "production")
        origin = m.Vector3(-0.7, -0.2, 0)
        quat = m.WXYZ(0.7071068, 0, 0, -0.7071068)
        front_wall = RoomWall(
            panel_sz=(2.1, 1.6, 0.02),
            pos=(0.035, 0.02, 0.89),
            quat=(-0.707107, 0.707107, 0, 0),
            name="wall_room",
            assets="rooms/kitchen/wall",
            backing=False,
        )
        cup = Cup(
            assets="rooms/kitchen/cup_4",
            pos=[0.3, 0, 1.0],
            name="cup",
            collision_count=32,
            randomize_colors=False,
        )
        spoon = ObjaverseMujocoSpoon(
            assets="rooms/kitchen/spoon",
            pos=[0.3, 0, 1.1],
            quat=[0, 1, 0, 0],
            name="spoon",
            collision_count=32,
            randomize_colors=False,
        )
        mug = VuerMug(
            pos=[0.5, -0.15, 0.95], quat=[1, 0, 0, 0], _attributes={"name": "mug"}, remove_joints=True
        )
        cupcake = Cupcake(pos=[0.4, 0.225, 0.82], scale="0.05 0.05 0.05", remove_joints=True)
        start_indicator = Body(
            pos=(-0.2, 0.1, 0.8),
            attributes=dict(name="start_indicator-1"),
            _children_raw="""
        <site name="start_indicator-1" pos="0 0.0 0.0" size="0.025"/>
        """,
        )
        table_A = GraniteCountertop(
            assets="rooms/kitchen/counter",
            size="2 0.325 0.015",
            attributes={"pos": "0.075 -0.325 0.905", "name": "table_A"},
        )
        stack_D = DrawerStack(base_pos="-0.2 -0.3 0.00", name="stack_D", assets="rooms/kitchen")
        stack_E = DrawerStack(base_pos="0.31 -0.3 0.00", name="stack_E", assets="rooms/kitchen")
        cabinet_A = KitchenCabinet(
            assets="rooms/kitchen/cabinet",
            attributes={"pos": "-0.77 -0.20 2.0", "name": "cabinet_A"},
            remove_joints=True,
        )
        cabinet_B = KitchenCabinet(
            assets="rooms/kitchen/cabinet",
            attributes={"pos": "0.88 -0.20 2.0", "name": "cabinet_B"},
            remove_joints=True,
        )
        cameras = make_camera_rig(pos=[-1.25, -0.1, 1.1])
        bagel = Bagel(attributes={"pos": "0.5 0.3 0.95", "name": "bagel"}, remove_joints=True)
        bowl = Bowl(
            assets="rooms/kitchen/bowl",
            collision_count=32,
            scale=0.2,
            pos=[0.3, 0.4, 0.95],
            name="bowl",
            remove_joints=True,
        )
        dw = KitchenDishwasher(
            assets="rooms/kitchen/dishwasher",
            attributes={"pos": "0.88 -0.075 0.00", "name": "dishwasher", "childclass": "dw"},
            remove_joints=True,
        )
        extra_children = []
        if mode == "production":
            extra_children = [dw, cabinet_A, cabinet_B]
        scene = Mjcf(
            WorldSettings("pastel"),
            LightingRig([-0.3, 0, 0.95]),
            Body(
                front_wall,
                table_A,
                stack_D,
                stack_E,
                *extra_children,
                attributes=dict(name="room", pos=-1 * origin, quat=quat),
            ),
            cup,
            spoon,
            bagel,
            mug,
            cupcake,
            bowl,
            start_indicator,
            *cameras.get_cameras(),
            FloatingRobotiq2f85(camera_rig=cameras, pos=[-0.3, 0, 0.95]),
        )
        return scene

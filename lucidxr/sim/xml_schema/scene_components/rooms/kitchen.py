from lucidxr.sim.xml_schema.objects.fixtures.cabinet import KitchenCabinet
from lucidxr.sim.xml_schema.objects.fixtures.drawer_stack import DrawerStack
from lucidxr.sim.xml_schema.objects.fixtures.granite_countertop import GraniteCountertop
from lucidxr.sim.xml_schema.objects.fixtures.room_wall import RoomWall
from lucidxr.sim.xml_schema.objects.fixtures.sink_wide import KitchenSinkWide
from lucidxr.sim.xml_schema.schema import Body


class KitchenLayout(Body):
    """Kitchen counter, drawers, cabinet, sink and wall as a reusable room body."""

    def __init__(self, *, name="room", pos=(0, 0, 0), quat=(1, 0, 0, 0)):
        front_wall = RoomWall(
            panel_sz=(2.3, 1.5, 0.02),
            pos=(1.15, 0.02, 1.5),
            quat=(-0.707107, 0.707107, 0, 0),
            name="wall_room",
            assets="rooms/kitchen/wall",
            backing=False,
        )
        cabinet_A = KitchenCabinet(
            assets="rooms/kitchen/cabinet", attributes={"pos": "-0.3 -0.20 2.0", "name": "cabinet_A"}
        )
        stack_A = DrawerStack(base_pos="-0.75 -0.3 0.00", name="stack_A", assets="rooms/kitchen")
        stack_B = DrawerStack(base_pos="0.51 -0.3 0.00", name="stack_B", assets="rooms/kitchen", visual=True)
        stack_C = DrawerStack(base_pos="1.02 -0.3 0.00", name="stack_C", assets="rooms/kitchen", visual=True)
        stack_D = DrawerStack(base_pos="1.53 -0.3 0.00", name="stack_D", assets="rooms/kitchen")
        stack_E = DrawerStack(base_pos="2.04 -0.3 0.00", name="stack_E", assets="rooms/kitchen")
        table_A = GraniteCountertop(
            assets="rooms/kitchen/counter",
            size="0.72 0.325 0.015",
            attributes={"pos": "-0.285 -0.325 0.905", "name": "table_A"},
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
            size="0.71 0.325 0.015",
            attributes={"pos": "1.77 -0.325 0.905", "name": "table_D"},
        )
        sink = KitchenSinkWide(assets="rooms/kitchen/sink_wide", attributes={"pos": "0.75 -0.31 0.94"})
        super().__init__(
            front_wall,
            cabinet_A,
            stack_A,
            stack_B,
            stack_C,
            stack_D,
            stack_E,
            table_A,
            table_B,
            table_C,
            table_D,
            sink,
            name=name,
            pos=pos,
            quat=quat,
        )

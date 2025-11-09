from vuer_mujoco.schemas.room_xmls.room_components.granite_countertop import GraniteCountertop
from vuer_mujoco.schemas.room_xmls.room_components.sink_wide import KitchenSinkWide
from vuer_mujoco.schemas.room_xmls.room_components.cabinet import KitchenCabinet
from vuer_mujoco.schemas.room_xmls.room_components.oven import KitchenOven
from vuer_mujoco.schemas.room_xmls.room_components.microwave import KitchenMicrowave
from vuer_mujoco.schemas.room_xmls.room_components.drawer_stack import DrawerStack
from vuer_mujoco.schemas.room_xmls.room_components.room_wall import RoomWall
from vuer_mujoco.schemas.room_xmls.room_components.dishwasher import KitchenDishwasher
from vuer_mujoco.schemas.room_xmls.room_components.refrigerator import KitchenFridge

from vuer_mujoco.schemas.utils import Save
from vuer_mujoco import DefaultStage
from vuer_mujoco.schemas.schema import Body


# Generate random values for r, g, and b
# r, g, b = random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)


def make_scene():
    from vuer_mujoco import Prettify
    front_wall = RoomWall(
        panel_sz=(2.3, 1.50, 0.02),
        pos=(1.15, 0.02, 1.5),
        quat=(-0.707107, 0.707107, 0, 0),
        name="wall_room",
        assets="assets/wall",
        backing=False,                      # generates the 10 cm backing slab
    )
    right_wall = RoomWall(
        panel_sz=(1.4, 1.50, 0.02),
        pos=(3.15, -1.2, 1.5),
        quat=(0.5, -0.5, -0.5, 0.5),
        name="right_wall_room",
        assets="assets/wall",
        backing=False,                      # generates the 10 cm backing slab
    )

    cabinet_A = KitchenCabinet(assets="assets/cabinet", attributes={"pos": "-0.3 -0.20 2.0", "name":"cabinet_A"})
    cabinet_B = KitchenCabinet(assets="assets/cabinet", attributes={"pos": "2.0 -0.20 2.0", "name":"cabinet_B"})
    cabinet_C = KitchenCabinet(assets="assets/cabinet", attributes={"pos": "2.91031 -0.65 2.0", "name":"cabinet_C", "quat":"0.7071068 0 0 -0.7071068"})
    
    stack_A = DrawerStack(base_pos="-0.75 -0.3 0.00", name="stack_A")
    stack_B = DrawerStack(base_pos="0.51 -0.3 0.00", name="stack_B", visual=True) 
    stack_C = DrawerStack(base_pos="1.02 -0.3 0.00", name="stack_C", visual=True)
    stack_D = DrawerStack(base_pos="1.53 -0.3 0.00", name="stack_D")
    stack_E = DrawerStack(base_pos="2.04 -0.3 0.00", name="stack_E")
    corner_box = Body(
            attributes=dict(name="corner_box", pos="2.7 -0.3 0.45"),
            _children_raw="""
                <geom name="corner_box_geom"
                      type="box" size="0.4 0.275 0.45"
                      density="1000"
                      material="single-cabinet_body_mat"/>
            """,
        )

    table_A = GraniteCountertop(assets="assets/counter", size="0.72 0.325 0.015", attributes={"pos": "-0.285 -0.325 0.905", "name":"table_A"})
    table_B = GraniteCountertop(assets="assets/counter", size="0.36 0.0345 0.015", attributes={"pos": "0.77 -0.616 0.905", "name":"table_B"})
    table_C = GraniteCountertop(assets="assets/counter", size="0.36 0.0345 0.015", attributes={"pos": "0.77 -0.01 0.905", "name":"table_C"})
    table_D = GraniteCountertop(assets="assets/counter", size="0.71 0.325 0.015", attributes={"pos": "1.77 -0.325 0.905", "name":"table_D"})
    table_E = GraniteCountertop(assets="assets/counter", size="0.575 0.325 0.015", attributes={"pos": "2.8 -0.575 0.905", "name":"table_E", "quat":"0.7071068 0 0 -0.7071068"})
    table_F = GraniteCountertop(assets="assets/counter", size="0.26 0.325 0.015", attributes={"pos": "2.8 -2.175 0.905", "name":"table_F", "quat":"0.7071068 0 0 -0.7071068"})

    sink = KitchenSinkWide(assets="assets/sink_wide", attributes={"pos": "0.75 -0.31 0.94"})
    stack_F = DrawerStack(base_pos= "2.85 -0.9 0", name="stack_F", base_quat="0.707105 0 0 -0.707108")
    oven = KitchenOven(assets="assets/oven", attributes={"pos": "2.796 -1.534 0.6404", "name":"oven", "quat":"0.707105 0 0 -0.707108"})
    microwave = KitchenMicrowave(assets="assets/microwave", attributes={"pos": "2.91031 -1.534 1.59586", "name":"microwave", "quat":"0.707105 0 0 -0.707108"})
    stack_G = DrawerStack(base_pos= "2.85 -2.17 0", name="stack_G", base_quat="0.707105 0 0 -0.707108")

    dw = KitchenDishwasher(assets="assets/dishwasher", attributes={"pos": "-0.1 -0.075 0.00", "name":"dishwasher", "childclass": "dw"})
    fridge = KitchenFridge(assets="assets/fridge", attributes={"pos": "-1.4 -0.45 0.95"})

    scene = DefaultStage(front_wall, right_wall, cabinet_A, cabinet_B, cabinet_C, stack_A, stack_B, stack_C, stack_D, stack_E, corner_box, table_A, table_B, table_C, table_D, table_E, table_F, sink, stack_F, stack_G, oven, microwave, dw, fridge, model="Kitchen")


    return scene._xml | Prettify()

if __name__ == "__main__":
    make_scene() | Save(__file__.replace(".py", ".mjcf.xml"))

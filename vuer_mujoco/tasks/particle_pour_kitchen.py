from pathlib import Path

import numpy as np

from vuer_mujoco.schemas.objects.bowl_0 import ObjaverseMujocoBowl
from vuer_mujoco.schemas.objects.cup_3 import ObjaverseMujocoCup
from vuer_mujoco.schemas.objects.mug import ObjaverseMujocoMug
from vuer_mujoco.schemas.objects.plate import ObjaverseMujoco
from vuer_mujoco.schemas.objects.spoon_7 import ObjaverseMujocoSpoon
from vuer_mujoco.schemas.room_xmls.room_components.cabinet import KitchenCabinet
from vuer_mujoco.schemas.room_xmls.room_components.dishwasher import KitchenDishwasher
from vuer_mujoco.schemas.room_xmls.room_components.drawer_stack import DrawerStack
from vuer_mujoco.schemas.room_xmls.room_components.granite_countertop import GraniteCountertop
from vuer_mujoco.schemas.room_xmls.room_components.microwave import KitchenMicrowave
from vuer_mujoco.schemas.room_xmls.room_components.oven import KitchenOven
from vuer_mujoco.schemas.room_xmls.room_components.refrigerator import KitchenFridge
from vuer_mujoco.schemas.room_xmls.room_components.room_wall import RoomWall
from vuer_mujoco.schemas.room_xmls.room_components.sink_wide import KitchenSinkWide
from vuer_mujoco.schemas.schema import Body, Replicate
from vuer_mujoco.tasks import add_env
from vuer_mujoco.tasks.base.lucidxr_task import get_site
from vuer_mujoco.tasks.base.mocap_task import MocapTask
from vuer_mujoco.schemas.components.rigs.camera_rig import make_camera_rig
from vuer_mujoco.tasks._floating_robotiq import FloatingRobotiq2f85
from vuer_mujoco.tasks._floating_shadowhand import FloatingShadowHand
from vuer_mujoco.schemas.schema import Composite
from vuer_mujoco.tasks.entrypoint import make_env

# Generate random values for r, g, and b
# r, g, b = random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)


def make_schema():
    import vuer_mujoco.schemas.se3.se3_mujoco as m
    from vuer_mujoco.schemas.utils.file import Prettify

    origin = m.Vector3(-1, -1, 0)
    quat = m.WXYZ(0.7071068, 0, 0, -0.7071068)

    front_wall = RoomWall(
        panel_sz=(2.3, 1.50, 0.02),
        pos=(1.15, 0.02, 1.5),
        quat=(-0.707107, 0.707107, 0, 0),
        name="wall_room",
        assets="kitchen/wall",
        backing=False,
    )
    right_wall = RoomWall(
        panel_sz=(1.4, 1.50, 0.02),
        pos=(3.15, -1.2, 1.5),
        quat=(0.5, -0.5, -0.5, 0.5),
        name="right_wall_room",
        assets="kitchen/wall",
        backing=False,
    )

    cabinet_A = KitchenCabinet(assets="kitchen/cabinet", attributes={"pos": "-0.3 -0.20 2.0", "name": "cabinet_A"})
    cabinet_B = KitchenCabinet(assets="kitchen/cabinet", attributes={"pos": "2.0 -0.20 2.0", "name": "cabinet_B"})
    cabinet_C = KitchenCabinet(
        assets="kitchen/cabinet", attributes={"pos": "2.91031 -0.65 2.0", "name": "cabinet_C", "quat": "0.7071068 0 0 -0.7071068"}
    )

    stack_A = DrawerStack(base_pos="-0.75 -0.3 0.00", name="stack_A", assets="kitchen")
    stack_B = DrawerStack(base_pos="0.51 -0.3 0.00", name="stack_B", assets="kitchen", visual=True)
    stack_C = DrawerStack(base_pos="1.02 -0.3 0.00", name="stack_C", assets="kitchen", visual=True)
    stack_D = DrawerStack(base_pos="1.53 -0.3 0.00", name="stack_D", assets="kitchen")
    stack_E = DrawerStack(base_pos="2.04 -0.3 0.00", name="stack_E", assets="kitchen")
    corner_box = Body(
        attributes=dict(name="corner_box", pos="2.7 -0.3 0.45"),
        _children_raw="""
                <geom name="corner_box_geom"
                      type="box" size="0.4 0.275 0.45"
                      density="1000"
                      material="single-cabinet_body_mat"/>
            """,
    )

    table_A = GraniteCountertop(
        assets="kitchen/counter", size="0.72 0.325 0.015", attributes={"pos": "-0.285 -0.325 0.905", "name": "table_A"}
    )
    table_B = GraniteCountertop(
        assets="kitchen/counter", size="0.36 0.0345 0.015", attributes={"pos": "0.77 -0.616 0.905", "name": "table_B"}
    )
    table_C = GraniteCountertop(
        assets="kitchen/counter", size="0.36 0.0345 0.015", attributes={"pos": "0.77 -0.01 0.905", "name": "table_C"}
    )
    table_D = GraniteCountertop(
        assets="kitchen/counter", size="0.71 0.325 0.015", attributes={"pos": "1.77 -0.325 0.905", "name": "table_D"}
    )
    table_E = GraniteCountertop(
        assets="kitchen/counter",
        size="0.575 0.325 0.015",
        attributes={"pos": "2.8 -0.575 0.905", "name": "table_E", "quat": "0.7071068 0 0 -0.7071068"},
    )
    table_F = GraniteCountertop(
        assets="kitchen/counter",
        size="0.26 0.325 0.015",
        attributes={"pos": "2.8 -2.175 0.905", "name": "table_F", "quat": "0.7071068 0 0 -0.7071068"},
    )

    sink = KitchenSinkWide(assets="kitchen/sink_wide", attributes={"pos": "0.75 -0.31 0.94"})
    stack_F = DrawerStack(base_pos="2.85 -0.9 0", name="stack_F", base_quat="0.707105 0 0 -0.707108", assets="kitchen")
    oven = KitchenOven(assets="kitchen/oven", attributes={"pos": "2.796 -1.534 0.6404", "name": "oven", "quat": "0.707105 0 0 -0.707108"})
    microwave = KitchenMicrowave(
        assets="kitchen/microwave", attributes={"pos": "2.91031 -1.534 1.59586", "name": "microwave", "quat": "0.707105 0 0 -0.707108"}
    )
    stack_G = DrawerStack(base_pos="2.85 -2.17 0", name="stack_G", base_quat="0.707105 0 0 -0.707108", assets="kitchen")

    dw = KitchenDishwasher(assets="kitchen/dishwasher", attributes={"pos": "-0.1 -0.075 0.00", "name": "dishwasher", "childclass": "dw"})
    fridge = KitchenFridge(assets="kitchen/fridge", attributes={"pos": "-1.4 -0.45 0.95"})

    cup_pos = list(np.array([-0.4, -1.25, 1.0]) - origin)
    # cup = Body(
    #     pos=cup_pos,
    #     _children_raw="""
    #                 <freejoint/>
    #                 !-- Bottom -->
    #                 <!-- Bottom -->
    #                 <geom type="cylinder" size="0.035 0.002" pos="0 0 0.002" rgba="0.7 0.5 0.3 1"/>
    #
    #                   <!-- Walls: 8 boxes, 7cm long, 2mm thick, 15cm tall -->
    #                   <!-- half-height 7.5cm = 0.075m -->
    #                   <!-- wall thickness 0.002m -->
    #                   <!-- wall length 0.035m (radius) -->
    #                   <!-- placed on circle of radius 0.035m -->
    #
    #                   <!-- wall 1 -->
    #                   <geom type="box" size="0.015 0.002 0.075" pos="0.035 0 0.075" euler="0 0 1.5708" rgba="0.7 0.5 0.3 1"/>
    #                   <!-- wall 2 -->
    #                   <geom type="box" size="0.015 0.002 0.075" pos="0.0247 0.0247 0.075" euler="0 0 2.3562" rgba="0.7 0.5 0.3 1"/>
    #                   <!-- wall 3 -->
    #                   <geom type="box" size="0.015 0.002 0.075" pos="0 0.035 0.075" euler="0 0 3.1416" rgba="0.7 0.5 0.3 1"/>
    #                   <!-- wall 4 -->
    #                   <geom type="box" size="0.015 0.002 0.075" pos="-0.0247 0.0247 0.075" euler="0 0 3.9269" rgba="0.7 0.5 0.3 1"/>
    #                   <!-- wall 5 -->
    #                   <geom type="box" size="0.015 0.002 0.075" pos="-0.035 0 0.075" euler="0 0 4.7124" rgba="0.7 0.5 0.3 1"/>
    #                   <!-- wall 6 -->
    #                   <geom type="box" size="0.015 0.002 0.075" pos="-0.0247 -0.0247 0.075" euler="0 0 5.4978" rgba="0.7 0.5 0.3 1"/>
    #                   <!-- wall 7 -->
    #                   <geom type="box" size="0.015 0.002 0.075" pos="0 -0.035 0.075" euler="0 0 6.2832" rgba="0.7 0.5 0.3 1"/>
    #                   <!-- wall 8 -->
    #                   <geom type="box" size="0.015 0.002 0.075" pos="0.0247 -0.0247 0.075" euler="0 0 0.7854" rgba="0.7 0.5 0.3 1"/>
    #         """
    # )
    cup = ObjaverseMujocoCup(assets="kitchen/cup", pos=cup_pos, name="cup", collision_count=32, randomize_colors=False)
    # plate_pos = list(np.array([-0.2, -1.25, 0.95]) - origin)
    # plate = ObjaverseMujoco(assets="kitchen/plate", pos=plate_pos, name="plate", collision_count=32, randomize_colors=False)

    particles_pos = list(np.array([-0.41, -1.26, 1.01]) - origin)
    particles = Replicate(
        Replicate(
            Replicate(
                Body(
                    pos=particles_pos,
                    _children_raw="""
                                <freejoint/>
                                <geom size=".008" rgba=".8 .2 .1 1" condim="1"/>
                            """,

                ),
                _attributes=dict(
                    count=9,
                    offset="0.0 0.0 0.01",
                )
            ),
            _attributes=dict(
                count=3,
                offset="0.0 0.01 0.0",
            ),
        ),
        _attributes=dict(
            count=3,
            offset="0.01 0.0 0.0",
        )
    )

    cameras = make_camera_rig(pos=[0.1, -0.15, 1])

    # scene = FloatingShadowHand(
    scene = FloatingShadowHand(
        Body(
            front_wall,
            right_wall,
            cabinet_A,
            cabinet_B,
            cabinet_C,
            stack_A,
            stack_B,
            stack_C,
            stack_D,
            stack_E,
            corner_box,
            table_A,
            table_B,
            table_C,
            table_D,
            table_E,
            table_F,
            sink,
            stack_F,
            stack_G,
            oven,
            microwave,
            dw,
            fridge,
            attributes=dict(name="room", pos=-1 * origin, quat=quat),
        ),
        cup,
        # plate,
        particles,
        *cameras.get_cameras(),
        pos=[0.2, -0.15, 1.1],
        # dual_gripper=True,
    )

    return scene._xml | Prettify()

def register():
    add_env(
        env_id="Particle_pour_kitchen-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=MocapTask,
            camera_names=["right", "left", "front"],
            xml_path="particle_pour_kitchen.mjcf.xml",
            workdir=Path(__file__).parent,
            mode="multiview",
        ),
    )


if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Save

    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

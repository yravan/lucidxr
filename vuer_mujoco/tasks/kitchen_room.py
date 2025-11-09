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
from vuer_mujoco.schemas.schema import Body
from vuer_mujoco.tasks import add_env
from vuer_mujoco.tasks.base.lucidxr_task import get_site
from vuer_mujoco.tasks.base.mocap_task import MocapTask
from vuer_mujoco.schemas.components.rigs.camera_rig import make_camera_rig
from vuer_mujoco.tasks._floating_robotiq import FloatingRobotiq2f85
from vuer_mujoco.tasks.entrypoint import make_env

# Generate random values for r, g, and b
# r, g, b = random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)


def make_schema(mode="cameraready", robot="panda", show_robot=False, **options):
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

    fridge = KitchenFridge(assets="kitchen/fridge", attributes={"pos": "-1.4 -0.45 0.95"})

    plate = ObjaverseMujoco(assets="kitchen/plate", pos=[0, -0.5, 0.95], name="plate", collision_count=32, randomize_colors=False)
    mug_pos = list(np.array([-0.4, -1.25, 1]) - origin)
    mug = ObjaverseMujocoMug(assets="kitchen/mug", pos=mug_pos, collision_count=32, visual_count=2)
    bowl_pos = list(np.array([-0.4, -1.25, 1]) - origin)
    bowl = ObjaverseMujocoBowl(assets="kitchen/bowl", collision_count=32, scale=0.2, pos=bowl_pos, name="bowl")
    spoon_pos = list(np.array([-0.4, -1.45, 1.3]) - origin)
    spoon = ObjaverseMujocoSpoon(assets="kitchen/spoon", pos=spoon_pos, name="spoon", scale=0.3, collision_count=32, randomize_colors=False)
    cup_pos = list(np.array([-0.4, -1.45, 1.3]) - origin)
    cup = ObjaverseMujocoCup(assets="kitchen/cup", pos=cup_pos, name="cup", collision_count=32, randomize_colors=False)

    cameras = make_camera_rig(pos=[0.1, -0.15, 1])

    # scene = FloatingShadowHand(
    scene = FloatingRobotiq2f85(
        Body(
            front_wall,
            # right_wall,
            cabinet_A,
            # cabinet_B,
            # cabinet_C,
            stack_A,
            stack_B,
            stack_C,
            stack_D,
            stack_E,
            # corner_box,
            table_A,
            table_B,
            table_C,
            table_D,
            # table_E,
            # table_F,
            sink,
            # stack_F,
            # stack_G,
            # oven,
            # microwave,
            # dw,
            # fridge,
            attributes=dict(name="room", pos=-1 * origin, quat=quat),
        ),
        bowl,
        cup,
        *cameras.get_cameras(),
        pos=[0.6, -0.15, 1.1],
        # dual_gripper=True,
    )

    return scene._xml | Prettify()


class CleanSink(MocapTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.first_goal = False
        self.second_goal = False
        self.cup_site = get_site(self.physics, "cup")
        self.bowl_site = get_site(self.physics, "bowl")
        self.sink_sites = [get_site(self.physics, f"sink-wide_corner_{i}") for i in range(1, 9)]
        self.gripper_site = get_site(self.physics, "gripper-pinch")

    def get_reward(self, physics):
        reward = 0.0
        cup_pos = physics.data.site_xpos[self.cup_site.id]
        bowl_pos = physics.data.site_xpos[self.bowl_site.id]
        if np.linalg.norm(cup_pos - bowl_pos) < 0.05:
            self.first_goal = True

        # Get positions of the 8 corner sites
        corner_positions = np.array([physics.data.site_xpos[site.id] for site in self.sink_sites])

        # Compute bounding box
        min_corner = np.min(corner_positions, axis=0)  # [x_min, y_min, z_min]
        max_corner = np.max(corner_positions, axis=0)  # [x_max, y_max, z_max]

        # Optional small margin (e.g., for numerical robustness)
        margin = 0.005
        min_corner -= margin
        max_corner += margin

        # Check if cup is inside bounding box
        cup_inside = np.all((cup_pos >= min_corner) & (cup_pos <= max_corner))
        bowl_inside = np.all((bowl_pos >= min_corner) & (bowl_pos <= max_corner))

        if cup_inside and bowl_inside:
            self.second_goal = True

        if self.first_goal and self.second_goal:
            # Check if the gripper is not in the sink
            gripper_pos = physics.data.site_xpos[self.gripper_site.id]
            gripper_inside = np.all((gripper_pos >= min_corner) & (gripper_pos <= max_corner))
            if not gripper_inside:
                reward = 1.0

        return reward


def register():
    add_env(
        env_id="KitchenRoom-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=CleanSink,
            camera_names=["right", "left", "wrist"],
            xml_path="kitchen_room.mjcf.xml",
            workdir=Path(__file__).parent,
            mode="multiview",
        ),
    )
    add_env(
        env_id="KitchenRoom-lucid-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=CleanSink,
            camera_names=["right", "right_r", "wrist"],
            xml_path="kitchen_room.mjcf.xml",
            workdir=Path(__file__).parent,
            mode="lucid",
            object_keys=["bowl", "cup"],
        ),
    )


if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Save

    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

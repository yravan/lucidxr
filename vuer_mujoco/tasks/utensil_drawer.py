import os
from pathlib import Path
import random
from copy import copy
import numpy as np

from vuer_mujoco.schemas.lucid_xr.objects.bagel import Bagel
from vuer_mujoco.schemas.room_xmls.room_components.cabinet import KitchenCabinet
from vuer_mujoco.schemas.room_xmls.room_components.drawer_stack import DrawerStack
from vuer_mujoco.schemas.objects.bowl_0 import ObjaverseMujocoBowl
from vuer_mujoco.schemas.objects.cup_3 import ObjaverseMujocoCup
from vuer_mujoco.schemas.objects.spoon_7 import ObjaverseMujocoSpoon
from vuer_mujoco.schemas.objects.mj_sdf import MjSDF
from vuer_mujoco.schemas.objects.mug import ObjaverseMujocoMug
from vuer_mujoco.schemas.objects.plate import ObjaverseMujoco
from vuer_mujoco.schemas.objects.spoon_7 import ObjaverseMujocoSpoon
from vuer_mujoco.schemas.room_xmls.room_components.cupcake import Cupcake
from vuer_mujoco.schemas.room_xmls.room_components.dishwasher import KitchenDishwasher
from vuer_mujoco.schemas.room_xmls.room_components.drawer_stack import DrawerStack
from vuer_mujoco.schemas.room_xmls.room_components.granite_countertop import GraniteCountertop
from vuer_mujoco.schemas.room_xmls.room_components.refrigerator import KitchenFridge
from vuer_mujoco.schemas.room_xmls.room_components.room_wall import RoomWall
from vuer_mujoco.schemas.room_xmls.room_components.sink_wide import KitchenSinkWide
from vuer_mujoco.schemas.schema import Body, Replicate
from vuer_mujoco.tasks import add_env
from vuer_mujoco.tasks.base.lucidxr_task import get_site, init_states
from vuer_mujoco.tasks.base.mocap_task import MocapTask
from vuer_mujoco.schemas.components.rigs.camera_rig_lower_fov import make_camera_rig
from vuer_mujoco.tasks._floating_shadowhand import FloatingShadowHand
from vuer_mujoco.tasks.entrypoint import make_env
import vuer_mujoco.schemas.se3.se3_mujoco as m
from vuer_mujoco.schemas.room_xmls.room_components.microwave_scaled import KitchenMicrowave
from vuer_mujoco.schemas.objects.vuer_mug import VuerMug
from vuer_mujoco.schemas.objects.cup_3 import ObjaverseMujocoCup
from vuer_mujoco.tasks._floating_robotiq import FloatingRobotiq2f85


x1, y1 = 0.2, -1
origin = m.Vector3(-0.7, -0.2, 0)


def make_schema(mode="production",**kwargs):
    from vuer_mujoco.schemas.utils.file import Prettify

    quat = m.WXYZ(0.7071068, 0, 0, -0.7071068)


    front_wall = RoomWall(
        panel_sz=(2.1, 1.6, 0.02),
        pos=(0.035, 0.02, 0.89),
        quat=(-0.707107, 0.707107, 0, 0),
        name="wall_room",
        assets="kitchen/wall",
        backing=False,
    )
    cup = ObjaverseMujocoCup(assets="kitchen/cup_4", pos=[0.3, 0, 1.0], name="cup", collision_count=32, randomize_colors=False)
    spoon = ObjaverseMujocoSpoon(assets="kitchen/spoon", pos=[0.3, 0, 1.1], quat=[0, 1, 0, 0], name="spoon", collision_count=32, randomize_colors=False)

    side_wall = RoomWall(
        panel_sz=(0.02, 1.6, 1.385),
        pos=(-1.005, -1.385, 0.89),
        quat=(-0.707107, 0.707107, 0, 0),
        name="wall_room_side",
        assets="kitchen/wall",
        backing=False,
    )
    mug = VuerMug(
        pos=[0.5, -0.15, 0.95],
        quat=[1, 0, 0, 0],
        _attributes={
            "name": "mug",
        },
        remove_joints=True,
    )

    cupcake = Cupcake(
        pos=[0.4, 0.225, 0.82],
        scale="0.05 0.05 0.05",
        remove_joints=True,
    )
    
    start_indicator = Body(
        pos=(-0.2, 0.1, 0.8),
        attributes=dict(name="start_indicator-1"),
        _children_raw="""
        <site name="start_indicator-1" pos="0 0.0 0.0" size="0.025"/>
        """,
    )

    table_A = GraniteCountertop(
        assets="kitchen/counter", size="2 0.325 0.015", attributes={"pos": "0.075 -0.325 0.905", "name": "table_A"}
    )

    stack_D = DrawerStack(base_pos="-0.2 -0.3 0.00", name="stack_D", assets="kitchen")
    stack_E = DrawerStack(base_pos="0.31 -0.3 0.00", name="stack_E", assets="kitchen")

    cabinet_A = KitchenCabinet(assets="kitchen/cabinet", attributes={"pos": "-0.77 -0.20 2.0", "name": "cabinet_A"}, remove_joints=True)
    cabinet_B = KitchenCabinet(assets="kitchen/cabinet", attributes={"pos": "0.88 -0.20 2.0", "name": "cabinet_B"}, remove_joints=True)

    cameras = make_camera_rig(pos=[-1.25, -0.1, 1.1])

    microwave = KitchenMicrowave(pos=[0.8, -0.3, 1.09],
                                 quat=[1, 0, 0, 0], remove_joints=True)

    bagel = Bagel( attributes={"pos": "0.5 0.3 0.95", "name": "bagel"}, remove_joints=True)
    bowl = ObjaverseMujocoBowl(assets="kitchen/bowl", collision_count=32, scale=0.2, pos=[0.3, 0.4, 0.95], name="bowl", remove_joints=True)

    dw = KitchenDishwasher(assets="kitchen/dishwasher", attributes={"pos": "0.88 -0.075 0.00", "name": "dishwasher", "childclass": "dw"}, remove_joints=True)
    dw2 = KitchenDishwasher(
        assets="kitchen/dishwasher", prefix="dw2", attributes={"pos": "0.88 -0.075 0.00", "name": "dishwasher2", "childclass": "dw"}, remove_joints=True
    )

    extra_children = []
    if mode == "production":
        extra_children = [
            dw,
            cabinet_A,
            cabinet_B,
        ]

    # scene = FloatingShadowHand(
    scene = FloatingRobotiq2f85(
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
        camera_rig=cameras,
        pos=[-0.3, 0, 0.95],
        # quat=[0, 0, 0, 1],
        # dual_gripper=True,
    )

    return scene._xml | Prettify()

class Fixed(MocapTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_sites()
        
    def set_sites(self):
        self.spoon_site = get_site(self.physics, "spoon")
        self.drawer_site = get_site(self.physics, "stack_E")
        
    def get_reward(self, physics):
        stack_e_hinge = physics.named.data.qpos["stack_E_drawer_slide"]
        
        drawer_closed = (abs(stack_e_hinge) < 0.15)
        drawer_site = physics.data.site_xpos[self.drawer_site.id]
        spoon_site = physics.data.site_xpos[self.spoon_site.id]
        
        z_dist = drawer_site[2] - spoon_site[2]
        z_success = 0.1 > z_dist > -0.005

        return float(z_success and drawer_closed)

class Random(Fixed):
    cup_qpos_addr = 4
    spoon_qpos_addr = 11
    
    d = 0.02
    xy_limits = [-0.15, 0.08], [-0.15, 0.08]
    xy_reject = None
    yaw_limits = (-np.pi, np.pi)  # ← add a range for yaw
    initial_pos = [0.3, 0, 1.0]

    xy_poses = init_states(xy_limits, d, xy_reject)
    print(f"Length: {len(xy_poses)}")
    pose_buffer = None

    @classmethod
    def random_state(
        cls,
        qpos=None,
        quat=None,
        addr=None,
        index=None,
        mocap_pos=None,
        **kwargs,
    ):
        if index is None:
            if not cls.pose_buffer:
                cls.pose_buffer = copy(cls.xy_poses)
                random.shuffle(cls.pose_buffer)

            x, y = cls.pose_buffer.pop(0)
            print(f"Randomly selected pose: {x}, {y}")
        else:
            x, y = cls.xy_poses[index]

        new_qpos = qpos.copy()
        new_qpos[cls.cup_qpos_addr] = cls.initial_pos[0] + x
        new_qpos[cls.cup_qpos_addr + 1] = cls.initial_pos[1] + y
        new_qpos[cls.cup_qpos_addr + 2] = cls.initial_pos[2]

        new_qpos[cls.spoon_qpos_addr] = cls.initial_pos[0] + x + np.random.normal(0.0, 0.005)
        new_qpos[cls.spoon_qpos_addr + 1] = cls.initial_pos[1] + y + np.random.normal(0.0, 0.005)
        new_qpos[cls.spoon_qpos_addr + 2] = cls.initial_pos[2] + 0.1
        new_qpos[cls.spoon_qpos_addr + 3:cls.spoon_qpos_addr + 7] = [0, 1, 0, 0]

        # Optional Gaussian noise on mocap
        if mocap_pos is not None:
            mocap_pos = mocap_pos.copy()
            mocap_pos += np.random.normal(0.0, 0.005, mocap_pos.shape)

        return dict(qpos=new_qpos, quat=quat, mocap_pos=mocap_pos, **kwargs)


def register(strict=False):
    add_env(
        env_id="UtensilDrawer-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=Fixed,
            xml_renderer=make_schema,
            camera_names=["front", "front_r", "wrist"],
            workdir=Path(__file__).parent,
            mode="multiview",
        ),
        strict=strict,
    )

    add_env(
        env_id="UtensilDrawer-Random-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=Random,
            xml_renderer=make_schema,
            camera_names=["front", "front_r", "wrist"],
            workdir=Path(__file__).parent,
            mode="multiview",
            keyframe_file="utensil_drawer.frame.yaml"
        ),
        strict=strict,
    )
    add_env(
        env_id="UtensilDrawer-Random-lucid-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=Random,
            xml_renderer=make_schema,
            camera_names=["front", "front_r", "wrist"],
            workdir=Path(__file__).parent,
            mode="lucid",
            keyframe_file="utensil_drawer.frame.yaml",
            object_keys=["cup", "spoon"],
        ),
        strict=strict,
    )


    add_env(
        env_id="UtensilDrawer-Random-gsplat-cic_11th_stationary",
        entrypoint=make_env,
        kwargs=dict(
            task=Random,
            xml_renderer=make_schema,
            camera_names=["front", "front_r", "wrist"],
            workdir=Path(__file__).parent,
            keyframe_file="utensil_drawer.frame.yaml",
            mode="gsplat",
            gsplat_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_11th_stationary",
            transform_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/utensil_drawer/cic_11th_stationary",
            invisible_prefix=["spoon", "cup", "stack_E","stack_D", "gripper"],
        ),
        strict=strict,
    )
    add_env(
        env_id="UtensilDrawer-Random-gsplat-cic_11th_kitchen_back",
        entrypoint=make_env,
        kwargs=dict(
            task=Random,
            xml_renderer=make_schema,
            camera_names=["front", "front_r", "wrist"],
            workdir=Path(__file__).parent,
            keyframe_file="utensil_drawer.frame.yaml",
            mode="gsplat",
            gsplat_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_11th_kitchen_back",
            transform_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/utensil_drawer/cic_11th_kitchen_back",
            invisible_prefix=["spoon", "cup", "stack_E","stack_D", "gripper"],
        ),
        strict=strict,
    )
    add_env(
        env_id="UtensilDrawer-Random-gsplat-cic_kitchen_4th_night",
        entrypoint=make_env,
        kwargs=dict(
            task=Random,
            xml_renderer=make_schema,
            camera_names=["front", "front_r", "wrist"],
            workdir=Path(__file__).parent,
            keyframe_file="utensil_drawer.frame.yaml",
            mode="gsplat",
            gsplat_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_kitchen_4th_night",
            transform_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/utensil_drawer/cic_kitchen_4th_night",
            invisible_prefix=["spoon", "cup", "stack_E","stack_D", "gripper"],
        ),
        strict=strict,
    )



if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Save

    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))
    
    # from vuer_mujoco.tasks import make
    # env = make("UtensilDrawer-Random-v1")
    # env.unwrapped.env.physics.named.data.qpos
    # env.reset()
    #
    # env.get_ordi()

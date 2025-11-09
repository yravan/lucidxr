import random
from copy import copy
from pathlib import Path



import numpy as np

from vuer_mujoco.schemas.components.rigs.camera_rig import make_camera_rig
from vuer_mujoco.schemas.se3.se3_mujoco import Vector3
from vuer_mujoco.schemas.utils.file import Save
from vuer_mujoco.schemas.schema import Body
from vuer_mujoco.tasks import add_env
from vuer_mujoco.schemas.components.concrete_slab import ConcreteSlab
from vuer_mujoco.tasks._floating_robotiq import FloatingRobotiq2f85
from vuer_mujoco.tasks._floating_shadowhand import FloatingShadowHand
from vuer_mujoco.schemas.components.force_plate import ForcePlate
from vuer_mujoco.tasks.base.lucidxr_task import get_geom_id, get_site, init_states
from vuer_mujoco.tasks.base.mocap_task import MocapTask
from vuer_mujoco.tasks.entrypoint import make_env


def make_schema(**_):
    from vuer_mujoco.schemas.utils.file import Prettify

    table = ConcreteSlab(pos=[0, 0, 0.6], rgba="0.8 0.8 0.8 1")
    box = Body(
        pos=(0, 0.24, 0.7),
        attributes=dict(name="box-1"),
        _children_raw="""
        <joint type="free" name="{name}"/>
        <geom name="box-1" type="box" pos="0 0.0 0.0"  rgba="0 1 0 1" size="0.025 0.025 0.025" density="1000"/>
        <site name="box-1" pos="0 0.0 0.0" size="0.025"/>
        """,
    )

    start_area = ForcePlate(
        name="start-area",
        pos=(0, 0.24, 0.6052),
        quat=(0, 1, 0, 0),
        type="box",
        size="0.2 0.2 0.005",
        rgba="1 0 0 1",
    )

    rig_origin = table.surface_origin + Vector3(x=-0.55, y=0, z=0)
    camera_rig = make_camera_rig(rig_origin)

    print(table.surface_origin, type(table.surface_origin))

    goal_area = ForcePlate(
        name="goal-area",
        pos=(0, -0.24, 0.6052),
        quat=(0, 1, 0, 0),
        type="box",
        size="0.2 0.2 0.005",
        rgba="0.137 0.667 1. 1.",
    )

    # scene = FloatingRobotiq2f85(
    #     table,
    #     start_area,
    #     goal_area,
    #     box,
    #     *camera_rig.get_cameras(),
    #     pos=[0, 0, 0.8],
    # )

    scene = FloatingShadowHand(
        table,
        start_area,
        goal_area,
        box,
        *camera_rig.get_cameras(),
        bimanual=False,
        pos=[-0.3, -0.15, 0.4],
    )

    xml = scene._xml | Prettify()

    # model = mujoco.MjModel.from_xml_string(xml)
    #
    # new_data = mujoco.MjData(model).copy()
    #
    # new_data.qpos[7:14] = [-0.5, .15, 1.1, 0, 0.707, 00, 0.707] # set hand to init pos
    #
    # mujoco.mj_forward(modle, new_data)


    return xml


class Fixed(MocapTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.box_site = None
        self.start_area_site = None
        self.goal_area_site = None
        # self.gripper_site = None
        self.set_sites()

        all_geom_names = [f"{self.physics.model.geom(i).name}_{i}" for i in range(self.physics.model.ngeom)]
        self.geom_name2id = {name: i for i, name in enumerate(all_geom_names)}

    def set_sites(self):
        self.box_site = get_site(self.physics, "box-1")
        self.start_area_site = get_site(self.physics, "start-area")
        self.goal_area_site = get_site(self.physics, "goal-area")
        # self.gripper_site = get_site(self.physics, "")

        self.box_geom_id = get_geom_id(self.physics, "box-1")
        self.goal_geom_id = get_geom_id(self.physics, "goal-area")

    def get_reward(self, physics):
        reward = 0.0

        for i in range(physics.data.ncon):
            contact = physics.data.contact[i]
            contact_geoms = [contact.geom1, contact.geom2]
            if self.box_geom_id in contact_geoms and self.goal_geom_id in contact_geoms:
                reward = 1.0

        return reward


class BlockRandom(Fixed):
    box_qpos_addr = 0
    d = 0.05
    xy_limits = [-0.15, 0.15], [-0.15, 0.15]
    xy_reject = None
    yaw_limits = (-np.pi, np.pi)  # ← add a range for yaw
    initial_pos = [0, 0.24, 0.7]

    xy_poses = init_states(xy_limits, d, xy_reject)
    print(f"Length: {len(xy_poses)}")
    pose_buffer = None

    @classmethod
    def random_state(
        cls,
        qpos=None,
        quat=None,
        addr=box_qpos_addr,
        index=None,
        mocap_pos=None,
        **kwargs,
    ):
        # if index is None:
        #     if not cls.pose_buffer:
        #         cls.pose_buffer = copy(cls.xy_poses)
        #         random.shuffle(cls.pose_buffer)
        #
        #     x, y = cls.pose_buffer.pop(0)
        #     print(f"Randomly selected pose: {x}, {y}")
        # else:
        #     x, y = cls.xy_poses[index]
        #
        new_qpos = qpos.copy()
        # new_qpos[addr] = cls.initial_pos[0] + x
        # new_qpos[addr + 1] = cls.initial_pos[1] + y
        # new_qpos[addr + 2] = cls.initial_pos[2]

        # -------------------- yaw randomisation --------------------
        yaw = random.uniform(*cls.yaw_limits)
        new_qpos[addr + 3] = np.cos(yaw / 2.0)   # qw
        new_qpos[addr + 4] = 0.0                 # qx
        new_qpos[addr + 5] = 0.0                 # qy
        new_qpos[addr + 6] = np.sin(yaw / 2.0)   # qz
        # -----------------------------------------------------------

        # preserve or overwrite the explicit `quat` argument
        quat = new_qpos[addr + 3 : addr + 7].copy()

        # Optional Gaussian noise on mocap
        if mocap_pos is not None:
            mocap_pos = mocap_pos.copy()
            mocap_pos += np.random.normal(0.0, 0.005, mocap_pos.shape)

        return dict(qpos=new_qpos, quat=quat, mocap_pos=mocap_pos, **kwargs)


class BlockRandomMore(BlockRandom):
    """
    Smaller version for more granular evaluation
    """

    d = 0.01
    xy_poses = init_states(BlockRandom.xy_limits, d, BlockRandom.xy_reject)
    print(f"Length: {len(xy_poses)}")


def register(strict=True):
    add_env(
        env_id="PickPlaceHand-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=Fixed,
            xml_path="pick_place_hand.mjcf.xml",
            workdir=Path(__file__).parent,
            camera_names=["front", "right", "wrist", "left"],
        ),
        strict=strict,
    )

    add_env(
        env_id="PickPlaceHand-block_rand-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=BlockRandom,
            xml_path="pick_place_hand.mjcf.xml",
            workdir=Path(__file__).parent,
            keyframe_file="pick_place_hand.frame.yaml",
            camera_names=["front", "right", "wrist", "left"],
        ),
        strict=strict,
    )


if __name__ == "__main__":
    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))
    # import yaml
    # import numpy as np
    # from vuer_mujoco.tasks.pick_place_hand import make_env
    #
    # env = make_env(
    #     task=Fixed,
    #     xml_path="pick_place_hand.mjcf.xml",
    #     workdir=Path(__file__).parent,  # adjust if needed
    #     camera_names=["front", "right", "wrist", "left"]
    # )
    #
    # obs = env.reset()
    #
    # # Fetch data from sim
    # sim = env.env.env.env.env.env.env.physics
    #
    # frame = {
    #     "qpos": sim.data.qpos.tolist(),
    #     "qvel": sim.data.qvel.tolist(),
    #     "mocap_pos": sim.data.mocap_pos.ravel().tolist(),
    #     "mocap_quat": sim.data.mocap_quat.ravel().tolist(),
    # }
    #
    # # Optionally include control values or sensor data if they exist
    # if sim.data.ctrl.size > 0:
    #     frame["ctrl"] = sim.data.ctrl.tolist()
    #
    # if sim.data.sensordata.size > 0:
    #     frame["sensordata"] = sim.data.sensordata.tolist()
    #
    # with open("pick_place_hand.frame.yaml", "w") as f:
    #     yaml.dump(frame, f)

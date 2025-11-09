import random
from pathlib import Path
import numpy as np

from vuer_mujoco.schemas.utils.file import Prettify
from vuer_mujoco.schemas.utils.file import Save
from vuer_mujoco.schemas.schema import Body
from vuer_mujoco.tasks import add_env
from vuer_mujoco.tasks._floating_robotiq import FloatingRobotiq2f85
from vuer_mujoco.tasks.base.mocap_task import MocapTask
from vuer_mujoco.tasks.base.lucidxr_task import get_site, init_states
from vuer_mujoco.schemas.components.rigs.camera_rig import make_camera_rig
from vuer_mujoco.schemas.components.concrete_slab import ConcreteSlab


r, g, b = random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)
x1, y1 = random.uniform(-0.4, 0.4), random.uniform(-0.2, 0.2)
x2, y2 = random.uniform(-0.4, 0.4), random.uniform(-0.2, 0.2)

def random_quat():
    theta = np.random.uniform(0, 2 * np.pi)
    w = np.cos(theta / 2)
    z = np.sin(theta / 2)
    return w, 0, 0, z

quat1= random_quat()
q1 = f"{quat1[0]} 0 0 {quat1[3]}"

quat2 = random_quat()
q2 = f"{quat2[0]} 0 0 {quat2[3]}"

def make_schema(**options):
    table = ConcreteSlab(pos=[0, 0, 0.6], rgba="0.8 0.8 0.8 1")

    table = ConcreteSlab(
        assets="model",
        pos=[0, 0, 0.6],
        # group=4,
        rgba="0.8 0.8 0.8 1",
        _attributes={
            "name": "table",
        },
    )

    camera_rig = make_camera_rig([-0.5, 0, 0.6])

    box_1 = Body(
        attributes=dict(name="box-1", pos=f"{x1} {y1} 0.8", quat=q1),
        rgba="0 1 0 1.0",
        _preamble="""
          <asset>
            <material name="bright_green_mat" rgba="0 1 0 1" specular="1.0" shininess="1.0" reflectance="0.3"/>
            <material name="top_blue_mat" rgba="0 0 1 1" specular="1.0" shininess="1.0"/>
          </asset>
        """,
        _children_raw="""
          <joint name="{name}-cube_joint0" type="free" limited="false" actuatorfrclimited="false"/>
          <geom name="{name}-cube_g0" size="0.021556 0.0218909 0.02073" type="box" rgba="{rgba}"/>
          <geom name="{name}-cube_g0_vis" size="0.021556 0.0218909 0.02073" type="box" contype="0" conaffinity="0" group="1" mass="0" material="bright_green_mat"/>
          <geom name="{name}-top_face" type="box" size="0.021556 0.0218909 0.001" pos="0 0 0.021" contype="0" conaffinity="0" group="1" mass="0" material="top_blue_mat"/>
          <site name="{name}-cube_default_site" pos="0 0 0" size="0.002" rgba="1 0 0 -1"/>
        """,
    )

    box_2 = Body(
        attributes=dict(name="box-2", pos=f"{x2} {y2} 0.8"),
        rgba="1 0 0 1.0",
        _preamble="""
          <asset>
            <material name="bright_red_mat" rgba="1 0 0 1" specular="1.0" shininess="1.0" reflectance="0.3"/>
            <material name="top_cyan_mat" rgba="0 1 1 1" specular="1.0" shininess="1.0"/>
          </asset>
        """,
        _children_raw="""
          <joint name="{name}-cube_joint0" type="free" limited="false" actuatorfrclimited="false"/>
          <geom name="{name}-cube_g0" size="0.021556 0.0218909 0.02073" type="box" rgba="{rgba}"/>
          <geom name="{name}-cube_g0_vis" size="0.021556 0.0218909 0.02073" type="box" contype="0" conaffinity="0" group="1" mass="0" material="bright_red_mat"/>
          <geom name="{name}-top_face" type="box" size="0.021556 0.0218909 0.001" pos="0 0 0.021" contype="0" conaffinity="0" group="1" mass="0" material="top_cyan_mat"/>
          <site name="{name}-cube_default_site" pos="0 0 0" size="0.002" rgba="1 0 0 -1"/>
        """,
    )

    scene = FloatingRobotiq2f85(
        *camera_rig.get_cameras(),
        table,
        box_1,
        box_2,
        pos=[0, 0, 0.8],
        **options,
    )

    return scene._xml | Prettify()

class StackFixed(MocapTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cube_1_site = None
        self.cube_2_site = None
        self.gripper_site = None
        self.set_sites()

    def set_sites(self):
        self.cube_1_site = get_site(self.physics, "box-1")
        self.cube_2_site = get_site(self.physics, "box-2")
        self.gripper_site = get_site(self.physics, "gripper-pinch")

    def get_reward(self, physics):
        reward = 0.0
        # I believe physics.data is an MjData instance
        cube_1_pos = np.array(physics.data.site_xpos[self.cube_1_site.id])
        cube_2_pos = np.array(physics.data.site_xpos[self.cube_2_site.id])
        gripper_pos = np.array(physics.data.site_xpos[self.gripper_site.id])


        box_width = 2*0.021556
        epsilon = 0.01

        first_2_close = abs(cube_1_pos[0] - cube_2_pos[0]) < box_width/2 and abs(cube_1_pos[1] - cube_2_pos[1]) < box_width/2
        first_2_stack = abs(cube_1_pos[2] - cube_2_pos[2]) < box_width + epsilon

        if first_2_close and first_2_stack and np.linalg.norm(gripper_pos - cube_2_pos) > 0.2:
            reward = 1.0

        return reward


def overlap(x1, y1, x2, y2):
    epsilon = 0.05
    return abs(x2 - x1) < epsilon or abs(y2 - y1) < epsilon


class StackRandom(StackFixed):
    cube_1_addr = 0
    cube_2_addr = 7

    xy_limits = [-0.2, 0.2], [-0.2, 0.2]
    d = 0.1
    xy_poses_1 = init_states(xy_limits, d, ([0, 0], [0, 0]))
    xy_poses_2 = init_states(xy_limits, d, ([0, 0], [0, 0]))
    pose_buffer_1, pose_buffer_2 = None, None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def random_state(
        cls,
        qpos=None,
        quat=None,
        addrs=(cube_1_addr, cube_2_addr),
        index=None,
        mocap_pos=None,
        **kwargs,
    ):
        import random
        from copy import copy

        while True:
            if index is None:
                if not cls.pose_buffer_1:
                    cls.pose_buffer_1 = copy(cls.xy_poses_1)
                    random.shuffle(cls.pose_buffer_1)
                if not cls.pose_buffer_2:
                    cls.pose_buffer_2 = copy(cls.xy_poses_2)
                    random.shuffle(cls.pose_buffer_2)

                x1, y1 = cls.pose_buffer_1.pop(0)
                x2, y2 = cls.pose_buffer_2.pop(0)

            else:
                x1, y1 = cls.xy_poses_1[index]
                x2, y2 = cls.xy_poses_2[index]

            no_overlap = not overlap(x1, y1, x2, x2)
            if no_overlap:
                break

        new_qpos = qpos.copy()
        new_qpos[addrs[0] : addrs[0] + 2] = x1, y1
        new_qpos[addrs[1] : addrs[1] + 2] = x2, y2

        new_qpos[addrs[0] + 3 : addrs[0] + 7] = random_quat()
        new_qpos[addrs[1] + 3 : addrs[1] + 7] = random_quat()

        # Add Gaussian noise to mocap position
        if mocap_pos is not None:
            mocap_pos = mocap_pos.copy()
            noise = np.random.normal(loc=0.0, scale=0.005, size=mocap_pos.shape)  # std=5mm
            mocap_pos += noise

        return dict(qpos=new_qpos, quat=quat, mocap_pos=mocap_pos, **kwargs)


def register(strict=True):
    from vuer_mujoco.tasks.entrypoint import make_env

    add_env(
        env_id="StackBlocks-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="stack_blocks.mjcf.xml",
            workdir=Path(__file__).parent,
            mode="multiview",
        ),
        strict=strict,
    )


    add_env(
        env_id="StackBlocks-random-v1",
        entrypoint=make_env,
        kwargs=dict(
            camera_names=["front", "right", "wrist", "top", "right_r"],
            xml_renderer=make_schema,
            keyframe_file=None,
            workdir=Path(__file__).parent,
            mode="multiview",
        ),
        strict=strict,
    )


if __name__ == "__main__":
    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))
    register()


from pathlib import Path

import numpy as np

from vuer_mujoco.schemas.objects.vuer_mug import VuerMug
from vuer_mujoco.schemas.components.rigs.camera_rig_hand import make_camera_rig
from vuer_mujoco.schemas.schema import Replicate, Body
from vuer_mujoco.tasks.base.lucidxr_task import init_states
from vuer_mujoco.tasks.base.mocap_task import MocapTask
from vuer_mujoco.vendors.robohive.robohive_object import RobohiveObj
from vuer_mujoco.tasks._floating_shadowhand import FloatingShadowHand


center = 0
x1, y1 = center - 0.05, -0.025
x2, y2 = center + 0.17, 0.0


def get_initial_positions():
    base_pos = np.array([0.295, 0.195, 0.85])

    x_offset = np.array([0.01, 0.0, 0.0])
    y_offset = np.array([0.0, 0.01, 0.0])
    z_offset = np.array([0.0, 0.0, 0.01])

    positions = []
    for i in range(3):  # outermost loop (x-axis)
        for j in range(2):  # middle loop (y-axis)
            for k in range(2):  # innermost loop (z-axis)
                pos = base_pos + i * x_offset + j * y_offset + k * z_offset
                positions.append(pos)

    return np.array(positions)


def make_schema(**_):
    from vuer_mujoco.schemas.utils.file import Prettify

    robohive_table = RobohiveObj(
        otype="furniture",
        asset_key="simpleTable/simpleWoodTable",
        pos=[0, 0, 0],
        quat=[0.7071, 0, 0, 0.7071],
        local_robohive_root="robohive",
    )
    robohive_table_2 = RobohiveObj(
        otype="furniture",
        asset_key="simpleTable/simpleWoodTable",
        name="robohive_table_2",
        pos=[0.75, 0, 0],
        quat=[0.7071, 0, 0, 0.7071],
        local_robohive_root="robohive",
    )

    particles = Replicate(
        Replicate(
            Replicate(
                Body(
                    name="particle",
                    pos=[0.295, 0.195, 0.85],
                    _children_raw="""
                                    <freejoint/>
                                    <geom size=".008" mass="0.001" rgba=".8 .2 .1 1" condim="1"/>
                                """,
                ),
                _attributes=dict(
                    count=2,
                    offset="0.0 0.0 0.01",
                ),
            ),
            _attributes=dict(
                count=2,
                offset="0.0 0.01 0.0",
            ),
        ),
        _attributes=dict(
            count=3,
            offset="0.01 0.0 0.0",
        ),
    )

    camera_rig = make_camera_rig(pos=[-0.4, 0, 0.77])

    vuer_mug = VuerMug(pos=[0.3, -0.2, 0.8])
    # mujoco_mug = MuJoCoMug(pos=[0.3, 0.2, 0.8])
    from vuer_mujoco.schemas.objects.cup_3 import ObjaverseMujocoCup

    cup = ObjaverseMujocoCup(
        assets="kitchen/cup",
        pos=[0.3, 0.2, 0.8],
        name="cup",
        collision_count=32,
        randomize_colors=False,
    )

    # scene = UR5ShadowHand(
    #     vuer_mug,
    #     mujoco_mug,
    #     particles,
    #     # table,
    #     robohive_table,
    #     robohive_table_2,
    #     *camera_rig.get_cameras(),
    #     bimanual=False,
    #     camera_rig=camera_rig,
    #     pos=[-0.4, 0, 0.77],
    # )

    scene = FloatingShadowHand(
        vuer_mug,
        cup,
        particles,
        # table,
        robohive_table,
        robohive_table_2,
        *camera_rig.get_cameras(),
        bimanual=False,
        camera_rig=camera_rig,
        pos=[-0.4, 0, 0.77],
    )

    return scene._xml | Prettify()


class Fixed(MocapTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mug_site = None
        self.tree_site = None
        self.gripper_site = None

    def get_reward(self, physics):
        # if all of the particles are d close to the vuer mug's position
        reward = 0
        # get ball positions
        ball_positions = np.array([physics.named.data.qpos[qpos_start : qpos_start + 3] for qpos_start in self.ball_qpos_addrs])

        mug_qpos_addr = 0
        vuer_mug_position = physics.named.data.qpos[mug_qpos_addr : mug_qpos_addr + 3]

        mask = np.linalg.norm(ball_positions - vuer_mug_position, axis=1) < 0.05

        if np.all(mask):
            reward = 1

        return reward


class CupRandom(Fixed):
    cup_qpos_addr = 7
    ball_qpos_addrs = [7 * i for i in range(2, 14)]
    xy_limits = [-0.1, 0.1], [-0.1, 0.1]
    d = 0.03
    xy_poses = init_states(xy_limits, d, reject=None)

    print("the length is", len(xy_poses))
    pose_buffer = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        import random
        from copy import copy

        if index is None:
            if not cls.pose_buffer:
                cls.pose_buffer = copy(cls.xy_poses)
                random.shuffle(cls.pose_buffer)

            x, y = cls.pose_buffer.pop(0)
        else:
            x, y = cls.xy_poses[index]

        new_qpos = qpos.copy()

        new_qpos[cls.cup_qpos_addr : cls.cup_qpos_addr + 2] = [0.3 + x, 0.2 + y]
        for addr_start, initial_position in zip(cls.ball_qpos_addrs, get_initial_positions()):
            new_qpos[addr_start : addr_start + 3] = [initial_position[0] + x, initial_position[1] + y, initial_position[2]]

        # Add Gaussian noise to mocap position
        # if mocap_pos is not None:
        #     mocap_pos = mocap_pos.copy()
        #     noise = np.random.normal(loc=0.0, scale=0.05, size=mocap_pos.shape)  # std=5mm
        #     mocap_pos += noise

        return dict(qpos=new_qpos, quat=quat, mocap_pos=mocap_pos, **kwargs)


def register(strict=True, **_):
    from vuer_mujoco.tasks import add_env
    from vuer_mujoco.tasks.entrypoint import make_env

    add_env(
        env_id="ParticlePour-fixed-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=Fixed,
            camera_names=["left", "right", "wrist"],
            xml_path="particle_pour.mjcf.xml",
            keyframe_file="particle_pour.frame.yaml",
            workdir=Path(__file__).parent,
        ),
        strict=strict,
    )

    add_env(
        env_id="ParticlePour-cup_rand-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=CupRandom,
            camera_names=["left", "right", "wrist"],
            xml_path="particle_pour.mjcf.xml",
            keyframe_file="particle_pour.frame.yaml",
            workdir=Path(__file__).parent,
        ),
        strict=strict,
    )

    add_env(
        env_id="ParticlePour-cup_rand-dr-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="particle_pour.mjcf.xml",
            task=CupRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist"],
            keyframe_file="particle_pour.frame.yaml",
            mode="domain_rand",
            color_randomization_args=dict(ignore_geom_names=["particle*", "vuer-mug*", "cup*", "rh_*"]),
            camera_randomization_args=dict(camera_names=["left", "right"]),
        ),
        strict=strict,
    )

    add_env(
        env_id="ParticlePour-cup_rand-dr-eval-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="particle_pour.mjcf.xml",
            task=CupRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist"],
            keyframe_file="particle_pour.frame.yaml",
            mode="domain_rand",
            color_randomization_args=dict(ignore_geom_names=["particle*", "vuer-mug*", "cup*", "rh_*"]),
            randomize_camera=False,
            randomize_every_n_steps=1_000,
        ),
        strict=strict,
    )

    add_env(
        env_id="ParticlePour-cup_rand-lucid-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="particle_pour.mjcf.xml",
            task=CupRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist"],
            keyframe_file="particle_pour.frame.yaml",
            mode="lucid",
            object_keys=["vuer-mug"],
            invisible_prefix=["particle", "vuer-mug", "cup", "rh_"],
        ),
        strict=strict,
    )


if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Save

    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

    # register()
    #
    # from vuer_mujoco.tasks import make
    #
    # env = make("ParticlePour-fixed-v1", strict=False)
    #
    # model = env.unwrapped.env.physics.model
    # all_geom_names = [f"{model.geom(i).name}_{i}" for i in range(model.ngeom)]
    # # env.

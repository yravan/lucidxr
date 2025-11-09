from pathlib import Path
from copy import copy
import random
from scipy.spatial.transform import Rotation as R

from vuer_mujoco.schemas.utils.file import Save
from vuer_mujoco.tasks import add_env
from vuer_mujoco.schemas.components.concrete_slab import ConcreteSlab
from vuer_mujoco.schemas.components.rigs.camera_rig_hand import make_camera_rig
from vuer_mujoco.schemas.se3.se3_mujoco import Vector3
from vuer_mujoco.tasks._floating_robotiq import FloatingRobotiq2f85
from vuer_mujoco.schemas.components.force_plate import ForcePlate
from vuer_mujoco.tasks.base.mocap_task import MocapTask
from vuer_mujoco.tasks.base.lucidxr_task import get_geom_id, get_site, init_states
from vuer_mujoco.tasks._floating_shadowhand import FloatingShadowHand
import numpy as np
# Generate random values for r, g, and b
# r, g, b = random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)


def make_schema(**_):
    from vuer_mujoco.schemas.utils.file import Prettify
    from vuer_mujoco.schemas.objects.vuer_mug import VuerMug

    table = ConcreteSlab(pos=[0, 0, 0.6], rgba="0.8 0.8 0.8 1", roughness="0.2")

    rig_origin = table.surface_origin + Vector3(x=-0.55, y=0, z=0)
    camera_rig = make_camera_rig(rig_origin)

    mug = VuerMug(pos=[0, -0.1, 0.8], quat=[0, 0, 1, 0])

    work_area = ForcePlate(
        name="start-area",
        pos=(0, 0, 0.6052),
        quat=(0, 1, 0, 0),
        type="box",
        size="0.35 0.35 0.005",
        # rgba=f"{r} {g} {b} 1.0",
        rgba="0.5 0 0 1.0",
    )

    scene = FloatingShadowHand(
        mug,
        table,
        work_area,
        *camera_rig.get_cameras(),
        bimanual=False,
        camera_rig=camera_rig,
        pos=[0, 0, 0.8],
    )

    return scene._xml | Prettify()

class Fixed(MocapTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mug_geom_id = None
        self.plate_geom_id = None
        self.mug_site_1 = None
        self.mug_site_3 = None

        self.set_sites()

    def set_sites(self):

        self.mug_geom_id = get_geom_id(self.physics, "vuer-mug")
        self.plate_geom_id = get_geom_id(self.physics, "start-area")
        self.mug_site_1 = get_site(self.physics, "mug_handle_1")
        self.mug_site_3 = get_site(self.physics, "mug_handle_3")




    def get_reward(self, physics):




        # mug on ground
        mug_on_ground = False
        other_things_touching_mug = False
        for i in range(physics.data.ncon):
            contact = physics.data.contact[i]
            contact_geoms = [contact.geom1, contact.geom2]
            if self.mug_geom_id in contact_geoms and self.plate_geom_id in contact_geoms:
                mug_on_ground = True


            elif self.mug_geom_id in contact_geoms and self.plate_geom_id not in contact_geoms:
                other_things_touching_mug = True

        # flipped
        mug_pos_1 = physics.data.site_xpos[self.mug_site_1.id]
        mug_pos_3 = physics.data.site_xpos[self.mug_site_3.id]

        vec = mug_pos_1 - mug_pos_3
        vec_normalized = vec / np.linalg.norm(vec)
        z_axis = np.array([0.0, 0.0, 1.0])
        alignment = np.dot(vec_normalized, z_axis)
        flipped = alignment > 0.95

        return float(mug_on_ground and flipped and not other_things_touching_mug)




class FlipRandom(Fixed):
    xy_limits = [-0.15, 0.15], [-0.15, 0.15]
    # yaw_limits = (-np.pi, np.pi)
    mug_qpos_addr = 0

    initial_pos = [0, -0.1, 0.8]
    xy_poses = init_states(xy_limits, 0.05, None)
    pose_buffer = None

    @classmethod
    def random_state(
        cls,
        qpos=None,
        quat=None,
        addr=mug_qpos_addr,
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
        new_qpos[addr] = cls.initial_pos[0] + x
        new_qpos[addr + 1] = cls.initial_pos[1] + y
        new_qpos[addr + 2] = cls.initial_pos[2]

        # # -------------------- yaw randomisation --------------------
        # yaw = random.uniform(*cls.yaw_limits)
        # new_qpos[addr + 3] = np.cos(yaw / 2.0)   # qw
        # new_qpos[addr + 4] = 0.0                 # qx
        # new_qpos[addr + 5] = 0.0                 # qy
        # new_qpos[addr + 6] = np.sin(yaw / 2.0)   # qz
        # # -----------------------------------------------------------

        # preserve or overwrite the explicit `quat` argument
        quat = new_qpos[addr + 3 : addr + 7].copy()

        if mocap_pos is not None:
            mocap_pos = mocap_pos.copy()
            mocap_pos += np.random.normal(0.0, 0.005, mocap_pos.shape)

        return dict(qpos=new_qpos, quat=quat, mocap_pos=mocap_pos, **kwargs)

def register(strict=True):
    from vuer_mujoco.tasks.entrypoint import make_env

    add_env(
        env_id="FlipMug-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="flip_mug.mjcf.xml",
            workdir=Path(__file__).parent,
            mode="multiview",
        ),
    )

    add_env(
        env_id="FlipMug-depth-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="flip_mug.mjcf.xml",
            workdir=Path(__file__).parent,
            mode="multiview-depth",
        ),
    )

    add_env(
        env_id="FlipMug-wrist-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="flip_mug.mjcf.xml",
            workdir=Path(__file__).parent,
            image_key="wrist/rgb",
            camera_id=4,
            mode="rgb",
        ),
    )

    add_env(
        env_id="FlipMug-wrist-depth-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="flip_mug.mjcf.xml",
            workdir=Path(__file__).parent,
            image_key="wrist/depth",
            camera_id=4,
            mode="depth",
        ),
    )

    add_env(
        env_id="FlipMug-random-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=FlipRandom,
            xml_path="flip_mug.mjcf.xml",
            workdir=Path(__file__).parent,
            camera_names = ["front", "right", "wrist", "left", "back"],
            keyframe_file = "flip_mug.frame.yaml"
        ),
        strict=strict
    )


    add_env(
        env_id="FlipMug-random-lucid-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=FlipRandom,
            xml_path="flip_mug.mjcf.xml",
            # xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            camera_names = ["right", "wrist", "back"],
            keyframe_file = "flip_mug.frame.yaml",
            mode="lucid",
            object_keys = ["mug"],
            invisible_prefix=["rh_", "shadow_hand"]
        ),
        strict=strict
    )

    add_env(
        env_id="FlipMug-domain_rand-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=FlipRandom,
            camera_names=["front", "right", "wrist", "left", "back"],
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="domain_rand",
            camera_randomization_args=dict(
                camera_names=["back", "right"]
            ),
            randomize_every_n_steps=1,
            randomize_camera=True,
            randomize_color=True,
            randomize_lighting=True,
        ),
        strict=strict,
    )



if __name__ == "__main__":
    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

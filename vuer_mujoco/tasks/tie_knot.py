import os
from pathlib import Path

import numpy as np

from vuer_mujoco.schemas.base import Xml
from vuer_mujoco.schemas.components.concrete_slab import ConcreteSlab
from vuer_mujoco.schemas.components.rigs.camera_rig_stereo import make_origin_stereo_rig
from vuer_mujoco.schemas.robots.camera import make_camera
from vuer_mujoco.schemas.schema import FreeBody, Body
from vuer_mujoco.tasks import add_env
from vuer_mujoco.schemas.components.rigs.camera_rig_calibrated import make_camera_rig, FOV
from vuer_mujoco.schemas.components.mj_ground_plane import GroundPlane
from vuer_mujoco.tasks._floating_robotiq import FloatingRobotiq2f85
from vuer_mujoco.tasks.base.lucidxr_task import get_geom_id, get_body_id, get_site, init_states
from vuer_mujoco.tasks.base.mocap_task import MocapTask
from vuer_mujoco.tasks.entrypoint import make_env
from vuer_mujoco.schemas.objects.orbit_table import OpticalTable


center = 0
x1, y1 = (
    0.05,
    0,
)


def make_schema(mode="cameraready", robot="panda", show_robot=False, **options):
    from vuer_mujoco.schemas.objects.rope import MuJoCoRope
    from vuer_mujoco.schemas.utils.file import Prettify

    optical_table = OpticalTable(
        pos=[-0.4, 0, 0.77],
        assets="model",
        _attributes={"name": "table_optical"},
    )
    table = ConcreteSlab(
        assets="model",
        pos=[0, 0, 0.76],
        group=4,
        rgba="0.8 0 0 0.0",
        _attributes={
            "name": "table",
        },
    )
    camera_rig = make_camera_rig(pos=[-0.3, 0, 1.07])
    stereo_cameras = make_origin_stereo_rig(pos=[-0.3, 0, 1.07])
    camera_rig.left_camera._xml = camera_rig.left_camera._xml.replace("0.14 0.355 1.395", "0.14 0.355 1.2")
    camera_rig.right_camera._xml = camera_rig.right_camera._xml.replace("pos=\"0.07500000000000001 -0.355 1.395\"", "pos=\"0.07500000000000001 -0.355 1.2\"")
    def rotated_wrist_camera(name="wrist", pos="0.1 0.0 0.01", quat="-0.11 0.7 -0.7 0.11"):
        return make_camera(
            name,
            pos=pos,
            quat=quat,
            fovy=FOV,
        )
    camera_rig.wrist_camera = rotated_wrist_camera

    if robot == "panda":
        from vuer_mujoco.schemas.robots.franka_panda import Panda
        from vuer_mujoco.schemas.robots.tomika_gripper import TomikaGripper

        gripper = TomikaGripper(
            name="test_gripper",
            mocap_pos="0.25 0.0 1.10",
            mocap_quat="0 0 1 0",
            wrist_mount=camera_rig.wrist_camera(),
        )
        panda = Panda(end_effector=gripper, name="test_panda", pos=(0, 0, 0.79), quat=(1, 0, 0, 0))
    else:
        raise ValueError(f"Unknown robot: {robot}")

    rope = MuJoCoRope(
        pos=[x1, y1, 1.1],
        damping=0.0005,
        twist=1e1,
        bend=1e1,
        geom_size=0.008,
        attributes={
            "prefix": "rope_",
            "count": "50 1 1",
            "curve": "s",
            "size": "0.43",
            "initial": "none",
            "offset": "0 0 0.8",
        },
    )
    rope_anchor = Body(
        """
          <!-- translate along x -->
        <joint name="jx" type="slide" axis="1 0 0"
               damping="500" frictionloss="200" armature="5"/>
        <!-- translate along y -->
        <joint name="jy" type="slide" axis="0 1 0"
               damping="500" frictionloss="200" armature="5"/>
        <!-- optional: rotate about z in the plane -->
        <!-- <joint name="jz" type="hinge" axis="0 0 1"
               damping="200" frictionloss="50" armature="1"/> -->
        <!-- your geoms here -->
        <geom type="sphere" size="0.01" contype="0" conaffinity="0" rgba="1 1 1 0"/>
        """,
        pos=[x1, y1, 1.1],
        quat=[1, 0, 0, 0],
        attributes={"name": "rope_anchor"},
        postamble="""
        <equality>
            <weld body1="rope_B_first" body2="rope_anchor" relpose="0 0 0  1 0 0 0" solref="0.001 3" solimp="0.9 0.95 0.01"/>
        </equality>
        """,
    )
    rope = FreeBody(rope)

    children = [
        *camera_rig.get_cameras(),
        *stereo_cameras.get_cameras(),
        table,
        rope,
        rope_anchor,
    ]

    if mode == "demo":
        pass
    elif mode == "cameraready":
        children += [optical_table]

    if show_robot:
        children.append(panda)
        children.append(gripper._mocaps)

    scene = FloatingRobotiq2f85(
        *children,
        pos=[-0.0, 0, 1.2],
        camera_rig=camera_rig,
        **options,
    )

    return scene._xml | Prettify()


class Fixed(MocapTask):
    vel_thresh = 0.01  # threshold for considering the rope to be stationary

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_reward(self, physics):
        # for j in range(physics.model.njnt):
        #     adr = physics.model.jnt_qposadr[j]
        #     type = physics.model.jnt_type[j]  # 0=free, 1=ball, 2=slide, 3=hinge
        #     print(physics.model.jnt(j).name,"→ qpos", adr, "type", type)
        rope_bodies = [get_body_id(physics, f"rope_B_{i}", exact_match=True) for i in range(1, 48)]
        rope_geom_ids = [get_geom_id(physics, f"rope_G{i}", exact_match=True) for i in range(48)]
        # for b in range(physics.model.nbody):
        #     print(physics.model.body(b).name)

        contact_count = 0
        for i in range(physics.data.ncon):
            c = physics.data.contact[i]
            g1, g2 = c.geom1, c.geom2
            if g1 in rope_geom_ids and g2 in rope_geom_ids and abs(g1 - g2) > 2:
                contact_count += 1
        has_self_contacts = contact_count >= 3

        # 3. Segment overlap (entanglement proxy)
        positions = np.array([physics.data.xpos[bid] for bid in rope_bodies])
        entangled = False
        for i in range(len(positions)):
            for j in range(i + 3, len(positions)):  # skip adjacent links
                if np.linalg.norm(positions[i] - positions[j]) < 0.02:
                    entangled = True
                    break
            if entangled:
                break

        # 4. Rope has settled
        stationary = True
        # for bid in rope_bodies:
        #     v = physics.data.cvel[bid]
        #     print(np.linalg.norm(v))
        #     if np.linalg.norm(v) > self.vel_thresh:
        #         stationary = False
        #         break

        # Gripper distance reward
        gripper_pos = physics.data.site_xpos[get_site(physics, "gripper-pinch").id]
        min_dist = min(np.linalg.norm(gripper_pos - p) for p in positions)
        gripper_far_enough = min_dist > 0.05  # tweak this threshold

        # print(has_self_contacts, entangled, stationary)

        return 1.0 if has_self_contacts and entangled and stationary and gripper_far_enough else 0.0


class RopeRandom(Fixed):
    rope_base_qpos_addr = 199

    d = 0.01
    xy_limits = [x1 - 0.05, x1 + 0.05], [y1 - 0.05, y1 + 0.05]
    xy_reject = [x1, y1], [x1, y1]

    xy_poses = init_states(xy_limits, d, xy_reject)
    print("the length is", len(xy_poses))
    pose_buffer = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def random_state(
        cls,
        index=None,
        qpos=None,
        mocap_pos=None,
        addr = rope_base_qpos_addr,
        **kwargs,
    ):
        import random

        if index is None:
            # if not cls.pose_buffer:
            #     cls.pose_buffer = copy(cls.xy_poses)
            #     random.shuffle(cls.pose_buffer)
            #
            # x, y = cls.pose_buffer.pop(0)
            x, y = random.choice(cls.xy_poses)
        else:
            x, y = cls.xy_poses[index]

        new_qpos = qpos.copy()

        new_qpos[addr : addr + 2] = x, y
        # print("new_qpos", new_qpos[addr : addr + 2])

        # Add Gaussian noise to mocap position
        if mocap_pos is not None:
            mocap_pos = mocap_pos.copy()
            noise = np.random.normal(loc=0.0, scale=0.005, size=mocap_pos.shape)  # std=5mm
            mocap_pos += noise

        return dict(qpos=new_qpos,mocap_pos=mocap_pos, **kwargs)

    def get_reward(self, physics):
        pass
        rope_bodies = [get_body_id(physics, f"rope_B_{i}", exact_match=True) for i in range(1, 48)]
        rope_geom_ids = [get_geom_id(physics, f"rope_G{i}", exact_match=True) for i in range(48)]

        contact_count = 0
        for i in range(physics.data.ncon):
            c = physics.data.contact[i]
            g1, g2 = c.geom1, c.geom2
            if g1 in rope_geom_ids and g2 in rope_geom_ids and abs(g1 - g2) > 2:
                contact_count += 1
        has_self_contacts = contact_count >= 3

        # 3. Segment overlap (entanglement proxy)
        positions = np.array([physics.data.xpos[bid] for bid in rope_bodies])
        entangled = False
        for i in range(len(positions)):
            for j in range(i + 3, len(positions)):  # skip adjacent links
                if np.linalg.norm(positions[i] - positions[j]) < 0.02:
                    entangled = True
                    break
            if entangled:
                break

        # 4. Rope has settled
        stationary = True
        # for bid in rope_bodies:
        #     v = physics.data.cvel[bid]
        #     print(np.linalg.norm(v))
        #     if np.linalg.norm(v) > self.vel_thresh:
        #         stationary = False
        #         break

        # Gripper distance reward
        gripper_pos = physics.data.site_xpos[get_site(physics, "gripper-pinch").id]
        min_dist = min(np.linalg.norm(gripper_pos - p) for p in positions)
        gripper_far_enough = min_dist > 0.05  # tweak this threshold

        # print(has_self_contacts, entangled, stationary)

        return 1.0 if has_self_contacts and entangled and stationary and gripper_far_enough else 0.0


def register(strict=True):
    add_env(
        env_id="TieKnot-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=Fixed,
            camera_names=["right", "wrist", "left", "stereo_far_left", "stereo_far_right"],
            xml_renderer=make_schema,
            keyframe_file="tie_knot.frame.yaml",
            workdir=Path(__file__).parent,
            mode="multiview",
            skip_start=50,  # Important for eval, otherwise the rope is not in the right position
        ),
        strict=strict,
    )
    add_env(
        env_id="TieKnot-rope_random-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=RopeRandom,
            camera_names=["right", "wrist", "left", "stereo_far_left", "stereo_far_right"],
            xml_renderer=make_schema,
            keyframe_file="tie_knot.frame.yaml",
            workdir=Path(__file__).parent,
            mode="multiview",
            skip_start=50,  # Important for eval, otherwise the rope is not in the right position
        ),
        strict=strict,
    )
    add_env(
        env_id="TieKnot-domain_rand-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=Fixed,
            camera_names=["right", "left", "wrist","stereo_far_left","stereo_far_right"],
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="domain_rand",
        ),
        strict=strict,
    )
    add_env(
        env_id="TieKnot-domain_rand-eval-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=Fixed,
            camera_names=["right", "left", "wrist","stereo_far_left","stereo_far_right"],
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="domain_rand",
            randomize_camera=False,
            randomize_every_n_steps=0,
        ),
        strict=strict,
    )
    add_env(
        env_id="TieKnot-random-lucid-v1",
        entrypoint=make_env,
        kwargs=dict(
            task=RopeRandom,
            camera_names=["right", "left", "wrist","stereo_far_left","stereo_far_right"],
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="lucid",
            object_keys=["rope"],
        ),
        strict=strict,
    )
    add_env(
        env_id="TieKnot-random-gsplat-cic_bench",
        entrypoint=make_env,
        kwargs=dict(
            task=RopeRandom,
            camera_names=["right", "left", "wrist","stereo_far_left","stereo_far_right"],
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="gsplat",
            gsplat_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_bench",
            transform_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/tie_knot/cic_bench",
            invisible_prefix=["rope","gripper","ur5"],
        ),
        strict=strict,
    )
    add_env(
        env_id="TieKnot-random-gsplat-google_building_table",
        entrypoint=make_env,
        kwargs=dict(
            task=RopeRandom,
            camera_names=["right", "left", "wrist","stereo_far_left","stereo_far_right"],
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="gsplat",
            gsplat_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/google_building_table",
            transform_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/tie_knot/google_building_table",
            invisible_prefix=["rope","gripper","ur5"],
        ),
        strict=strict,
    )
    add_env(
        env_id="TieKnot-random-gsplat-mit_medical_wood_chair",
        entrypoint=make_env,
        kwargs=dict(
            task=RopeRandom,
            camera_names=["right", "left", "wrist","stereo_far_left","stereo_far_right"],
            xml_renderer=make_schema,
            workdir=Path(__file__).parent,
            mode="gsplat",
            gsplat_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/mit_medical_wood_chair",
            transform_path = f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/tie_knot/mit_medical_wood_chair",
            invisible_prefix=["rope","gripper","ur5"],
        ),
        strict=strict,
    )


if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Save

    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

import os

from pathlib import Path

import numpy as np

from vuer_mujoco.schemas.components.rigs.camera_rig_stereo import make_origin_stereo_rig
from vuer_mujoco.schemas.objects.mj_sdf import MjSDF
from vuer_mujoco.schemas.objects.mug import ObjaverseMujocoMug
from vuer_mujoco.schemas.objects.rope import MuJoCoRope
from vuer_mujoco.schemas.objects.sort_shapes import LeBox, SquareBlock, TriangleBlock, HexBlock, CircleBlock
from vuer_mujoco.schemas.objects.vuer_mug import VuerMug
from vuer_mujoco.schemas.schema import FreeBody, Body
from vuer_mujoco.tasks._floating_robotiq import UR5Robotiq2f85
from vuer_mujoco.schemas.components.rigs.camera_rig_calibrated import make_camera_rig
from vuer_mujoco.tasks.base.lucidxr_task import get_site
from vuer_mujoco.tasks.base.mocap_task import MocapTask
from itertools import combinations
from math import hypot
import random

from vuer_mujoco.vendors.robohive.robohive_object import RobohiveObj


x_center, y_center = 0.3, 0.15
x1, y1 = 0.3, -0.25
x2, y2 = 0.45, -0.15

def sample_two_points(
    *,
    xmin,
    xmax,
    ymin,
    ymax,
    d,
    eps,
    exclude_center=None,  # (xc, yc) or None
    exclude_radius=0.0,  # distance to keep away from the center
    max_attempts=10_000,
):
    xs = np.arange(xmin, xmax + 1e-12, d)
    ys = np.arange(ymin, ymax + 1e-12, d)
    grid = np.array(np.meshgrid(xs, ys)).T.reshape(-1, 2)

    if grid.shape[0] < 3:
        raise ValueError("Grid contains fewer than three points.")

    # Pre-compute mask for the exclusion zone, if requested
    if exclude_center is not None and exclude_radius > 0.0:
        cx, cy = exclude_center
        dists_to_center = np.hypot(grid[:, 0] - cx, grid[:, 1] - cy)
        valid_mask = dists_to_center > exclude_radius
        candidate_indices = np.nonzero(valid_mask)[0]
        if len(candidate_indices) < 3:
            raise ValueError("Exclusion zone leaves fewer than three valid points.")
    else:
        candidate_indices = np.arange(len(grid))

    for _ in range(max_attempts):
        idx = random.sample(list(candidate_indices), k=2)
        pts = grid[idx]

        # pair-wise separation constraint
        if all(hypot(*(a - b)) > eps for a, b in combinations(pts, 2)):
            return [tuple(p) for p in pts]

    raise ValueError("Unable to find three points satisfying all constraints; " "relax `eps` / `exclude_radius` or enlarge the grid.")

def make_schema(**options):
    from vuer_mujoco.schemas.utils.file import Prettify
    from vuer_mujoco.schemas.objects.cylinder import Cylinder

    robohive_table = RobohiveObj(
        otype="furniture",
        asset_key="simpleTable/simpleWoodTable",
        pos=[0.4, 0, 0],
        quat=[0.7071, 0, 0, 0.7071],
        local_robohive_root="robohive",
    )
    camera_rig = make_camera_rig(pos=[0, 0, 0.77])
    stereo_rig = make_origin_stereo_rig(pos=[0, 0, 0.77])


    ibox = LeBox(attributes={"name": "insertion-box"}, assets="sort_shape", pos=[0.5, 0, 0.82], scale=0.08)
    square_block = SquareBlock(attributes={"name": "square"}, assets="sort_shape", pos=[0.3, -0.0, 0.82], scale=0.07)
    triangle_block = TriangleBlock(attributes={"name": "triangle"}, assets="sort_shape", pos=[0.4, -0.0, 0.82], scale=0.07)
    hex_block = HexBlock(attributes={"name": "hex"}, assets="sort_shape", pos=[0.3, 0.1, 0.82], scale=0.07)
    circle_block = CircleBlock(attributes={"name": "circle"}, assets="sort_shape", pos=[0.4, 0.1, 0.82], scale=0.07)

    rope = MuJoCoRope(
        pos=[x1, -y1, 1.1],
        damping=0.0005,
        twist=1e1,
        bend=1e1,
        geom_size=0.008,
        attributes={
            "prefix": "rope_",
            "count": "30 1 1",
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
        pos=[x1, -y1, 1.1],
        quat=[1, 0, 0, 0],
        attributes={"name": "rope_anchor"},
        postamble="""
            <equality>
                <weld body1="rope_B_first" body2="rope_anchor" relpose="0 0 0  1 0 0 0" solref="0.001 3" solimp="0.9 0.95 0.01"/>
            </equality>
            """,
    )
    rope = FreeBody(rope)



    box = MjSDF(
        pos=[0.465, 0.27, 0.82],
        quat=[1, 0, 0, 0],
        assets="ball_sorting_toy",
        geom_quat = "-0.5 -0.5 0.5 0.5",
        _attributes={"name": "ball-sorting-toy"},
        scale="0.12 0.12 0.12",
        additional_children_raw="""
        <site name="hole-1" pos="0.08 0 0.05" size="0.03" rgba="1 0 0 0" type="sphere"/>
        """
    )
    #
    ball_1 = Cylinder(
        pos=[x_center + 0.05, y_center, 0.79],
        quat=[0, 0, 1, 0],
        rgba="1 0.5 0 1",
        _attributes={
            "name": "cylinder-orange",
        },
    )
    ball_2 = Cylinder(
        pos=[x_center - 0.05, y_center, 0.79],
        quat=[0, 0, 1, 0],
        rgba="0 0 1 1",
        _attributes={
            "name": "cylinder-blue",
        },
    )
    mug = ObjaverseMujocoMug(assets="kitchen/mug", pos=[x1, y1, 0.85], collision_count=32, visual_count=2)
    mug_tree = MjSDF(
        pos=[x2, y2, 1],
        assets="mug_tree",
        mass=0.3,
        _attributes={
            "name": "tree",
            "quat": "0.5 0.5 0.5 0.5",
        },
        additional_children_raw="""\t<site name="tree_goal_1" pos="-.03 0.076 -0.036" size="0.007" rgba="1 1 1 1"/>
                                          \t<site name="tree_goal_2" pos="-.03 0.066 -0.016" size="0.007" rgba="1 1 1 1"/>
                                          \t<site name="tree_goal_3" pos="-.03 0.071 -0.026" size="0.007" rgba="1 1 1 1"/>
                                          \t<site name="tree_goal_4" pos="-.03 0.081 -0.046" size="0.007" rgba="1 1 1 1"/>
                                          \t<site name="tree_goal_5" pos="-.03 0.086 -0.056" size="0.007" rgba="1 1 1 1"/>
                                          \t<site name="tree_goal_6" pos="-.03 0.091 -0.066" size="0.007" rgba="1 1 1 1"/>
                                            """,
        scale="0.17 0.2118 0.17",
    )


    children = [
        *camera_rig.get_cameras(),
        *stereo_rig.get_cameras(),
        robohive_table,
        # robot_room,
        # box,
        ball_1,
        # ball_2,
        ibox,
        square_block,
        triangle_block,
        hex_block,
        circle_block,
        mug,
        # mug_tree,
        rope,
        rope_anchor,
    ]

    scene = UR5Robotiq2f85(
        *children,
        pos=[0, 0, 0.77],
        **options,
        camera_rig=camera_rig,
    )

    return scene._xml | Prettify()


class Fixed(MocapTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.step = 0

    @staticmethod
    def _site_in_hole(
        physics,
        cyl_site_id: int,
        hole_site_id: int,
        radial_margin: float = 0.002,  # shrink circle slightly for robustness
        depth_thresh: float = 0.001,
    ):  # require being 5 mm past the plane
        """
        Returns True iff the cylinder site is inside the hole circle AND has crossed the hole plane.

        - Uses the hole site's frame so this works even if the hole is tilted.
        - radial_margin > 0 makes the test stricter than the exact radius to avoid edge flukes.
        - depth_thresh < 0 means: below the hole plane along the hole's local +Z axis.
        """
        # Hole geometry
        hole_pos = physics.data.site_xpos[hole_site_id]  # (3,)
        hole_R = physics.data.site_xmat[hole_site_id].reshape(3, 3)  # local->world
        hole_rad = float(physics.model.site_size[hole_site_id][0])  # sphere site: size[0] = radius

        # Cylinder site world pos
        cyl_pos = physics.data.site_xpos[cyl_site_id]

        # Express relative position in the hole's local frame
        rel_world = cyl_pos - hole_pos
        rel_local = hole_R.T @ rel_world  # world -> local

        radial_dist = np.linalg.norm(rel_local[:2])  # distance in hole plane
        depth_along_hole_z = rel_local[2]  # +z is "out of hole"; negative is "through"

        inside_circle = radial_dist <= (hole_rad - radial_margin)
        past_plane = depth_along_hole_z <= depth_thresh
        # print("depth_along_hole_z", depth_along_hole_z, "radial_dist", radial_dist, "hole_rad", hole_rad)
        # print("past_plane", past_plane, "inside_circle", inside_circle)
        return bool(inside_circle and past_plane)

    def check_orange_in_goal(self, physics):
        self.cylinder_1 = get_site(physics, "cylinder-orange")
        return self._site_in_hole(physics, self.cylinder_1.id, get_site(physics, "hole-1").id)

    def check_blue_in_goal(self, physics):
        self.cylinder_2 = get_site(physics, "cylinder-blue")
        return self._site_in_hole(physics, self.cylinder_2.id, get_site(physics, "hole-1").id)

    def get_reward(self, physics):

        if self.step == 0 and self.check_blue_in_goal(physics):
            self.step += 1
        if self.step == 1 and self.check_orange_in_goal(physics):
            self.step += 1
        if self.step == 2:
            return 1.0

        # print("step", self.step)
        # print(f"Step: {self.step}, Orange in goal: {self.check_orange_in_goal(physics)}, Blue in goal: {self.check_blue_in_goal(physics)}")

        return 0.0


class ColorRandom(Fixed):
    box_qpos_addr = 0
    ball_qpos_addrs = [7, 14, 21]

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
        new_qpos = qpos.copy()
        # randomly swap the balls positions
        positions = [
            [x1, y1, 0.62],
            [x3, y3, 0.62],
            [x4, y4, 0.62],
        ]
        random.shuffle(positions)
        for i, ball_addr in enumerate(cls.ball_qpos_addrs):
            new_qpos[ball_addr] = positions[i][0]
            new_qpos[ball_addr + 1] = positions[i][1]
            new_qpos[ball_addr + 2] = positions[i][2]
        if mocap_pos is not None:
            mocap_pos = mocap_pos.copy()
            mocap_pos += np.random.normal(0.0, 0.005, mocap_pos.shape)
            
        return dict(qpos=new_qpos, quat=quat, mocap_pos=mocap_pos, **kwargs)


class BallRandom(Fixed):
    box_qpos_addr = 0
    ball_qpos_addrs = [7, 14]
    d = 0.02
    initial_pos = [x_center, y_center, 0.79]
    x_bounds = [-0.125, 0.125]
    y_bounds = [-0.1, 0.1]

    xmin = initial_pos[0] + x_bounds[0]
    xmax = initial_pos[0] + x_bounds[1]
    ymin = initial_pos[1] + y_bounds[0]
    ymax = initial_pos[1] + y_bounds[1]

    eps = 0.08

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
        points = sample_two_points(
            xmin=cls.xmin,
            xmax=cls.xmax,
            ymin=cls.ymin,
            ymax=cls.ymax,
            d=cls.d,
            eps=cls.eps,
        )

        new_qpos = qpos.copy()
        for ball_addr in cls.ball_qpos_addrs:
            x, y = points.pop()
            new_qpos[ball_addr] = x
            new_qpos[ball_addr + 1] = y
            new_qpos[ball_addr + 2] = 0.79

        if mocap_pos is not None:
            mocap_pos = mocap_pos.copy()
            mocap_pos += np.random.normal(0.0, 0.005, mocap_pos.shape)

        return dict(qpos=new_qpos, quat=quat, mocap_pos=mocap_pos, **kwargs)


def register(strict=True):
    from vuer_mujoco.tasks import add_env
    from vuer_mujoco.tasks.entrypoint import make_env

    add_env(
        env_id="BallSortingToyNew-fixed-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer = make_schema,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist", "stereo_far_left", "stereo_far_right"],
            keyframe_file="ball_sorting_toy_new.frame.yaml",
        ),
        strict=strict,
    )
    add_env(
        env_id="BallSortingToyNew-color_random-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer = make_schema,
            task=ColorRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist", "stereo_far_left", "stereo_far_right"],
            keyframe_file="ball_sorting_toy_new.frame.yaml",
        ),
        strict=strict,
    )
    add_env(
        env_id="BallSortingToyNew-ball_random-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer = make_schema,
            task=BallRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist", "stereo_far_left", "stereo_far_right"],
            keyframe_file="ball_sorting_toy_new.frame.yaml",
        ),
        strict=strict,
    )
    add_env(
        env_id="BallSortingToyNew-fixed-lucid-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer=make_schema,
            task=Fixed,
            xml_render_options=dict(mode="lucid"),
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist", "stereo_far_left", "stereo_far_right"],
            mode="lucid",
            keyframe_file="ball_sorting_toy_new.frame.yaml",
            object_keys=["cylinder-blue", "cylinder-orange", "ball-sorting-toy"],
        ),
        strict=strict,
    )
    add_env(
        env_id="BallSortingToyNew-ball_random-gsplat-cic_kitchen_4th_night",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer = make_schema,
            task=BallRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist", "stereo_far_left", "stereo_far_right"],
            mode="gsplat",
            gsplat_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_kitchen_4th_night",
            transform_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/ball_sorting_toy_new/cic_kitchen_4th_night",
            invisible_prefix=["cylinder-blue", "cylinder-orange", "ball-sorting-toy", "gripper", "ur5"],
            keyframe_file="ball_sorting_toy_new.frame.yaml",
        ),
        strict=strict,
    )
    add_env(
        env_id="BallSortingToyNew-ball_random-gsplat-cic_4th_nook",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer = make_schema,
            task=BallRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist", "stereo_far_left", "stereo_far_right"],
            mode="gsplat",
            gsplat_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_4th_nook",
            transform_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/ball_sorting_toy_new/cic_4th_nook",
            invisible_prefix=["cylinder-blue", "cylinder-orange", "ball-sorting-toy", "gripper", "ur5"],
            keyframe_file="ball_sorting_toy_new.frame.yaml",
        ),
        strict=strict,
    )
    add_env(
        env_id="BallSortingToyNew-ball_random-gsplat-cic_11th_kitchen",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer = make_schema,
            task=BallRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist", "stereo_far_left", "stereo_far_right"],
            mode="gsplat",
            gsplat_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_11th_kitchen",
            transform_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/ball_sorting_toy_new/cic_11th_kitchen",
            invisible_prefix=["cylinder-blue", "cylinder-orange", "ball-sorting-toy", "gripper", "ur5"],
            keyframe_file="ball_sorting_toy_new.frame.yaml",
        ),
        strict=strict,
    )
    add_env(
        env_id="BallSortingToyNew-ball_random-gsplat-cic_11th_kitchen_back",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer = make_schema,
            task=BallRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist", "stereo_far_left", "stereo_far_right"],
            mode="gsplat",
            gsplat_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_11th_kitchen_back",
            transform_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/ball_sorting_toy_new/cic_11th_kitchen_back",
            invisible_prefix=["cylinder-blue", "cylinder-orange", "ball-sorting-toy", "gripper", "ur5"],
            keyframe_file="ball_sorting_toy_new.frame.yaml",
        ),
        strict=strict,
    )
    add_env(
        env_id="BallSortingToyNew-ball_random-gsplat-cic_11th_stationary",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer = make_schema,
            task=BallRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist", "stereo_far_left", "stereo_far_right"],
            mode="gsplat",
            gsplat_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_11th_stationary",
            transform_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/ball_sorting_toy_new/cic_11th_stationary",
            invisible_prefix=["cylinder-blue", "cylinder-orange", "ball-sorting-toy", "gripper", "ur5"],
            keyframe_file="ball_sorting_toy_new.frame.yaml",
        ),
        strict=strict,
    )
    add_env(
        env_id="BallSortingToyNew-ball_random-gsplat-cic_bench",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer = make_schema,
            task=BallRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist", "stereo_far_left", "stereo_far_right"],
            mode="gsplat",
            gsplat_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_bench",
            transform_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/ball_sorting_toy_new/cic_bench",
            invisible_prefix=["cylinder-blue", "cylinder-orange", "ball-sorting-toy", "gripper", "ur5"],
            keyframe_file="ball_sorting_toy_new.frame.yaml",
        ),
        strict=strict,
    )
    add_env(
        env_id="BallSortingToyNew-ball_random-gsplat-cic_kitchen_4th_day",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer = make_schema,
            task=BallRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist", "stereo_far_left", "stereo_far_right"],
            mode="gsplat",
            gsplat_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_kitchen_4th_day",
            transform_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/ball_sorting_toy_new/cic_kitchen_4th_day",
            invisible_prefix=["cylinder-blue", "cylinder-orange", "ball-sorting-toy", "gripper", "ur5"],
            keyframe_file="ball_sorting_toy_new.frame.yaml",
        ),
        strict=strict,
    )
    add_env(
        env_id="BallSortingToyNew-ball_random-gsplat-google_building_table",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer = make_schema,
            task=BallRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist", "stereo_far_left", "stereo_far_right"],
            mode="gsplat",
            gsplat_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/google_building_table",
            transform_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/ball_sorting_toy_new/google_building_table",
            invisible_prefix=["cylinder-blue", "cylinder-orange", "ball-sorting-toy", "gripper", "ur5"],
            keyframe_file="ball_sorting_toy_new.frame.yaml",
        ),
        strict=strict,
    )
    add_env(
        env_id="BallSortingToyNew-ball_random-gsplat-cic_12th_coffee_table",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer = make_schema,
            task=BallRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist", "stereo_far_left", "stereo_far_right"],
            mode="gsplat",
            gsplat_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/cic_12th_coffee_table",
            transform_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/ball_sorting_toy_new/cic_12th_coffee_table",
            invisible_prefix=["cylinder-blue", "cylinder-orange", "ball-sorting-toy", "gripper", "ur5"],
            keyframe_file="ball_sorting_toy_new.frame.yaml",
        ),
        strict=strict,
    )
    add_env(
        env_id="BallSortingToyNew-ball_random-gsplat-mit_medical_wood_chair",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer = make_schema,
            task=BallRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist", "stereo_far_left", "stereo_far_right"],
            mode="gsplat",
            gsplat_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/splats/mit_medical_wood_chair",
            transform_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/ball_sorting_toy_new/mit_medical_wood_chair",
            invisible_prefix=["cylinder-blue", "cylinder-orange", "ball-sorting-toy", "gripper", "ur5"],
            keyframe_file="ball_sorting_toy_new.frame.yaml",
        ),
        strict=strict,
    )
    add_env(
        env_id="BallSortingToyNew-ball_random-gsplat-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer = make_schema,
            task=BallRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist", "stereo_far_left", "stereo_far_right"],
            mode="gsplat",
            dataset_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/ball_toy/cic_lunette_bookshelf_3",
            invisible_prefix=["cylinder-blue", "cylinder-orange", "ball-sorting-toy", "gripper", "ur5"],
            keyframe_file="ball_sorting_toy_new.frame.yaml",
        ),
        strict=strict,
    )
    add_env(
        env_id="BallSortingToyNew-ball_random-gsplat-v2",
        entrypoint=make_env,
        kwargs=dict(
            xml_renderer = make_schema,
            task=BallRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist", "stereo_far_left", "stereo_far_right"],
            mode="gsplat",
            dataset_path=f"{os.environ['LUCIDSIM_EVAL_DATASETS']}/ball_toy/cic_kitchen_v3",
            invisible_prefix=["cylinder-blue", "cylinder-orange", "ball-sorting-toy", "gripper", "ur5"],
            keyframe_file="ball_sorting_toy_new.frame.yaml",
        ),
        strict=strict,
    )


if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Save

    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

from pathlib import Path

import numpy as np

from vuer_mujoco.schemas.objects.mj_sdf import MjSDF
from vuer_mujoco.tasks._floating_robotiq import FloatingRobotiq2f85
from vuer_mujoco.schemas.components.rigs.camera_rig import make_camera_rig
from vuer_mujoco.schemas.components.concrete_slab import ConcreteSlab
from vuer_mujoco.tasks.base.lucidxr_task import get_site
from vuer_mujoco.tasks.base.mocap_task import MocapTask
from itertools import combinations
from math import hypot
import random

# scene center is 0.41 + 0.2 / 2 = 0.50
x1, y1 = -0.25, -0.05
x2, y2 = 0, 0.05
x3, y3 = -0.05, -0.15
x4, y4 = -0.2, -0.14


def sample_three_points(
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
        idx = random.sample(list(candidate_indices), k=3)
        pts = grid[idx]

        # pair-wise separation constraint
        if all(hypot(*(a - b)) > eps for a, b in combinations(pts, 2)):
            return [tuple(p) for p in pts]

    raise ValueError("Unable to find three points satisfying all constraints; " "relax `eps` / `exclude_radius` or enlarge the grid.")


def make_schema(**options):
    from vuer_mujoco.schemas.utils.file import Prettify
    from vuer_mujoco.schemas.objects.cylinder import Cylinder

    cameras = make_camera_rig(pos=[-0.8, 0, 0.7])
    table = ConcreteSlab(pos=[0, 0, 0.6], rgba="0.8 0.8 0.8 1")

    box = MjSDF(
        pos=[x2, y2, 0.65],
        quat=[0.677739, 0.682136, -0.201568, -0.186361],
        assets="ball_sorting_toy",
        _attributes={"name": "ball-sorting-toy", "quat": "0.707 0.707 0 0"},
        scale="0.12 0.12 0.12",
    )
    #
    ball_1 = Cylinder(
        pos=[x1, y1, 0.62],
        quat=[0, 0, 1, 0],
        rgba="1 0 0 1",
        _attributes={
            "name": "cylinder-1",
        },
    )
    ball_2 = Cylinder(
        pos=[x3, y3, 0.62],
        quat=[0, 0, 1, 0],
        rgba="0 0 1 1",
        _attributes={
            "name": "cylinder-2",
        },
    )
    ball_3 = Cylinder(
        pos=[x4, y4, 0.62],
        quat=[0, 0, 1, 0],
        rgba="0 1 0 1",
        _attributes={
            "name": "cylinder-3",
        },
    )

    scene = FloatingRobotiq2f85(
        box,
        ball_1,
        ball_2,
        ball_3,
        table,
        cameras.right_camera,
        cameras.right_camera_r,
        cameras.front_camera,
        cameras.top_camera,
        cameras.left_camera,
        cameras.back_camera,
        pos=[0, 0, 0.79],
    )

    return scene._xml | Prettify()


class Fixed(MocapTask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.box_site = None
        self.start_area_site = None
        self.goal_area_site = None
        self.gripper_site = None
        self.set_sites()

        all_geom_names = [f"{self.physics.model.geom(i).name}_{i}" for i in range(self.physics.model.ngeom)]
        self.geom_name2id = {name: i for i, name in enumerate(all_geom_names)}

    def set_sites(self):
        self.gripper_site = get_site(self.physics, "gripper-pinch")

    def get_reward(self, physics):
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
    ball_qpos_addrs = [7, 14, 21]
    d = 0.02
    initial_pos = [x2, y2, 0.85]
    x_bounds = [-0.22, 0.22]
    y_bounds = [-0.22, 0.22]

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
        points = sample_three_points(
            xmin=cls.xmin,
            xmax=cls.xmax,
            ymin=cls.ymin,
            ymax=cls.ymax,
            d=cls.d,
            eps=cls.eps,
            exclude_center=[x2, y2],
            exclude_radius=0.16,
        )

        new_qpos = qpos.copy()
        for ball_addr in cls.ball_qpos_addrs:
            x, y = points.pop()
            new_qpos[ball_addr] = x
            new_qpos[ball_addr + 1] = y
            new_qpos[ball_addr + 2] = 0.62

        if mocap_pos is not None:
            mocap_pos = mocap_pos.copy()
            mocap_pos += np.random.normal(0.0, 0.005, mocap_pos.shape)

        return dict(qpos=new_qpos, quat=quat, mocap_pos=mocap_pos, **kwargs)


def register():
    from vuer_mujoco.tasks import add_env
    from vuer_mujoco.tasks.entrypoint import make_env

    add_env(
        env_id="BallSortingToy-fixed-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="ball_sorting_toy.mjcf.xml",
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist", "front", "right_r"],
        ),
    )
    add_env(
        env_id="BallSortingToy-color_random-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="ball_sorting_toy.mjcf.xml",
            task=ColorRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist", "front", "right_r"],
        ),
    )
    add_env(
        env_id="BallSortingToy-ball_random-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="ball_sorting_toy.mjcf.xml",
            task=BallRandom,
            workdir=Path(__file__).parent,
            camera_names=["left", "right", "wrist", "front", "right_r"],
        ),
    )
    add_env(
        env_id="BallSortingToy-fixed-lucid-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_render_options=dict(mode="lucid"),
            workdir=Path(__file__).parent,
            mode="lucid",
            prefix_to_class_ids={"ball-1": 148, "table": 100, "ball-2": 148, "ball-sorting-toy": 41},
            object_prefix="mug",
        ),
    )


if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Save

    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

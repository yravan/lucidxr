import copy
import random
from typing import Dict

import numpy as np

from source.gripper_se3 import GripperTrajectory
from source.se3_trajectory import SE3Transform
from source.utils import init_states, is_in_rect
from vuer_mujoco.tasks.utensil_drawer import Random

from scipy.signal import savgol_filter

def smooth_velocity(positions: np.ndarray, window: int = 7, polyorder: int = 2) -> np.ndarray:
    """Compute smoothed velocity with Savitzky–Golay filtering."""
    # Apply filter to positions, then differentiate
    smoothed_positions = savgol_filter(positions, window, polyorder, axis=0)
    vel = np.gradient(smoothed_positions, axis=0)
    return vel

center = 0
xy_limits = [center - 0.2, center], [-0.1, 0.1]
x2, y2 = center + 0.17, 0.0
xy_reject = [x2 - 0.11, x2 + 0.11], [y2 - 0.11, y2 + 0.11]
available_poses = None

def get_utensil_drawer_keypoints(
    traj: "GripperTrajectory",
    grip_threshold: float = 0.2,
    frame_skip: int = 30,
) -> Dict[str, int]:
    """
    Return keypoint indices [first, second, third] for a GripperTrajectory.

    - first  = 0
    - second = index with lowest Z (min z position)
    - third  = first index >= second + min_gap_after_second with ctrl < grip_threshold
              (falls back to last index if not found)

    Parameters
    ----------
    traj : GripperTrajectory
        Trajectory of GripperPose (expects each transform to have .position and .ctrl)
    grip_threshold : float
        Threshold on ctrl to declare "gripper closed" (default 0.2)
    min_gap_after_second : int
        Minimum number of frames to skip after `second` before searching for `third`

    Returns
    -------
    List[int] : [first, second, third]
    """
    N = len(traj.transforms)
    assert N >= 1, "Empty trajectory"

    start = 0

    start_position = traj[start].position
    vel = smooth_velocity(traj.positions)

    handle_grasp = np.argmax(traj.ctrls[frame_skip:] > 0.8) + frame_skip
    handle_grasp_position = traj[handle_grasp].position

    handle_release = np.argmax(np.logical_and(vel[handle_grasp:, 2] > 0, traj.ctrls[handle_grasp:] < 0.8)) + handle_grasp
    handle_release_position = traj[handle_release].position

    # mask = traj.ctrls[handle_release:] > 0.5
    # valid_indices = np.flatnonzero(mask)  # indices (relative to handle_release) where mask is True
    # spoon_grasp = handle_release + valid_indices[np.argmax(traj.positions[handle_release:, 0][mask])]
    spoon_grasp = np.argmax(traj.ctrls[handle_release:] > 0.75) + handle_release

    spoon_release = np.argmax(traj.ctrls[spoon_grasp:] < 0.2) + spoon_grasp

    drawer_push = np.argmax(np.logical_and(traj.positions[spoon_release + 20:, 0] > handle_release_position[0], vel[spoon_release + 20:, 0] > 0, traj.ctrls[spoon_release + 20:] > 0.8)) + spoon_release + 20

    drawer_push_end = np.argmax(vel[drawer_push:, 0] < 0) + drawer_push

    end = N - 1

    return {
        "start": start,
        "handle_grasp": handle_grasp,
        "handle_release": handle_release,
        "spoon_grasp": spoon_grasp,
        "spoon_release": spoon_release,
        "drawer_push": drawer_push,
        "drawer_push_end": drawer_push_end,
        "end": end,
    }


def generate_utensil_drawer_poses(
    traj: "GripperTrajectory", keypoints: Dict[str, int], metadata: Dict[str, np.ndarray]
) -> Dict[str, int]:
    global available_poses
    new_poses = {}
    metadata = copy.deepcopy(metadata)

    start = keypoints["start"]
    start_position = traj[start]
    new_start_position = copy.deepcopy(start_position)
    new_start_position.position += np.random.uniform(low=-0.02, high=0.02, size=3)
    new_poses["start"] = new_start_position

    handle_grasp = keypoints["handle_grasp"]
    handle_grasp_position = traj[handle_grasp]
    new_handle_grasp_position = copy.deepcopy(handle_grasp_position)
    new_handle_grasp_position.position[0] += np.random.uniform(low=-0.005, high=0.005)
    # randomize the z along the handle
    handle_y_bounds = [-0.1735, -0.0465]
    new_handle_grasp_position.position[1] = np.random.uniform(low=handle_y_bounds[0], high=handle_y_bounds[1])
    new_poses["handle_grasp"] = new_handle_grasp_position

    handle_release = keypoints["handle_release"]
    handle_release_position = traj[handle_release]
    new_handle_release_position = copy.deepcopy(handle_release_position)
    new_handle_grasp_position.position[[0]] += np.random.uniform(low=-0.005, high=0.005)
    new_handle_release_position.position[1] = new_handle_grasp_position.position[1] + np.random.uniform(low=-0.005, high=0.005)
    new_poses["handle_release"] = new_handle_release_position

    initial_qpos = metadata["initial_qpos"]
    new_qpos = Random.random_state(qpos=initial_qpos)["qpos"]
    new_qpos = np.array(new_qpos)
    initial_qpos = np.array(initial_qpos)
    delta_x, delta_y = new_qpos[Random.spoon_qpos_addr:Random.spoon_qpos_addr+2] - initial_qpos[Random.spoon_qpos_addr:Random.spoon_qpos_addr+2]
    metadata["initial_qpos"] = new_qpos

    spoon_grasp  = keypoints["spoon_grasp"]
    new_spoon_grasp_position = copy.deepcopy(traj[spoon_grasp])
    new_spoon_grasp_position.position[0:2] += np.array([delta_x, delta_y])
    # new_spoon_grasp_position.position += np.random.uniform(low=-0.003, high=0.003, size=3)
    new_poses["spoon_grasp"] = new_spoon_grasp_position
    print(initial_qpos[Random.spoon_qpos_addr:Random.spoon_qpos_addr+3], traj[spoon_grasp].position)

    spoon_release = keypoints["spoon_release"]
    spoon_release_position = traj[spoon_release]
    new_spoon_release_position = copy.deepcopy(spoon_release_position)
    new_spoon_release_position.position[0:2] += np.random.uniform(low=-0.05, high=0.05, size=2)
    new_spoon_release_position.position[2] += np.random.uniform(low=-0.02, high=0.02)
    new_poses["spoon_release"] = new_spoon_release_position

    drawer_push = keypoints["drawer_push"]
    drawer_push_position = traj[drawer_push]
    new_drawer_push_position = copy.deepcopy(drawer_push_position)
    new_drawer_push_position.position[[0,2]] += np.random.uniform(low=-0.02, high=0.02, size=2)
    new_drawer_push_position.position[1] = np.random.uniform(low=handle_y_bounds[0], high=handle_y_bounds[1])
    new_poses["drawer_push"] = new_drawer_push_position

    drawer_push_end = keypoints["drawer_push_end"]
    drawer_push_end_position = traj[drawer_push_end]
    new_drawer_push_end_position = copy.deepcopy(drawer_push_end_position)
    new_drawer_push_end_position.position[[0,2]] += np.random.uniform(low=-0.02, high=0.02, size=2)
    new_drawer_push_end_position.position[1] = new_drawer_push_position.position[1] + np.random.uniform(low=-0.03, high=0.03)
    new_poses["drawer_push_end"] = new_drawer_push_end_position

    end = keypoints["end"]
    end_position = traj[end]
    new_end_position = copy.deepcopy(end_position)
    new_end_position.position += np.random.uniform(low=-0.02, high=0.02, size=3)
    new_poses["end"] = new_end_position

    return new_poses, metadata


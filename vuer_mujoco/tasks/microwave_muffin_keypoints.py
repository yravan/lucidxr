import copy
import random
from typing import Dict

import numpy as np

from source.gripper_se3 import GripperTrajectory
from source.se3_trajectory import SE3Transform
from source.utils import init_states, is_in_rect
from vuer_mujoco.tasks.microwave_muffin import Random

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

def get_microwave_muffin_keypoints(
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

    handle_grasp = np.argmax(np.logical_and(traj.ctrls[frame_skip:] > 0.5, vel[frame_skip:, 0] < 0, vel[frame_skip:, 1] > 0)) + frame_skip
    handle_grasp_position = traj[handle_grasp].position

    handle_release = np.argmax(np.logical_and(traj.positions[handle_grasp:, 0] < start_position[0], vel[handle_grasp:, 1] < 0, traj.ctrls[handle_grasp:] < 0.5)) + handle_grasp
    handle_release_position = traj[handle_release].position

    muffin_grasp = np.argmax(np.logical_and(traj.ctrls[handle_release:] > 0.5, traj.positions[handle_release:, 0] > handle_grasp_position[0])) + handle_release

    muffin_release = np.argmax(traj.ctrls[muffin_grasp:] < 0.2) + muffin_grasp

    microwave_push = np.argmax(np.logical_and(vel[muffin_release:, 0] > 0, vel[muffin_release:, 1] < 0)) + muffin_release

    microwave_push_end = np.argmax(vel[microwave_push:, 0] < 0) + microwave_push

    end = N - 1

    return {
        "start": start,
        "handle_grasp": handle_grasp,
        "handle_release": handle_release,
        "muffin_grasp": muffin_grasp,
        "muffin_release": muffin_release,
        "microwave_push": microwave_push,
        "microwave_push_end": microwave_push_end,
        "end": end,
    }


def generate_microwave_muffin_poses(
    traj: "GripperTrajectory", keypoints: Dict[str, int], metadata: Dict[str, np.ndarray]
) -> Dict[str, int]:
    global available_poses
    new_poses = {}


    start = keypoints["start"]
    start_position = traj[start]
    new_start_position = copy.deepcopy(start_position)
    new_start_position.position += np.random.uniform(low=-0.02, high=0.02, size=3)
    new_poses["start"] = new_start_position

    handle_grasp = keypoints["handle_grasp"]
    handle_grasp_position = traj[handle_grasp]
    new_handle_grasp_position = copy.deepcopy(handle_grasp_position)
    new_handle_grasp_position.position[1] += np.random.uniform(low=-0.005, high=0.005)
    # randomize the z along the handle
    handle_z_bounds = [0.85, 0.97]
    new_handle_grasp_position.position[2] = np.random.uniform(low=handle_z_bounds[0], high=handle_z_bounds[1])
    new_poses["handle_grasp"] = new_handle_grasp_position

    handle_release = keypoints["handle_release"]
    handle_release_position = traj[handle_release]
    new_handle_release_position = copy.deepcopy(handle_release_position)
    new_handle_release_position.position[0:2] += np.random.uniform(low=-0.01, high=0.01, size=2)
    new_handle_release_position.position[2] = new_handle_grasp_position.position[2]  # keep the same z as grasp
    new_poses["handle_release"] = new_handle_release_position


    initial_qpos = metadata["initial_qpos"]
    new_qpos = Random.random_state(qpos=initial_qpos)["qpos"]
    new_qpos = np.array(new_qpos)
    initial_qpos = np.array(initial_qpos)
    delta_x, delta_y = new_qpos[Random.box_qpos_addr:Random.box_qpos_addr+2] - initial_qpos[Random.box_qpos_addr:Random.box_qpos_addr+2]
    metadata["initial_qpos"] = new_qpos

    muffin_grasp  = keypoints["muffin_grasp"]
    new_muffin_grasp_position = copy.deepcopy(traj[muffin_grasp])
    new_muffin_grasp_position.position[0:2] += np.array([delta_x, delta_y])
    # new_muffin_grasp_position.position += np.random.uniform(low=-0.003, high=0.003, size=3)
    new_poses["muffin_grasp"] = new_muffin_grasp_position

    muffin_release = keypoints["muffin_release"]
    muffin_release_position = traj[muffin_release]
    new_muffin_release_position = copy.deepcopy(muffin_release_position)
    new_muffin_release_position.position[0:2] += np.random.uniform(low=-0.05, high=0.0, size=2)
    new_muffin_release_position.position[2] += np.random.uniform(low=-0.005, high=0.01)
    new_poses["muffin_release"] = new_muffin_release_position

    microwave_push = keypoints["microwave_push"]
    microwave_push_position = traj[microwave_push]
    new_microwave_push_position = copy.deepcopy(microwave_push_position)
    new_microwave_push_position.position[0:2] += np.random.uniform(low=-0.02, high=0.02, size=2)
    new_microwave_push_position.position[2] = np.random.uniform(low=handle_z_bounds[0], high=handle_z_bounds[1])
    new_poses["microwave_push"] = new_microwave_push_position

    microwave_push_end = keypoints["microwave_push_end"]
    microwave_push_end_position = traj[microwave_push_end]
    new_microwave_push_end_position = copy.deepcopy(microwave_push_end_position)
    new_microwave_push_end_position.position[0:2] += np.random.uniform(low=-0.02, high=0.02, size=2)
    new_microwave_push_end_position.position[2] = new_microwave_push_position.position[2] + np.random.uniform(low=-0.03, high=0.03)
    new_poses["microwave_push_end"] = new_microwave_push_end_position

    end = keypoints["end"]
    end_position = traj[end]
    new_end_position = copy.deepcopy(end_position)
    new_end_position.position += np.random.uniform(low=-0.02, high=0.02, size=3)
    new_poses["end"] = new_end_position

    return new_poses, metadata


import copy
import random
from typing import Dict

import numpy as np

from source.gripper_se3 import GripperTrajectory
from source.se3_trajectory import SE3Transform
from source.utils import init_states, is_in_rect

center = 0
xy_limits = [center - 0.2, center], [-0.1, 0.1]
x2, y2 = center + 0.17, 0.0
xy_reject = [x2 - 0.11, x2 + 0.11], [y2 - 0.11, y2 + 0.11]
available_poses = None

def get_mug_tree_keypoints(
    traj: "GripperTrajectory",
    grip_threshold: float = 0.2,
    min_gap_after_second: int = 30,
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

    # Positions (N,3) and ctrls (N,)
    positions = np.stack([T.position for T in traj.transforms], axis=0)  # (x,y,z)
    ctrls = np.array([getattr(T, "ctrl", np.nan) for T in traj.transforms], dtype=float)

    first = 0

    # Robust min-Z (handles NaNs by treating them as +inf so they won't be picked)
    z = positions[:, 2]
    z_safe = np.where(np.isfinite(z), z, np.inf)
    second = int(np.argmin(z_safe))

    # Search for first ctrl < threshold after a gap
    start = min(second + max(0, int(min_gap_after_second)), N - 1)
    # Valid finite ctrl values
    mask_valid = np.isfinite(ctrls[start:])
    mask_closed = (ctrls[start:] < grip_threshold) & mask_valid
    idxs = np.nonzero(mask_closed)[0]
    third = int(start + idxs[0]) if idxs.size > 0 else N - 1

    # Ensure strictly increasing (clamp if needed)
    if second <= first:
        second = min(first + 1, N - 1)
    if third <= second:
        third = min(second + 1, N - 1)

    return {
        "start": first,
        "mug_grasp": second,
        "mug_place": third,
    }


def generate_mug_tree_poses(
    traj: "GripperTrajectory", keypoints: Dict[str, int], metadata: Dict[str, np.ndarray]
) -> Dict[str, int]:
    global available_poses
    new_poses = {}


    first = keypoints["start"]
    gripper_position = traj[first]
    new_gripper_position = copy.deepcopy(gripper_position)

    new_gripper_position.position[0:2] += np.random.uniform(low=-0.01, high=0.01, size=2)
    new_gripper_position.position[2] = 1.1496423721313477

    new_poses["start"] = new_gripper_position


    second = keypoints["mug_grasp"]
    initial_qpos = metadata["initial_qpos"]
    mug_pose = initial_qpos[7:10]
    if not available_poses:
        available_poses = init_states(xy_limits, 0.01, xy_reject)
        random.shuffle(available_poses)
    x2, y2 = available_poses.pop()
    noise = np.random.uniform(-0.005, 0.005, size=2)
    while not is_in_rect(x2 + noise[0], y2 + noise[1], xy_limits):
        noise = np.random.uniform(-0.005, 0.005, size=2)
    x2, y2 = x2 + noise[0], y2 + noise[1]
    new_mug_pose = np.array([x2, y2, mug_pose[2]])
    metadata["initial_qpos"][7:10] = new_mug_pose
    displacement = SE3Transform(new_mug_pose - mug_pose, np.array([0, 0, 0, 1]))
    grasp_position = traj[second]
    new_grasp_position = displacement * copy.deepcopy(grasp_position)

    new_poses["mug_grasp"] = new_grasp_position

    third = keypoints["mug_place"]
    place_pose = traj[third]
    new_third_position = copy.deepcopy(place_pose)
    new_poses["mug_place"] = new_third_position

    return new_poses, metadata


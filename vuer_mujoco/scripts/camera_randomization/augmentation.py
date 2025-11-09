import numpy as np
from scipy.spatial.transform import Rotation as R  # pip install scipy, if needed

from vuer_mujoco.scripts.camera_randomization.utils import load_cam_video, aug_reverse_batched, warp_forward_zbuffer_batched
import math
import torch


class CameraRandomization:
    position_perturbation_size = 0.01  # metres
    rotation_perturbation_size = 0.087  # ≈5° in radians
    fovy_perturbation_size = 5.0  # degrees

    # hard coded for now,
    near = 0.02
    far = 1.9


def recover_metric_depth(
    *,
    n_depth,
):
    d = n_depth / 255
    d = d * (CameraRandomization.far - CameraRandomization.near) + CameraRandomization.near
    valid_mask = torch.logical_and(d > CameraRandomization.near, d < CameraRandomization.far)
    return d, valid_mask


def _random_small_rotation(max_angle_rad: float) -> np.ndarray:
    """
    Draw a random 3-D rotation with magnitude ≤ max_angle_rad (axis-angle).
    Returns a 3×3 rotation matrix.
    """
    axis = np.random.normal(size=3)
    axis /= np.linalg.norm(axis) + 1e-12  # random unit axis
    angle = np.random.uniform(-max_angle_rad, max_angle_rad)
    return R.from_rotvec(axis * angle).as_matrix()


def _perturb_fovy_and_K(K: np.ndarray, fovy_delta_deg: float) -> np.ndarray:
    """
    Given an intrinsic matrix K (fx, fy, cx, cy) and a desired Δfovy,
    scale fx and fy so that the vertical FOV changes by that amount.
    Assumes the principal point is roughly at the image centre so that
    image height ≈ 2·cy.
    """
    K_new = K.copy()
    fy = K[1, 1]
    cy = K[1, 2]
    H = 2.0 * cy  # approximate image height
    fovy0 = 2.0 * np.arctan(H / (2.0 * fy))  # current vertical FOV (rad)

    fovy_new = fovy0 + np.deg2rad(fovy_delta_deg)
    fovy_new = np.clip(fovy_new, 1e-3, np.deg2rad(179.0))  # avoid singularities

    scale = np.tan(fovy_new / 2.0) / np.tan(fovy0 / 2.0)  # >1 if FOV widens
    K_new[0, 0] = K[0, 0] / scale  # fx'
    K_new[1, 1] = fy / scale  # fy'
    return K_new


def sample_poses_batch(c2ws: torch.Tensor, Ks: torch.Tensor):
    """
    Perturb a batch of camera extrinsics (c2ws, B×4×4) and intrinsics (Ks, B×3×3).

    Returns
    -------
    c2ws_new : (B,4,4)
    Ks_new   : (B,3,3)
    """
    B, *_ = c2ws.shape
    device, dtype = c2ws.device, c2ws.dtype
    eps = 1e-9

    # ------------------------------------------------ translation ----------------
    delta_pos = (torch.rand(B, 3, device=device, dtype=dtype) * 2.0 - 1.0) * CameraRandomization.position_perturbation_size  # (B,3)

    # ------------------------------------------------ rotation -------------------
    # random axis (unit) and small angle
    axis = torch.randn(B, 3, device=device, dtype=dtype)
    axis = axis / (axis.norm(dim=-1, keepdim=True) + eps)  # (B,3)

    angle = (torch.rand(B, 1, device=device, dtype=dtype) * 2.0 - 1.0) * CameraRandomization.rotation_perturbation_size  # (B,1)

    cos, sin = torch.cos(angle), torch.sin(angle)  # (B,1)
    one_mc = 1.0 - cos

    # split axis components as (B,1) each
    x = axis[:, 0:1]
    y = axis[:, 1:2]
    z = axis[:, 2:3]

    # Rodrigues – build ΔR (B,3,3) without broadcasting conflicts
    R_delta = torch.empty(B, 3, 3, device=device, dtype=dtype)
    R_delta[:, 0, 0] = (cos + x * x * one_mc).squeeze(-1)
    R_delta[:, 0, 1] = (x * y * one_mc - z * sin).squeeze(-1)
    R_delta[:, 0, 2] = (x * z * one_mc + y * sin).squeeze(-1)

    R_delta[:, 1, 0] = (y * x * one_mc + z * sin).squeeze(-1)
    R_delta[:, 1, 1] = (cos + y * y * one_mc).squeeze(-1)
    R_delta[:, 1, 2] = (y * z * one_mc - x * sin).squeeze(-1)

    R_delta[:, 2, 0] = (z * x * one_mc - y * sin).squeeze(-1)
    R_delta[:, 2, 1] = (z * y * one_mc + x * sin).squeeze(-1)
    R_delta[:, 2, 2] = (cos + z * z * one_mc).squeeze(-1)

    # apply to extrinsics
    R_orig = c2ws[:, :3, :3]  # (B,3,3)
    t_orig = c2ws[:, :3, 3]  # (B,3)

    R_new = torch.bmm(R_delta, R_orig)  # (B,3,3)
    t_new = t_orig + delta_pos  # (B,3)

    c2ws_new = c2ws.clone()
    c2ws_new[:, :3, :3] = R_new
    c2ws_new[:, :3, 3] = t_new

    # ---------------------------------------------- FOV / intrinsics ------------
    fx, fy = Ks[:, 0, 0], Ks[:, 1, 1]  # (B,)
    cx, cy = Ks[:, 0, 2], Ks[:, 1, 2]
    H = 2.0 * cy  # (B,)

    fovy0 = 2.0 * torch.atan(H / (2.0 * fy))  # (B,)
    delta_deg = (torch.rand(B, device=device, dtype=dtype) * 2.0 - 1.0) * CameraRandomization.fovy_perturbation_size  # (B,)
    fovy_new = fovy0 + torch.deg2rad(delta_deg)
    fovy_new = torch.clamp(fovy_new, min=1e-3, max=math.radians(179.0))  # (B,)

    scale = torch.tan(fovy_new / 2.0) / torch.tan(fovy0 / 2.0)  # (B,)

    Ks_new = Ks.clone()
    Ks_new[:, 0, 0] = fx / scale
    Ks_new[:, 1, 1] = fy / scale
    # principal point (cx, cy) unchanged

    return c2ws_new, Ks_new


def sample_pose(c2w: np.ndarray, K: np.ndarray):
    """
    Randomly perturb a camera pose and intrinsics.

    Parameters
    ----------
    c2w : (4,4) array_like
        Original camera-to-world transform.
    K   : (3,3) array_like
        Original intrinsic matrix.

    Returns
    -------
    c2w_new : (4,4) np.ndarray
        Perturbed camera-to-world matrix.
    K_new   : (3,3) np.ndarray
        Perturbed intrinsic matrix.
    """
    # --- translation perturbation -------------------------------------------------
    delta_pos = np.random.uniform(
        low=-CameraRandomization.position_perturbation_size,
        high=CameraRandomization.position_perturbation_size,
        size=3,
    )

    # --- rotation perturbation ----------------------------------------------------
    delta_rot = _random_small_rotation(CameraRandomization.rotation_perturbation_size)

    # Apply rotation in camera frame (i.e. R' = ΔR · R)
    R_orig = c2w[:3, :3]
    t_orig = c2w[:3, 3]
    R_new = delta_rot @ R_orig
    t_new = t_orig + delta_pos

    c2w_new = np.eye(4, dtype=c2w.dtype)
    c2w_new[:3, :3] = R_new
    c2w_new[:3, 3] = t_new

    # --- FOV perturbation ---------------------------------------------------------
    delta_fovy_deg = np.random.uniform(
        -CameraRandomization.fovy_perturbation_size,
        CameraRandomization.fovy_perturbation_size,
    )
    K_new = _perturb_fovy_and_K(K, delta_fovy_deg)

    return c2w_new, K_new


if __name__ == "__main__":
    from ml_logger import ML_Logger
    import torch

    loader = ML_Logger(prefix="lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree_ur/2025/07/01/12.23.54")

    episode_key = "data/ep_00001.h5"
    cam_key = "left"
    Ks, c2ws = loader.load_h5(episode_key + f":{cam_key}/K,{cam_key}/C2W")

    rgb_stream, num_frames = load_cam_video(loader, f"{cam_key}/rgb", episode_key)
    depth_stream, num_frames = load_cam_video(loader, f"{cam_key}/lucid/midas_depth_full", episode_key)

    metric_depth_stream, _ = recover_metric_depth(
        n_depth=torch.from_numpy(depth_stream[..., 0]),
        # near=CameraRandomization.near,
        # far=CameraRandomization.far,
    )

    ###################################################################################3

    def get_batch():
        idxs = [*range(64)]
        T_olds = c2ws[idxs]
        K_olds = Ks[idxs]
        depth_olds = metric_depth_stream[idxs]
        rgb_olds = rgb_stream[idxs]

        T_news = []
        K_news = []
        for T_old, K_old in zip(T_olds, K_olds):
            c2w_new, K_new = sample_pose(T_old, K_old)
            T_news.append(c2w_new)
            K_news.append(K_new)

        # convert to batched tensors
        T_olds = torch.from_numpy(np.stack(T_olds)).cuda().float()
        T_news = torch.from_numpy(np.stack(T_news)).cuda().float()
        K_olds = torch.from_numpy(np.stack(K_olds)).cuda().float()
        K_news = torch.from_numpy(np.stack(K_news)).cuda().float()
        depth_olds = torch.from_numpy(np.stack(depth_olds)).cuda().float()
        rgb_olds = torch.from_numpy(np.stack(rgb_olds)).cuda().float().permute(0, 3, 1, 2) / 255.0  # (B, C, H, W)

        return dict(
            T_old=T_olds,
            T_new=T_news,
            K_old=K_olds,
            K_new=K_news,
            depth_old=depth_olds,
        ), rgb_olds

    from ml_logger import logger

    logger.split("t")
    kwargs, rgb_olds = get_batch()
    print(logger.split("t"))
    flow_t, viz = aug_reverse_batched(**kwargs, return_viz=True)
    print(logger.split("t"))
    warped, _ = warp_forward_zbuffer_batched(rgb_olds, flow_t, kwargs["depth_old"][:, None], tol_abs=1_000, tol_rel=1_000)
    print(logger.split("t"))
    # kwargs["depth_old.shape"]
    #
    # convert to numpy for visualization
    from matplotlib import pyplot as plt
    warped_np = warped.permute(0, 2, 3, 1).cpu().numpy()
    for i in range(warped_np.shape[0]):
        plt.imshow(warped_np[i])
        plt.show()

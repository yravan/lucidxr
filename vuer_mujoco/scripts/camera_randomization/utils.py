"""
Augment camera poses by randomizing position, rotation, and fov.
Save as additional datasets
"""

from pathlib import Path
import numpy as np
import imageio
import sys
from torchvision.utils import flow_to_image
import torch
import torch.nn.functional as F

# 1.  Alias the parent package
sys.modules["numpy._core"] = np.core

# 2.  Alias *every* already-loaded sub-module
core_prefix = "numpy.core."
for name, mod in list(sys.modules.items()):
    if name.startswith(core_prefix):
        sys.modules["numpy._core." + name[len(core_prefix) :]] = mod


# def aug(
#     *,
#     T_old,
#     T_new,
#     K,
#     depth_new,
#     img_old,
#     device="cuda",
# ):
#     frame = torch.from_numpy(depth_new).to(device=device).float()
#     frame = torch.where(frame >= far, torch.tensor(1_000, device=device), frame)
# 
#     height, width = img_old.shape[0:2]
#     cx, cy = K[0, 2], K[1, 2]
#     us = torch.arange(width, device=device).float() + 0.5
#     vs = torch.arange(height, device=device).float() + 0.5
#     f_px = K[0, 0]  # focal length in pixels
# 
#     us, vs = torch.meshgrid(us, vs, indexing="xy")
#     us.to(device=device)
#     vs.to(device=device)
# 
#     K = torch.from_numpy(K).to(device=device).float()
# 
#     # sample camera
#     xs = frame * (us - cx) / f_px
#     ys = frame * (vs - cy) / f_px
#     current_samples = torch.stack([xs, ys, frame], axis=-1)  # shape (height, width, 3)
# 
#     T_new = torch.from_numpy(T_new).to(device=device).float()
#     T_old = torch.from_numpy(T_old).to(device=device).float()
#     T_old_to_new = torch.linalg.inv(T_new) @ T_old
# 
#     current_samples_h = torch.cat([current_samples, torch.ones((height, width, 1), dtype=torch.float32, device=device)], axis=-1).reshape(
#         -1, 4
#     )
# 
#     samples_to_prev = current_samples_h @ torch.linalg.inv(T_old_to_new).T
#     samples_to_prev_px = samples_to_prev[..., :3] @ K.T
# 
#     samples_to_prev_px = samples_to_prev_px / samples_to_prev_px[..., 2:]
#     samples_to_prev_px = samples_to_prev_px.reshape(height, width, 3)
# 
#     dxs = samples_to_prev_px[..., 0] - us
#     dys = samples_to_prev_px[..., 1] - vs
# 
#     flow = torch.stack([dxs, dys], axis=-1)  # shape (height, width, 2)
#     flow_tensor = flow.permute(2, 0, 1)
#     flow_viz = flow_to_image(flow_tensor).permute(1, 2, 0).cpu().numpy()
# 
#     return flow_tensor, flow_viz


def aug_reverse(
    *,
    T_old,
    T_new,
    K_old,
    K_new,
    depth_old,  # (Ho,Wo)
    img_new,  # just for target size
    far=1_000.0,
    device="cuda",
):
    # tensors -------------------------------------------------
    depth_t = torch.as_tensor(depth_old, device=device, dtype=torch.float32)
    depth_t = torch.where(depth_t >= far, torch.tensor(far, device=device), depth_t)

    Kold = torch.as_tensor(K_old, device=device, dtype=torch.float32)
    Knew = torch.as_tensor(K_new, device=device, dtype=torch.float32)
    Told = torch.as_tensor(T_old, device=device, dtype=torch.float32)
    Tnew = torch.as_tensor(T_new, device=device, dtype=torch.float32)

    # pixel grid in the OLD image -----------------------------
    Ho, Wo = depth_t.shape
    fx_o, fy_o = Kold[0, 0], Kold[1, 1]
    cx_o, cy_o = Kold[0, 2], Kold[1, 2]

    u_o = torch.arange(Wo, device=device).float() + 0.5
    v_o = torch.arange(Ho, device=device).float() + 0.5
    u_o, v_o = torch.meshgrid(u_o, v_o, indexing="xy")

    x = depth_t * (u_o - cx_o) / fx_o
    y = depth_t * (v_o - cy_o) / fy_o
    pts_old = torch.stack((x, y, depth_t), dim=-1)  # (Ho,Wo,3)

    # transform to NEW camera --------------------------------
    T_old_to_new = torch.linalg.inv(Tnew) @ Told  # old→new
    pts_h = torch.cat((pts_old, torch.ones_like(depth_t)[..., None]), dim=-1).view(-1, 4)

    pts_new = (pts_h @ T_old_to_new.T)[..., :3]

    # project with K_new -------------------------------------
    px_new = pts_new @ Knew.T
    px_new = px_new[:, :2] / px_new[:, 2:3]
    px_new = px_new.view(Ho, Wo, 2)

    # flow on the OLD grid -----------------------------------
    dx = px_new[..., 0] - u_o
    dy = px_new[..., 1] - v_o
    flow = torch.stack((dx, dy), dim=-1)  # (Ho,Wo,2)

    flow_t = flow.permute(2, 0, 1)  # (2,Ho,Wo)
    flow_viz = flow_to_image(flow_t).permute(1, 2, 0).cpu().numpy()

    return flow_t, flow_viz


def aug_reverse_batched(
    *,
    T_old: torch.Tensor,  # (B,4,4)  C2W of old cameras
    T_new: torch.Tensor,  # (B,4,4)  C2W of new cameras
    K_old: torch.Tensor,  # (B,3,3)  intrinsics of old cams
    K_new: torch.Tensor,  # (B,3,3)  intrinsics of new cams
    depth_old: torch.Tensor,  # (B,H,W)  depth maps of old frames
    device: str = "cuda",
    far: float = 1_000.0,
    return_viz: bool = False,
):
    """
    Vectorised remake of `aug_reverse` (old → new).  All tensors must
    already be on `device` and of dtype `float32` or `float16`.

    Returns
    -------
    flow  : (B,2,H,W)  pixel flow   old → new   (dx, dy)
    viz   : (B,H,W,3)  RGB visualisation (only if return_viz=True)
    """
    B, H, W = depth_old.shape
    dtype = depth_old.dtype

    # ─── 0. clip depth & homogenise ------------------------------------------
    depth = depth_old.clamp(max=far)  # (B,H,W)

    # make the pixel grid once, then expand to B
    u = torch.arange(W, device=device, dtype=dtype) + 0.5  # (W,)
    v = torch.arange(H, device=device, dtype=dtype) + 0.5  # (H,)
    u, v = torch.meshgrid(u, v, indexing="xy")  # (H,W)

    u = u.unsqueeze(0).expand(B, -1, -1)  # (B,H,W)
    v = v.unsqueeze(0).expand(B, -1, -1)  # (B,H,W)

    # ─── 1. back-project in OLD cameras --------------------------------------
    fx_o, fy_o = K_old[:, 0, 0].view(B, 1, 1), K_old[:, 1, 1].view(B, 1, 1)
    cx_o, cy_o = K_old[:, 0, 2].view(B, 1, 1), K_old[:, 1, 2].view(B, 1, 1)

    x = depth * (u - cx_o) / fx_o
    y = depth * (v - cy_o) / fy_o
    pts_old = torch.stack((x, y, depth, torch.ones_like(depth)), dim=-1)  # (B,H,W,4)
    pts_flat = pts_old.view(B, -1, 4)  # (B,N,4)

    # ─── 2. transform to NEW cameras (batch bmm) -----------------------------
    T_old_to_new = torch.linalg.inv(T_new) @ T_old  # (B,4,4)
    pts_new = torch.bmm(pts_flat, T_old_to_new.transpose(1, 2))  # (B,N,4)
    pts_new = pts_new[..., :3]  # (B,N,3)

    # ─── 3. project with each K_new  ----------------------------------------
    px = torch.bmm(pts_new, K_new.transpose(1, 2))  # (B,N,3)
    px_xy = px[..., :2] / px[..., 2:3].clamp(min=1e-6)  # (B,N,2)
    px_xy = px_xy.view(B, H, W, 2)

    # ─── 4. flow  (old grid → new) ------------------------------------------
    dx = px_xy[..., 0] - u
    dy = px_xy[..., 1] - v
    flow = torch.stack((dx, dy), dim=1)  # (B,2,H,W)

    if not return_viz:
        return flow

    # torch-vision’s helper only handles 1 image at a time → loop on CPU
    viz = []
    for b in range(B):
        f_img = flow_to_image(flow[b]).permute(1, 2, 0).cpu()  # (H,W,3)
        viz.append(f_img)
    viz = torch.stack(viz)  # (B,H,W,3)

    return flow, viz


def load_cam_video(loader, image_key, episode_key):
    session_prefix = Path(episode_key).parent.parent
    stem = Path(episode_key).stem

    video_path = f"videos/{stem}/{image_key}.mp4"
    video_memory = loader.load_file(video_path)
    frames = list(imageio.v3.imiter(video_memory, plugin="pyav"))  # PyAV backend

    stacked = np.stack(frames, axis=0)
    return stacked, len(frames)


def zbuffer_visibility(
    depth_src: torch.Tensor,  # (B,1,H,W)
    flow_old_to_new: torch.Tensor,  # (B,2,H,W)
    tol_abs: float = 2e-3,  # 2 mm
    tol_rel: float = 0.01,  # 1 % of depth
):
    """
    Boolean mask that is True where the source pixel wins the Z-buffer
    *within a tolerance* (tol_abs + tol_rel·depth).
    """
    B, _, H, W = depth_src.shape
    device = depth_src.device
    N = H * W

    ys, xs = torch.meshgrid(
        torch.arange(H, device=device),
        torch.arange(W, device=device),
        indexing="ij",
    )
    xs = xs.flatten().float()  # (N,)
    ys = ys.flatten().float()

    depth_flat = depth_src.reshape(B, -1)  # (B,N)
    flow_flat = flow_old_to_new.reshape(B, 2, -1)  # (B,2,N)

    out = torch.zeros_like(depth_src, dtype=torch.bool)

    for b in range(B):
        u_new = xs + flow_flat[b, 0]  # float
        v_new = ys + flow_flat[b, 1]

        u_i = torch.round(u_new).long()
        v_i = torch.round(v_new).long()

        inside = (u_i >= 0) & (u_i < W) & (v_i >= 0) & (v_i < H)
        if inside.sum() == 0:
            continue

        idx_tgt = v_i[inside] * W + u_i[inside]  # flat index (M,)
        d_vals = depth_flat[b, inside]  # (M,)

        # ---- Z-buffer: nearest depth per target pixel ----
        min_depth = torch.full((N,), float("inf"), device=device)
        min_depth.scatter_reduce_(0, idx_tgt, d_vals, reduce="amin")

        tol = tol_abs + tol_rel * min_depth[idx_tgt]  # (M,)

        visible = d_vals <= min_depth[idx_tgt] + tol  # (M,) bool

        mask_full = torch.zeros(N, dtype=torch.bool, device=device)
        mask_full[inside] = visible
        out[b, 0] = mask_full.view(H, W)

    return out  # (B,1,H,W)


def warp_forward(
    img: torch.Tensor,
    flow: torch.Tensor,
    *,
    mode: str = "bilinear",
    padding_mode: str = "zeros",
    align_corners: bool = True,
    return_valid_mask: bool = False,
):
    """
    Warp an image with a per-pixel flow field (pixel units).

    Parameters
    ----------
    img  :  (B, C, H, W)   torch.float32 / float16  in [0,1] or [0,255]
           Image **that belongs to the flow’s reference frame**.
    flow :  (B, 2, H, W)   (dx, dy) in *pixels*.
           Same H, W, device & dtype as `img`.
           Positive dx moves a point *right*, positive dy moves it *down*.

    Returns
    -------
    warped : (B, C, H, W)  Sampled image.
    valid  : (B, 1, H, W)  Bool mask   (only if `return_valid_mask=True`)
            1 where the sampling grid stayed inside the image.
    """
    if img.dim() != 4 or flow.dim() != 4:
        raise ValueError("`img` and `flow` must be 4-D tensors (B,C,H,W / B,2,H,W).")

    B, C, H, W = img.shape
    # ---------- 1. build a base grid in normalised co-ordinates [-1, 1] ----------
    # y first, x second  (same order as grid_sample)
    ys, xs = torch.meshgrid(
        torch.linspace(-1.0, 1.0, H, device=img.device, dtype=img.dtype),
        torch.linspace(-1.0, 1.0, W, device=img.device, dtype=img.dtype),
        indexing="ij",
    )
    base_grid = torch.stack((xs, ys), dim=-1)  # (H, W, 2)
    base_grid = base_grid.unsqueeze(0).repeat(B, 1, 1, 1)  # (B, H, W, 2)

    # ---------- 2. convert pixel-flow → normalised flow ----------
    #   For align_corners=True:
    #       x_n =  2 * x_pix / (W-1)  − 1
    #   so Δx_n / Δx_pix =  2 / (W-1)
    norm_flow = torch.empty_like(flow)
    norm_flow[:, 0, :, :] = flow[:, 0, :, :] * (2.0 / max(W - 1, 1))  # dx
    norm_flow[:, 1, :, :] = flow[:, 1, :, :] * (2.0 / max(H - 1, 1))  # dy
    norm_flow = norm_flow.permute(0, 2, 3, 1)  # (B,H,W,2)

    # ---------- 3. add offset and sample ----------
    grid = base_grid + norm_flow  # (B, H, W, 2)
    warped = F.grid_sample(img, grid, mode=mode, padding_mode=padding_mode, align_corners=align_corners)

    if return_valid_mask:
        # Points inside the image have both co-ords in [-1, 1]
        valid = ((grid[..., 0].abs() <= 1.0) & (grid[..., 1].abs() <= 1.0)).unsqueeze(1)  # (B,1,H,W) bool
        return warped, valid

    return warped


def warp_forward_batched(
    img: torch.Tensor,  # (B,C,H,W)
    flow: torch.Tensor,  # (B,2,H,W)   dx, dy  (pixels)
    *,
    mode="bilinear",
    padding_mode="zeros",
    align_corners=True,
    return_valid_mask: bool = False,
):
    """
    Vectorised replacement for `warp_forward`.  The sign convention is
    unchanged: flow (dx,dy) tells where a *source* pixel moves in the
    *target* image, therefore to sample the source we pass **–flow**.
    """
    # if img.shape[:3] != flow.shape[:3]:
    #     raise ValueError("`img` and `flow` must share batch, H, W.")

    B, C, H, W = img.shape
    dtype, dev = img.dtype, img.device

    # ─── 1. base grid (once per batch)  in NDC  ───────────────────────────
    #   y first, x second (grid_sample convention)
    v, u = torch.meshgrid(
        torch.linspace(-1.0, 1.0, H, dtype=dtype, device=dev),
        torch.linspace(-1.0, 1.0, W, dtype=dtype, device=dev),
        indexing="ij",
    )  # each (H,W)
    base_grid = torch.stack((u, v), dim=-1)  # (H,W,2)
    base_grid = base_grid.unsqueeze(0).expand(B, -1, -1, -1)  # (B,H,W,2)

    # ─── 2. pixel → NDC scaling for the whole batch ───────────────────────
    scale_x = 2.0 / max(W - 1, 1)
    scale_y = 2.0 / max(H - 1, 1)
    norm_flow = torch.empty_like(flow)
    norm_flow[:, 0] = flow[:, 0] * scale_x  # dx
    norm_flow[:, 1] = flow[:, 1] * scale_y  # dy
    norm_flow = norm_flow.permute(0, 2, 3, 1)  # (B,H,W,2)

    # ─── 3. add & sample ──────────────────────────────────────────────────
    grid = base_grid + norm_flow
    warped = F.grid_sample(img, grid, mode=mode, padding_mode=padding_mode, align_corners=align_corners)

    if not return_valid_mask:
        return warped

    valid = ((grid[..., 0].abs() <= 1) & (grid[..., 1].abs() <= 1)).unsqueeze(1)  # (B,1,H,W) bool
    return warped, valid


# ─────────────────────────────────────────────────────────────────────────
# 2.  Visibility-aware batched warp  (needs source depth)
# ─────────────────────────────────────────────────────────────────────────
def warp_forward_zbuffer_batched(
    img_src: torch.Tensor,  # (B,C,H,W)
    flow_old_to_new: torch.Tensor,  # (B,2,H,W)
    depth_src: torch.Tensor,  # (B,1,H,W)
    *,
    tol_abs: float = 2e-3,
    tol_rel: float = 0.01,
    fill_value: float = 0.0,
    mode="bilinear",
    padding_mode="zeros",
    align_corners=True,
):
    """
    Occlusion-aware batch warp.  Keeps only the **front-most** source pixel per
    target location (Z-buffer) with absolute/relative tolerances.
    """
    # 1. visibility mask in source image
    vis_src = zbuffer_visibility(depth_src, flow_old_to_new, tol_abs=tol_abs, tol_rel=tol_rel)  # (B,1,H,W)

    # 2. regular inverse warp for colours
    warped = warp_forward_batched(img_src, -flow_old_to_new, mode=mode, padding_mode=padding_mode, align_corners=align_corners)  # (B,C,H,W)

    # 3. warp the binary visibility mask with nearest-neighbour
    vis_tgt = (
        warp_forward_batched(vis_src.float(), -flow_old_to_new, mode="nearest", padding_mode="zeros", align_corners=align_corners)[0] > 0.5
    )  # (B,1,H,W)

    # 4. apply the mask
    warp_masked = warped * vis_tgt.float() + fill_value * (~vis_tgt).float()
    return warp_masked, vis_tgt


def warp_forward_zbuffer(
    img_src,
    flow_old_to_new,
    depth_src,
    *,
    tol_abs=2e-3,
    tol_rel=0.01,
    fill_value=0.0,
    mode="bilinear",
    padding_mode="zeros",
    align_corners=True,
):
    vis_src = zbuffer_visibility(depth_src, flow_old_to_new, tol_abs=tol_abs, tol_rel=tol_rel)  # (B,1,H,W)

    warp = warp_forward(img_src, -flow_old_to_new, mode=mode, padding_mode=padding_mode, align_corners=align_corners)

    vis_tgt = warp_forward(vis_src.float(), -flow_old_to_new, mode="nearest", padding_mode="zeros", align_corners=align_corners) > 0.5

    warp_masked = warp * vis_tgt.float() + fill_value * (~vis_tgt).float()
    return warp_masked, vis_tgt

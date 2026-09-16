"""Inference-only adapter for standard gsplat checkpoints and rasterization."""

from dataclasses import dataclass
from math import isqrt

import numpy as np


@dataclass(frozen=True)
class SplatRenderParams:
    device: str = "cuda"
    background: tuple[float, float, float] = (1.0, 1.0, 1.0)
    near: float = 0.01  # reconstruction units
    far: float = 1e10
    radius_clip: float = 0.0
    packed: bool = True
    rasterize_mode: str = "antialiased"
    sh_degree: int | None = None  # use all checkpoint coefficients

    def __post_init__(self):
        if (
            not np.isfinite([self.near, self.far, self.radius_clip]).all()
            or not 0 < self.near < self.far
            or self.radius_clip < 0
        ):
            raise ValueError("Invalid clipping parameters")
        bg = np.asarray(self.background)
        if bg.shape != (3,) or not np.isfinite(bg).all() or np.any((bg < 0) | (bg > 1)):
            raise ValueError("background must be RGB in [0,1]")
        if self.rasterize_mode not in {"classic", "antialiased"}:
            raise ValueError("Invalid rasterize_mode")
        if self.sh_degree is not None and (type(self.sh_degree) is not int or self.sh_degree < 0):
            raise ValueError("sh_degree must be a nonnegative integer")


class GsplatRenderer:
    """Load once and cache activated tensors; no optimizers or densification code.

    render(K, C2W, width, height) uses OpenCV camera axes and returns RGB uint8,
    expected z-depth float32 and accumulated alpha float32. Caller owns lifetime.
    """

    def __init__(self, checkpoint, params: SplatRenderParams | None = None):
        self.params = params or SplatRenderParams()
        try:
            import torch
            from gsplat import rasterization
        except ImportError as exc:
            raise ImportError(
                "Gaussian splatting requires optional torch and gsplat; run uv sync --extra splat on a CUDA Linux host"
            ) from exc
        if not self.params.device.startswith("cuda") or not torch.cuda.is_available():
            raise RuntimeError("GsplatRenderer requires an available CUDA device")
        self._torch, self._rasterize = torch, rasterization
        self.device = torch.device(self.params.device)
        checkpoint = torch.load(checkpoint, map_location="cpu", weights_only=True)
        splats = checkpoint["splats"]
        tensors = {
            name: splats[name].detach().to(device=self.device, dtype=torch.float32).contiguous()
            for name in ("means", "quats", "scales", "opacities", "sh0", "shN")
        }
        n = tensors["means"].shape[0]
        shapes = {"means": (n, 3), "quats": (n, 4), "scales": (n, 3), "opacities": (n,), "sh0": (n, 1, 3)}
        if n == 0 or any(tuple(tensors[k].shape) != shape for k, shape in shapes.items()):
            raise ValueError("Invalid splat checkpoint tensor shapes")
        shn = tensors["shN"]
        if shn.ndim != 3 or shn.shape[0] != n or shn.shape[2] != 3:
            raise ValueError("shN must have shape (N, K-1, 3)")
        coefficients = shn.shape[1] + 1
        degree = isqrt(coefficients) - 1
        if (degree + 1) ** 2 != coefficients:
            raise ValueError("Spherical harmonic coefficient count must be square")
        self.degree = degree if self.params.sh_degree is None else self.params.sh_degree
        if self.degree > degree or any(not t.isfinite().all().item() for t in tensors.values()):
            raise ValueError("Invalid SH degree or nonfinite checkpoint")
        if (tensors["quats"].norm(dim=-1) == 0).any().item():
            raise ValueError("Checkpoint contains zero quaternions")
        self.tensors = {k: tensors[k] for k in ("means", "quats")}
        self.tensors.update(
            scales=tensors["scales"].exp(),
            opacities=tensors["opacities"].sigmoid(),
            colors=torch.cat((tensors["sh0"], shn), dim=1),
        )
        if not self.tensors["scales"].isfinite().all().item():
            raise ValueError("Checkpoint scales overflow")
        self.background = torch.tensor(self.params.background, device=self.device, dtype=torch.float32)[None]

    def render(self, K, C2W, width, height):
        torch = self._torch
        if self.tensors is None:
            raise RuntimeError("Renderer is closed")
        with torch.inference_mode():
            views = torch.as_tensor(np.linalg.inv(C2W), device=self.device, dtype=torch.float32)[None]
            intrinsics = torch.as_tensor(K, device=self.device, dtype=torch.float32)[None]
            colors, alpha, _ = self._rasterize(
                **self.tensors,
                viewmats=views,
                Ks=intrinsics,
                width=width,
                height=height,
                sh_degree=self.degree,
                packed=self.params.packed,
                backgrounds=self.background,
                near_plane=self.params.near,
                far_plane=self.params.far,
                radius_clip=self.params.radius_clip,
                rasterize_mode=self.params.rasterize_mode,
                render_mode="RGB+ED",
            )
            return {
                "rgb": (colors[0, ..., :3].clamp(0, 1) * 255).round().to(torch.uint8).cpu().numpy(),
                "depth": colors[0, ..., 3].cpu().numpy(),
                "alpha": alpha[0, ..., 0].cpu().numpy(),
            }

    def close(self):
        self.tensors = None
        self.background = None

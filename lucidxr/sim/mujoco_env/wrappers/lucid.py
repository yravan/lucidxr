"""Lucid generation inputs: hidden-scene conditioning and retained foreground."""

from dataclasses import dataclass, replace

import numpy as np
from gymnasium import spaces

from .ade20k import COLORS
from .camera_view import Camera, CameraView, depth_image
from .observations import ObservationWrapper


def midas_depth(depth, far, mask=None):
    """Legacy relative inverse depth in [0,255], with finite empty-mask handling."""
    valid = np.isfinite(depth) & (depth > 0)
    inverse = np.zeros_like(depth, dtype=np.float32)
    np.divide(1, depth, out=inverse, where=valid)
    if mask is not None:
        valid &= mask
        if not valid.any():
            return inverse * 0
        low, high = inverse[valid].min(), inverse[valid].max()
        return np.where(valid, np.clip((inverse - low) / (high - low + 1e-8), 0, 1) * 255, 0).astype(
            np.float32
        )
    near = valid & (depth < far)
    candidates = near if near.any() else valid
    if not candidates.any():
        return inverse
    low = inverse[candidates].min() - 1
    high = inverse[valid].max()
    return np.where(valid, np.clip((inverse - low) / (high - low + 1e-8), 0, 1) * 255, 0).astype(np.float32)


@dataclass(frozen=True)
class LucidParams:
    camera: Camera
    preserve_bodies: tuple[str, ...] = ()
    key: str | None = None
    # Camera.semantic assigns ADE IDs 1..150; unmatched geoms/background are black.


class LucidWrapper(ObservationWrapper):
    """Prepare conditioning observations; diffusion inference belongs to its caller.

    preserve_mask=True means retain this original MuJoCo pixel when compositing.
    Camera masks select objects in the hidden-scene conditioning image. Outputs
    have explicit keys and types, without packed masks or truncated geom IDs.
    """

    uses_rendering = True

    def __init__(self, env, params: LucidParams):
        super().__init__(env)
        if not isinstance(params, LucidParams):
            raise TypeError("params must be LucidParams")
        camera = params.camera
        self.key = params.key or f"{camera.key or camera.name}/lucid"
        if any(type(label) is not int or not 1 <= label < len(COLORS) for label in camera.semantic.values()):
            raise ValueError("Lucid semantic labels must be ADE20K IDs 1..150")
        self.scene_view = CameraView(
            self.base.model,
            replace(
                camera,
                key="scene",
                products=("depth", "segmentation", "semantic"),
                calibration=True,
                hide_bodies=tuple(dict.fromkeys((*camera.hide_bodies, *params.preserve_bodies))),
            ),
        )
        self.full_view = CameraView(
            self.base.model,
            replace(
                camera,
                key="full",
                products=("rgb", "depth"),
                calibration=False,
                masks={"preserve": params.preserve_bodies},
                semantic={},
            ),
        )
        h, w = camera.height, camera.width
        rgb = spaces.Box(0, 255, (h, w, 3), np.uint8)
        entries = {
            "rgb": rgb,
            "overlay": rgb,
            "semantic_rgb": rgb,
            "preserve_mask": spaces.Box(0, 1, (h, w), np.bool_),
            "midas_depth": spaces.Box(0, 255, (h, w), np.float32),
            "masked_midas_depth": spaces.Box(0, 255, (h, w), np.float32),
            "normalized_depth": spaces.Box(0, 255, (h, w), np.uint8),
        }
        for name in ("depth", "segmentation", "semantic", "K", "C2W"):
            entries[name] = self.scene_view.spaces[f"scene/{name}"]
        entries.update(
            {f"mask/{name}": self.scene_view.spaces[f"scene/mask/{name}"] for name in camera.masks}
        )
        entries = {f"{self.key}/{name}": value for name, value in entries.items()}
        if entries.keys() & env.observation_space.spaces.keys():
            raise ValueError("Lucid output keys overlap existing observations")
        self.observation_space = spaces.Dict({**env.observation_space.spaces, **entries})

    def observation(self, observation):
        return self._apply_observation(dict(observation))

    def _apply_observation(self, observation):
        scene = {k.removeprefix("scene/"): v for k, v in self.scene_view.capture(self.base.rendering).items()}
        full = self.full_view.capture(self.base.rendering)
        camera = self.scene_view.camera
        mask = full["full/mask/preserve"]
        labels = scene["semantic"]
        scene["semantic_rgb"] = COLORS[np.maximum(labels, 0)]
        scene["rgb"] = full["full/rgb"]
        scene["preserve_mask"] = mask
        scene["overlay"] = np.where(mask[..., None], scene["rgb"], np.uint8(255))
        scene["midas_depth"] = midas_depth(scene["depth"], camera.far)
        masks = [scene[f"mask/{name}"] for name in camera.masks]
        selected = np.logical_or.reduce(masks) if masks else np.zeros_like(mask)
        scene["masked_midas_depth"] = midas_depth(
            np.clip(scene["depth"], camera.near, camera.far), camera.far, selected
        )
        scene["normalized_depth"] = np.rint(
            depth_image(full["full/depth"], camera.near, camera.far) * 255
        ).astype(np.uint8)
        observation.update({f"{self.key}/{name}": value for name, value in scene.items()})
        return observation

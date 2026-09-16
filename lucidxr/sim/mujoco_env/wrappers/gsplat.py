"""Gaussian-splat observations with explicit alignment and foreground compositing."""

from dataclasses import dataclass

import numpy as np
from gymnasium import spaces

from ..splat import SplatAlignment
from .observations import ObservationWrapper


@dataclass(frozen=True)
class GsplatParams:
    camera: str
    width: int = 640
    height: int = 360
    key: str = "splat"
    alignment: SplatAlignment = SplatAlignment()
    foreground_rgb: str | None = None
    preserve_mask: str | None = None

    def __post_init__(self):
        if any(type(x) is not int or x <= 0 for x in (self.width, self.height)):
            raise ValueError("Image dimensions must be positive integers")
        if (self.foreground_rgb is None) != (self.preserve_mask is None):
            raise ValueError("foreground_rgb and preserve_mask must be provided together")


class GsplatWrapper(ObservationWrapper):
    """Add RGB/depth/alpha; inject a reusable renderer with render(K,C2W,w,h).

    The renderer is caller-owned and may be shared by multiple cameras. RGB
    compositing matches the original foreground overlay; depth/alpha describe
    the splat render only, not the composite. No hidden checkpoint downloads.
    """

    uses_rendering = True

    def __init__(self, env, renderer, params: GsplatParams):
        super().__init__(env)
        self.params, self.renderer = params, renderer
        self.camera_id = self.base.model.camera(params.camera).id
        # Resolve once; reject unsupported orthographic calibration immediately.
        self.base.rendering.calibration(self.camera_id, params.width, params.height)
        self.rotation, self.origin = params.alignment.camera_transform()
        self._render_key = (
            id(renderer),
            self.camera_id,
            params.width,
            params.height,
            self.rotation.tobytes(),
            self.origin.tobytes(),
            params.alignment.scale,
        )
        h, w = params.height, params.width
        entries = {
            f"{params.key}/rgb": spaces.Box(0, 255, (h, w, 3), np.uint8),
            f"{params.key}/depth": spaces.Box(0, np.inf, (h, w), np.float32),
            f"{params.key}/alpha": spaces.Box(0, 1, (h, w), np.float32),
        }
        if entries.keys() & env.observation_space.spaces.keys():
            raise ValueError("Splat output keys overlap existing observations")
        if params.foreground_rgb is not None:
            for key, shape, dtype in (
                (params.foreground_rgb, (h, w, 3), np.uint8),
                (params.preserve_mask, (h, w), np.bool_),
            ):
                space = env.observation_space.spaces.get(key)
                if space is None or space.shape != shape or space.dtype != dtype:
                    raise ValueError(f"Invalid foreground observation {key!r}")
        self.observation_space = spaces.Dict({**env.observation_space.spaces, **entries})

    def observation(self, observation):
        return self._apply_observation(dict(observation))

    def _capture(self):
        p = self.params
        K, pose = self.base.rendering.calibration(self.camera_id, p.width, p.height)
        pose[:3, :3] = self.rotation @ pose[:3, :3]
        pose[:3, 3] = self.rotation @ (pose[:3, 3] - self.origin) / p.alignment.scale
        values = self.renderer.render(K, pose, p.width, p.height)
        # Copies prevent compositing or later backend calls mutating prior observations.
        values = {name: np.array(values[name], copy=True) for name in ("rgb", "depth", "alpha")}
        values["depth"] *= p.alignment.scale
        for name, value in values.items():
            if not self.observation_space[f"{p.key}/{name}"].contains(value):
                raise ValueError(f"Splat renderer returned invalid {name}")
        return values

    def _apply_observation(self, observation):
        p = self.params
        values = self.base.rendering.external(self._render_key, self._capture)
        if p.foreground_rgb is not None:
            np.copyto(
                values["rgb"], observation[p.foreground_rgb], where=observation[p.preserve_mask][..., None]
            )
        observation.update({f"{p.key}/{name}": value for name, value in values.items()})
        return observation

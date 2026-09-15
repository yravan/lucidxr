"""Seeded visual randomization independent of camera observation wrappers."""

from dataclasses import dataclass

import gymnasium as gym
import mujoco
import numpy as np
from scipy.spatial.transform import Rotation


@dataclass(frozen=True)
class VisualRandomization:
    """Uniform perturbations around the original model, never the last sample.

    Names default to every camera/light. Textures are optional because large
    texture trees require a baseline copy; no dataset/model service is involved.
    """

    cameras: tuple[str, ...] | None = None
    lights: tuple[str, ...] | None = None
    camera_position: float = 0.01
    camera_rotation: float = 0.087
    camera_fovy: float = 5.0
    light_position: float = 0.1
    light_color: float = 0.1
    color: float = 0.2
    textures: bool = False


class DomainRandomization(gym.Wrapper):
    """Randomize at reset; explicitly call randomize() for an offline variant.

    Put this inside observation wrappers so reset observations see the sampled
    model. Observation reads never resample. Physics dynamics are unchanged.
    """

    def __init__(self, env, config=None):
        super().__init__(env)
        self.config = config if config is not None else VisualRandomization()
        for name in (
            "camera_position",
            "camera_rotation",
            "camera_fovy",
            "light_position",
            "light_color",
            "color",
        ):
            value = getattr(self.config, name)
            if not np.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and nonnegative")
        model = self.unwrapped.model
        self._cameras = np.array(
            [model.camera(name).id for name in self.config.cameras]
            if self.config.cameras is not None
            else list(range(model.ncam)),
            dtype=int,
        )
        self._lights = np.array(
            [model.light(name).id for name in self.config.lights]
            if self.config.lights is not None
            else list(range(model.nlight)),
            dtype=int,
        )
        fields = [
            "cam_pos",
            "cam_quat",
            "cam_fovy",
            "light_pos",
            "light_diffuse",
            "light_ambient",
            "light_specular",
            "geom_rgba",
            "mat_rgba",
        ]
        if self.config.textures:
            fields.append("tex_data")
        self._defaults = {name: getattr(model, name).copy() for name in fields}

    def restore(self):
        for name, value in self._defaults.items():
            getattr(self.unwrapped.model, name)[:] = value
        self._refresh()

    def _refresh(self):
        base = self.unwrapped
        mujoco.mj_forward(base.model, base.data)
        # Recreate the lazy renderer to upload changed textures without relying
        # on private OpenGL context internals. Usually only happens at reset.
        if self.config.textures and base._rendering is not None:
            base._rendering.close()
            base._rendering = None

    def randomize(self):
        base = self.unwrapped
        rng, model, config = base.np_random, base.model, self.config
        for name, value in self._defaults.items():
            getattr(model, name)[:] = value
        for field, ids, scale, bounds in (
            ("cam_pos", self._cameras, config.camera_position, None),
            ("cam_fovy", self._cameras, config.camera_fovy, (1, 179)),
            ("light_pos", self._lights, config.light_position, None),
            ("light_diffuse", self._lights, config.light_color, (0, 1)),
            ("light_ambient", self._lights, config.light_color, (0, 1)),
            ("light_specular", self._lights, config.light_color, (0, 1)),
        ):
            target = getattr(model, field)
            value = self._defaults[field][ids] + rng.uniform(-scale, scale, target[ids].shape)
            target[ids] = np.clip(value, *bounds) if bounds else value
        if len(self._cameras):
            rotation = Rotation.from_rotvec(
                rng.uniform(-config.camera_rotation, config.camera_rotation, (len(self._cameras), 3))
            )
            baseline = Rotation.from_quat(self._defaults["cam_quat"][self._cameras], scalar_first=True)
            model.cam_quat[self._cameras] = (baseline * rotation).as_quat(scalar_first=True)
        for name in ("geom_rgba", "mat_rgba"):
            target = getattr(model, name)
            target[:, :3] = np.clip(
                target[:, :3] + rng.uniform(-config.color, config.color, target[:, :3].shape), 0, 1
            )
        if config.textures:
            # Per-texture RGB tint, no full-sized noise array for large textures.
            for index in range(model.ntex):
                start = model.tex_adr[index]
                count = model.tex_width[index] * model.tex_height[index] * model.tex_nchannel[index]
                channels = model.tex_nchannel[index]
                pixels = model.tex_data[start : start + count].reshape(-1, channels)
                shift = rng.uniform(-config.color, config.color, min(3, channels)) * 255
                pixels[:, : len(shift)] = np.clip(pixels[:, : len(shift)].astype(float) + shift, 0, 255)
        self._refresh()

    def reset(self, *, seed=None, options=None):
        self.restore()
        _, info = self.env.reset(seed=seed, options=options)
        self.randomize()
        return self.env.get_wrapper_attr("observe")(), info

    def observe(self):
        return self.env.get_wrapper_attr("observe")()

    def close(self):
        self.restore()
        self.env.close()

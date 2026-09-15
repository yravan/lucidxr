"""Randomize a scene's light pool without changing model topology."""

from dataclasses import dataclass, field

import mujoco
import numpy as np

from .randomization import RandomizationParams, RandomizationWrapper
from .sampling import PositionRandomization, RotationRandomization, Uniform, check_range, select_ids


@dataclass(frozen=True)
class LightingRandomizationParams(RandomizationParams):
    names: tuple[str, ...] | None = None
    position: PositionRandomization = field(default_factory=lambda: PositionRandomization(0.1))
    rotation: RotationRandomization = field(default_factory=lambda: RotationRandomization(0.35))
    ambient: float = 0.1
    diffuse: float = 0.1
    specular: float = 0.1
    active_probability: float | None = 0.5
    active_count: tuple[int, int] | None = None  # inclusive; takes precedence over probability
    shadow_probability: float | None = None
    cutoff: Uniform | None = None  # degrees; classic spotlights
    exponent: Uniform | None = None
    attenuation: Uniform | None = None  # each of the three coefficients
    intensity: Uniform | None = None  # candela; PBR backends only
    range: Uniform | None = None
    bulbradius: Uniform | None = None  # PBR soft-shadow backend only

    def __post_init__(self):
        super().__post_init__()
        RandomizationWrapper.validate_scales(
            ambient=self.ambient, diffuse=self.diffuse, specular=self.specular
        )
        for name in ("active_probability", "shadow_probability"):
            value = getattr(self, name)
            if value is not None and (not np.isfinite(value) or not 0 <= value <= 1):
                raise ValueError(f"{name} must be in [0,1] or None")
        if self.active_count is not None:
            if (
                len(self.active_count) != 2
                or any(type(v) is not int for v in self.active_count)
                or not 0 <= self.active_count[0] <= self.active_count[1]
            ):
                raise ValueError("active_count must be an inclusive nonnegative integer range")
        for name in ("exponent", "attenuation", "intensity", "range", "bulbradius"):
            check_range(getattr(self, name), name=name)
        check_range(self.cutoff, high=90, name="cutoff")
        if not isinstance(self.position, PositionRandomization) or not isinstance(
            self.rotation, RotationRandomization
        ):
            raise TypeError("position/rotation require their sampling dataclasses")


class LightingRandomization(RandomizationWrapper):
    """Sample pose, activation/count, shadows and backend-specific light properties.

    The number of active lights varies within a compiled scene's existing pool.
    Add additional potential lights in Scene.build(), not in the reset hot path.
    """

    def __init__(self, env, params: LightingRandomizationParams | None = None):
        self.params = params = self.parameters(params, LightingRandomizationParams)
        model = env.unwrapped.model
        self.ids = select_ids(model, "light", params.names)
        if params.active_count and params.active_count[1] > len(self.ids):
            raise ValueError("active_count exceeds the selected scene light pool")
        if params.rotation.max_angle and np.any(
            model.light_mode[self.ids] >= int(mujoco.mjtCamLight.mjCAMLIGHT_TARGETBODY)
        ):
            raise ValueError("Target-tracking lights derive direction; set rotation.max_angle=0")
        fields = ("pos", "dir", "ambient", "diffuse", "specular", "active", "castshadow")
        fields += tuple(
            name
            for name in ("cutoff", "exponent", "attenuation", "intensity", "range", "bulbradius")
            if getattr(params, name) is not None
        )
        super().__init__(env, params=self.params, fields={f"light_{name}": self.ids for name in fields})

    def sample(self, rng):
        params, model = self.params, self.base.model
        model.light_pos[self.ids] = params.position.sample(rng, self._defaults["light_pos"])
        if len(self.ids) and params.rotation.max_angle:
            direction = params.rotation.sample(rng, len(self.ids)).apply(self._defaults["light_dir"])
            model.light_dir[self.ids] = direction / np.linalg.norm(direction, axis=1, keepdims=True)
        for name in ("ambient", "diffuse", "specular"):
            self.perturb(rng, f"light_{name}", getattr(params, name), bounds=(0, 1))
        if params.active_count is not None:
            count = rng.integers(params.active_count[0], params.active_count[1] + 1)
            active = np.zeros(len(self.ids), dtype=bool)
            active[rng.choice(len(self.ids), count, replace=False)] = True
            model.light_active[self.ids] = active
        elif params.active_probability is not None:
            model.light_active[self.ids] = rng.random(len(self.ids)) < params.active_probability
        if params.shadow_probability is not None:
            model.light_castshadow[self.ids] = rng.random(len(self.ids)) < params.shadow_probability
        for name in ("cutoff", "exponent", "attenuation", "intensity", "range", "bulbradius"):
            distribution = getattr(params, name)
            if distribution is not None:
                target = getattr(model, f"light_{name}")
                target[self.ids] = distribution.sample(rng, target[self.ids].shape)

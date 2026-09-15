"""Role-aware pixel randomization, separate from material properties."""

from dataclasses import dataclass

import numpy as np

from .randomization import RandomizationParams, RandomizationWrapper
from .texture_assets import KINDS, select_textures
from .texture_patterns import MODES, paint


@dataclass(frozen=True)
class TextureRandomizationParams(RandomizationParams):
    names: tuple[str, ...] | None = None
    kinds: tuple[str, ...] = ("2d", "cube")  # explicitly include skybox to modify it
    modes: tuple[str, ...] = ("tint",)
    strength: float = 0.2  # tint offset in normalized color units
    checker_tiles: int = 2
    gradient_axis: str = "random"
    noise_probability: float = 0.9
    blend: float = 1.0  # interpolate the sampled result with the original RGB

    def __post_init__(self):
        super().__post_init__()
        RandomizationWrapper.validate_scales(strength=self.strength)
        if type(self.checker_tiles) is not int or self.checker_tiles < 1:
            raise ValueError("checker_tiles must be a positive integer")
        if self.gradient_axis not in {"x", "y", "random"}:
            raise ValueError("gradient_axis must be x, y or random")
        if not np.isfinite(self.noise_probability) or not 0 <= self.noise_probability <= 1:
            raise ValueError("noise_probability must be in [0,1]")
        if self.strength > 1:
            raise ValueError("strength must be in [0,1]")
        if not np.isfinite(self.blend) or not 0 <= self.blend <= 1:
            raise ValueError("blend must be in [0,1]")
        if isinstance(self.kinds, str) or not self.kinds or set(self.kinds) - KINDS.keys():
            raise ValueError("kinds must contain 2d, cube and/or skybox")
        if isinstance(self.modes, str) or not self.modes or set(self.modes) - MODES:
            raise ValueError(f"modes must contain values from {sorted(MODES)}")
        if self.names is not None and (
            isinstance(self.names, str) or len(set(self.names)) != len(self.names)
        ):
            raise ValueError("names must be a sequence of distinct texture names")


class TextureRandomization(RandomizationWrapper):
    """Sample each selected color texture once, retaining alpha/exposure and PBR maps.

    Each selected asset owns an RGB-only baseline. Pixel edits are the purpose of
    this wrapper; use MaterialRandomization for inexpensive surface-color changes.
    """

    def __init__(self, env, params: TextureRandomizationParams | None = None):
        self.params = self.parameters(params, TextureRandomizationParams)
        self.assets = select_textures(env.unwrapped.model, self.params.names, self.params.kinds)
        self.texture_ids = tuple(asset.id for asset in self.assets)
        super().__init__(env, params=self.params, fields={}, texture_ids=self.texture_ids)

    def _restore_model(self):
        for asset in self.assets:
            asset.restore()

    def sample(self, rng):
        for asset in self.assets:
            paint(
                asset.pixels,
                rng,
                mode=rng.choice(self.params.modes),
                strength=self.params.strength,
                face_height=asset.face_height,
                baseline=asset.baseline,
                blend=self.params.blend,
                checker_tiles=self.params.checker_tiles,
                gradient_axis=self.params.gradient_axis,
                noise_probability=self.params.noise_probability,
            )

"""Explicit scalar texture operations, independent of RGB augmentation."""

from dataclasses import dataclass

import mujoco
import numpy as np

from .randomization import RandomizationParams, RandomizationWrapper
from .sampling import Uniform, check_range
from .texture_assets import KINDS, TextureAsset

# Role, channel count, selected channel. Never interpret emissive weight as alpha.
CHANNELS = {
    "alpha": (int(mujoco.mjtTextureRole.mjTEXROLE_RGBA), 4, 3),
    "opacity": (int(mujoco.mjtTextureRole.mjTEXROLE_OPACITY), 1, 0),
    "exposure_weight": (int(mujoco.mjtTextureRole.mjTEXROLE_EMISSIVE), 4, 3),
}


@dataclass(frozen=True)
class TextureScalarRandomizationParams(RandomizationParams):
    channel: str = "alpha"
    values: Uniform = Uniform(0.5, 1.0)  # normalized stored channel values
    names: tuple[str, ...] | None = None
    kinds: tuple[str, ...] = ("2d", "cube")
    per_pixel: bool = False  # default: coherent value per asset

    def __post_init__(self):
        super().__post_init__()
        if self.channel not in CHANNELS:
            raise ValueError(f"channel must be one of {tuple(CHANNELS)}")
        if not isinstance(self.values, Uniform):
            raise TypeError("values must be Uniform")
        check_range(self.values, high=1, name="values")
        if type(self.per_pixel) is not bool:
            raise TypeError("per_pixel must be bool")
        if isinstance(self.kinds, str) or not self.kinds or set(self.kinds) - KINDS.keys():
            raise ValueError("kinds must contain 2d, cube and/or skybox")
        if self.names is not None and (
            isinstance(self.names, str) or len(set(self.names)) != len(self.names)
        ):
            raise ValueError("names must contain distinct texture names")


class TextureScalarRandomization(RandomizationWrapper):
    """Sample opacity, RGBA alpha, or emissive exposure weight as separate operations.

    Only exclusively matching material roles are eligible. Explicit incompatible
    names fail; automatic selection skips them. Unreferenced images are skipped.
    Baselines own only the selected channel, so RGB restoration is independent.
    """

    def __init__(self, env, params: TextureScalarRandomizationParams | None = None):
        params = self.parameters(params, TextureScalarRandomizationParams)
        model = env.unwrapped.model
        role, channels, channel = CHANNELS[params.channel]
        allowed = {int(KINDS[kind]) for kind in params.kinds}
        ids = range(model.ntex) if params.names is None else [model.texture(n).id for n in params.names]
        assets = []
        for index in ids:
            roles = set(np.nonzero(model.mat_texid == index)[1].tolist())
            kind = int(model.tex_type[index])
            if roles != {role} or model.tex_nchannel[index] != channels or kind not in allowed:
                if params.names is not None:
                    raise ValueError(
                        f"Texture {model.texture(index).name!r} is not exclusively {params.channel}"
                    )
                continue
            start = int(model.tex_adr[index])
            h, w = int(model.tex_height[index]), int(model.tex_width[index])
            pixels = model.tex_data[start : start + h * w * channels].reshape(h, w, channels)[..., channel]
            assets.append(TextureAsset(index, pixels, pixels.copy(), h if kind == 0 else w))
        self.assets = tuple(assets)
        self.texture_ids = tuple(asset.id for asset in assets)
        super().__init__(env, params=params, fields={}, texture_ids=self.texture_ids)

    def _restore_model(self):
        for asset in self.assets:
            asset.restore()

    def sample(self, rng):
        for asset in self.assets:
            if not self.params.per_pixel:
                asset.pixels[...] = np.rint(self.params.values.sample(rng, ()) * 255).astype(np.uint8)
                continue
            # Bound temporary allocations even for large environment maps.
            rows = max(1, 65536 // asset.pixels.shape[1])
            for start in range(0, asset.pixels.shape[0], rows):
                target = asset.pixels[start : start + rows]
                target[...] = np.rint(self.params.values.sample(rng, target.shape) * 255).astype(np.uint8)

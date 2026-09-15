"""Randomize surface appearance without altering dynamics or opacity."""

import numpy as np

from .randomization import RandomizationWrapper


class TextureRandomization(RandomizationWrapper):
    """Tint geometry/material colors and optionally the actual texture pixels.

    color is a uniform per-channel offset in [0,1] units. Texture pixels are
    opt-in because keeping their baseline can require substantial memory.
    Geometries/materials/textures are shared model resources, sampled once each.
    """

    def __init__(self, env, *, color=0.2, textures=False):
        self.validate_scales(color=color)
        self.color, self.textures = color, textures
        fields = {name: (slice(None), slice(0, 3)) for name in ("geom_rgba", "mat_rgba")}
        if textures:
            fields["tex_data"] = slice(None)
        super().__init__(env, fields=fields, textures_changed=textures)

    def sample(self, rng):
        for field in ("geom_rgba", "mat_rgba"):
            self.perturb(rng, field, self.color, bounds=(0, 1))
        if not self.textures:
            return
        model = self.base.model
        for index in range(model.ntex):
            start = model.tex_adr[index]
            channels = model.tex_nchannel[index]
            count = model.tex_width[index] * model.tex_height[index] * channels
            pixels = model.tex_data[start : start + count].reshape(-1, channels)
            shift = rng.uniform(-self.color, self.color, min(3, channels)) * 255
            pixels[:, : len(shift)] = np.clip(pixels[:, : len(shift)].astype(float) + shift, 0, 255)

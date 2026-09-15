"""Randomize light positions and illumination colors."""

import numpy as np

from .randomization import RandomizationWrapper


class LightingRandomization(RandomizationWrapper):
    """Uniform position offsets in meters and ambient/diffuse/specular offsets.

    names=None selects every light. Color channels remain within [0,1].
    """

    def __init__(self, env, *, names=None, position=0.1, color=0.1):
        self.validate_scales(position=position, color=color)
        model = env.unwrapped.model
        self.ids = np.array(
            [model.light(name).id for name in names] if names is not None else list(range(model.nlight)),
            dtype=int,
        )
        self.position, self.color = position, color
        super().__init__(
            env,
            fields={
                name: self.ids for name in ("light_pos", "light_diffuse", "light_ambient", "light_specular")
            },
        )

    def sample(self, rng):
        self.perturb(rng, "light_pos", self.position)
        for field in ("light_diffuse", "light_ambient", "light_specular"):
            self.perturb(rng, field, self.color, bounds=(0, 1))

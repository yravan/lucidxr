"""Surface color, reflectance and texture-mapping randomization."""

from dataclasses import dataclass

import numpy as np

from .randomization import RandomizationParams, RandomizationWrapper
from .sampling import Uniform, check_range


@dataclass(frozen=True)
class MaterialRandomizationParams(RandomizationParams):
    names: tuple[str, ...] | None = None
    geom_names: tuple[str, ...] | None = None  # default: geoms without a material
    color: float = 0.2  # symmetric RGB offsets, alpha unchanged
    emission: Uniform | None = None
    specular: Uniform | None = None
    shininess: Uniform | None = None
    reflectance: Uniform | None = None
    metallic: Uniform | None = None
    roughness: Uniform | None = None
    texrepeat: Uniform | None = None  # absolute repeats, sampled independently per axis

    def __post_init__(self):
        super().__post_init__()
        RandomizationWrapper.validate_scales(color=self.color)
        for name in ("emission", "specular", "shininess", "reflectance", "metallic", "roughness"):
            check_range(getattr(self, name), high=1, name=name)
        check_range(self.texrepeat, low=np.finfo(float).eps, name="texrepeat")
        for names in (self.names, self.geom_names):
            if names is not None and (isinstance(names, str) or len(names) != len(set(names))):
                raise ValueError("Names must be sequences of distinct names")


class MaterialRandomization(RandomizationWrapper):
    """Sample selected materials and unmaterialized geom colors without copying textures."""

    def __init__(self, env, params: MaterialRandomizationParams | None = None):
        self.params = params = self.parameters(params, MaterialRandomizationParams)
        model = env.unwrapped.model
        self.ids = np.array(
            [model.material(n).id for n in params.names]
            if params.names is not None
            else list(range(model.nmat)),
            dtype=int,
        )
        geoms = (
            np.array([model.geom(n).id for n in params.geom_names], dtype=int)
            if params.geom_names is not None
            else np.flatnonzero(model.geom_matid < 0)
        )
        fields = {"mat_rgba": (self.ids, slice(0, 3)), "geom_rgba": (geoms, slice(0, 3))}
        self.properties = tuple(
            name
            for name in (
                "emission",
                "specular",
                "shininess",
                "reflectance",
                "metallic",
                "roughness",
                "texrepeat",
            )
            if getattr(params, name) is not None
        )
        fields.update({f"mat_{name}": self.ids for name in self.properties})
        super().__init__(env, params=self.params, fields=fields)

    def sample(self, rng):
        for field in ("geom_rgba", "mat_rgba"):
            self.perturb(rng, field, self.params.color, bounds=(0, 1))
        for name in self.properties:
            target = getattr(self.base.model, f"mat_{name}")
            target[self.ids] = getattr(self.params, name).sample(rng, target[self.ids].shape)

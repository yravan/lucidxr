"""Scene lifecycle shared by every scene definition."""

from abc import ABC, abstractmethod
from pathlib import Path
from types import MappingProxyType

import numpy as np

from lucidxr.sim.assets import asset_root
from lucidxr.sim.xml_schema.document import prepare_xml
from lucidxr.sim.xml_schema.schema import Mjcf


class Scene(ABC):
    """Define only build(); asset resolution, seeding, export and loading are shared."""

    def __init__(self, *, assets: str | Path | None = None, seed: int = 0, **options):
        self.assets = asset_root(assets)
        self.seed = seed
        self.options = MappingProxyType(options)

    @property
    def rng(self) -> np.random.Generator:
        """A fresh generator for a repeatable build; retain it locally while sampling."""
        return np.random.default_rng(self.seed)

    @abstractmethod
    def build(self) -> Mjcf:
        """Compose scene components and objects into one MJCF document."""

    def to_xml(self) -> str:
        document = self.build()
        if not isinstance(document, Mjcf):
            raise TypeError(f"{type(self).__name__}.build() must return Mjcf")
        return prepare_xml(str(document), assets=self.assets)

    def compile(self):
        import mujoco

        return mujoco.MjModel.from_xml_string(self.to_xml())

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_xml())
        return path

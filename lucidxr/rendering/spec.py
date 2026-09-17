"""Explicit render requests and content identity, independent of directory names."""

import hashlib
import json
from dataclasses import asdict, dataclass, field
from importlib.metadata import version
from pathlib import Path

from lucidxr.sim.playback import ReplaySpec

FORMAT_VERSION = 2


def file_hash(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def implementation():
    """Bind outputs to installed simulator/renderer code and dependency versions."""
    root = Path(__file__).resolve().parents[1]
    files = sorted(p for folder in ("sim", "rendering") for p in (root / folder).rglob("*.py"))
    return {
        "code": digest({p.relative_to(root).as_posix(): file_hash(p) for p in files}),
        "packages": {name: version(name) for name in ("mujoco", "numpy", "h5py", "av")},
    }


@dataclass(frozen=True)
class RenderSpec:
    """One frame per recorded state; fps controls video playback, not label timing."""

    cameras: tuple[str, ...]
    width: int = 640
    height: int = 360
    fps: int = 50
    products: tuple[str, ...] = ("rgb",)
    replay: ReplaySpec = field(default_factory=ReplaySpec)

    def __post_init__(self):
        if isinstance(self.replay, dict):
            object.__setattr__(self, "replay", ReplaySpec(**self.replay))
        object.__setattr__(self, "cameras", tuple(self.cameras))
        object.__setattr__(self, "products", tuple(self.products))
        if not self.cameras or len(set(self.cameras)) != len(self.cameras):
            raise ValueError("Provide unique camera names")
        if any(not isinstance(name, str) or not name for name in self.cameras):
            raise ValueError("Camera names must be nonempty strings")
        if any(type(x) is not int or x < 1 for x in (self.width, self.height, self.fps)):
            raise ValueError("Dimensions and fps must be positive integers")
        if self.width % 2 or self.height % 2:
            raise ValueError("H.264 RGB output requires even dimensions")
        if not self.products or len(set(self.products)) != len(self.products):
            raise ValueError("Provide unique products")
        if set(self.products) - {"rgb", "depth", "segmentation"} or "rgb" not in self.products:
            raise ValueError("Products must include rgb; depth and segmentation are supported additions")

    def to_dict(self):
        return asdict(self)


def request(source, spec, *, assets=None):
    target = None
    if spec.replay.scene is not None:
        from lucidxr.sim.demos import scene_fingerprint

        target = scene_fingerprint(spec.replay.make_scene(None, assets=assets))
    return {
        "format_version": FORMAT_VERSION,
        "source_sha256": file_hash(source),
        "spec": spec.to_dict(),
        "target_scene_fingerprint": target,
        "implementation": implementation(),
    }

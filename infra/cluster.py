"""One explicit SSH/Slurm profile; no embedded cluster credentials or host paths."""

import os
import re
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Cluster:
    host: str
    user: str
    root: str
    partition: str
    account: str
    cpus: int = 2
    memory_gb: int = 4
    minutes: int = 10
    concurrency: int = 2
    uv: str = "uv"

    def __post_init__(self):
        for name in ("host", "user", "partition", "account"):
            if not re.fullmatch(r"[A-Za-z0-9_.@-]+", getattr(self, name)) or getattr(self, name).startswith(
                "-"
            ):
                raise ValueError(f"Invalid cluster {name}")
        if not self.root.startswith("/") or any(c in self.root for c in "\n\r\x00"):
            raise ValueError("Cluster root must be an absolute remote path")
        if any(
            type(x) is not int or x < 1 for x in (self.cpus, self.memory_gb, self.minutes, self.concurrency)
        ):
            raise ValueError("Cluster resource values must be positive integers")

    def to_dict(self):
        return asdict(self)


def cluster(name, *, config=None):
    path = Path(config or os.environ.get("LUCIDXR_INFRA_CONFIG", "~/.config/lucidxr/infra.toml")).expanduser()
    with path.open("rb") as stream:
        profiles = tomllib.load(stream).get("clusters", {})
    if name not in profiles:
        raise ValueError(f"Unknown cluster {name!r} in {path}")
    return Cluster(**profiles[name])

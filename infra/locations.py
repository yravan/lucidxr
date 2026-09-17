"""Resolve explicitly configured filesystem roots; no implicit network access."""

import os
import tomllib
from pathlib import Path


def location(name: str, *, config: str | Path | None = None) -> Path:
    """Read a named root from TOML, without creating directories or mounting storage.

    Paths must be absolute (or start with ~). The same interface works on a
    workstation, a cluster login node, or a machine with a Dropbox sync folder.
    """
    path = Path(config or os.environ.get("LUCIDXR_INFRA_CONFIG", "~/.config/lucidxr/infra.toml")).expanduser()
    with path.open("rb") as stream:
        roots = tomllib.load(stream).get("locations", {})
    if name not in roots:
        raise ValueError(f"Unknown location {name!r} in {path}; configured: {', '.join(sorted(roots))}")
    value = roots[name]
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Location {name!r} must be a nonempty filesystem path")
    root = Path(value).expanduser()
    if not root.is_absolute():
        raise ValueError(f"Location {name!r} must be absolute or start with ~")
    return root

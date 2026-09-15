"""One explicit location for task assets; no network access at runtime."""

import hashlib
import json
from pathlib import Path


def asset_root(root: str | Path | None = None) -> Path:
    """Use the bundled assets unless an alternate asset tree is supplied."""
    return Path(root).expanduser().resolve() if root is not None else Path(__file__).resolve().parent


def verify(root: str | Path | None = None) -> None:
    """Check a bundled or relocated asset tree against the pinned manifest."""
    directory = asset_root(root)
    manifest = json.loads((asset_root() / "manifest.json").read_text())
    for name, expected in manifest["files"].items():
        path = directory / name
        if not path.is_file():
            raise FileNotFoundError(f"Missing task asset: {path}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected["sha256"]:
            raise ValueError(f"Asset checksum mismatch: {path}")

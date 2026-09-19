"""A portable cache contract; no simulator, deployment or video imports."""

import hashlib
import json
from pathlib import Path


def fingerprint(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def file_hash(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load_manifest(directory, *, verify=False):
    root = Path(directory).resolve()
    value = json.loads((root / "manifest.json").read_text())
    identity = value.pop("fingerprint")
    if value["version"] != 1 or fingerprint(value) != identity:
        raise ValueError("Invalid training cache manifest")
    if not value["episodes"] or not any(e["split"] == "train" for e in value["episodes"]):
        raise ValueError("A cache requires training episodes")
    groups, sources = {}, {}
    expected_files = set()
    for episode in value["episodes"]:
        key = episode["id"]
        if not key or key in (".", "..") or Path(key).name != key or episode["frames"] < 2:
            raise ValueError("Invalid episode identity or frame count")
        for name in ("images", "state", "actions"):
            relative = f"{key}/{name}.npy"
            if relative in expected_files:
                raise ValueError("Duplicate episode identity")
            expected_files.add(relative)
        if episode["split"] not in ("train", "validation") or not episode["group"]:
            raise ValueError("Episodes require an explicit group and split")
        if groups.setdefault(episode["group"], episode["split"]) != episode["split"]:
            raise ValueError("A collection group crosses train/validation splits")
        pair = (episode["group"], episode["split"])
        if sources.setdefault(episode["source"], pair) != pair:
            raise ValueError("Render variants of one recording must share their group and split")
    if set(value["files"]) != expected_files:
        raise ValueError("Episode arrays differ from the manifest's checked file inventory")
    for name, record in value["files"].items():
        path = (root / name).resolve()
        if not path.is_relative_to(root) or path.stat().st_size != record["bytes"]:
            raise ValueError(f"Missing or invalid cache file: {name}")
        if verify and file_hash(path) != record["sha256"]:
            raise ValueError(f"Corrupt cache file: {name}")
    value["fingerprint"] = identity
    return value

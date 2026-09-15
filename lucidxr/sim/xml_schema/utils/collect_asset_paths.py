"""Inspect file declarations without hiding malformed XML."""

from pathlib import Path
from xml.etree import ElementTree


def collect_asset_paths(xml_path: str | Path, strict=False) -> list[str]:
    """Return sorted unique asset paths; strict controls missing input files only."""
    try:
        root = ElementTree.parse(xml_path).getroot()
    except FileNotFoundError:
        if strict:
            raise
        return []
    return sorted({node.get("file") for asset in root.iter("asset") for node in asset if node.get("file")})

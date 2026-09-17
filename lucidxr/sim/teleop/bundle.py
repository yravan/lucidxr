"""Export just the scene's referenced files for Vuer's browser simulator."""

import hashlib
import shutil
from pathlib import Path

from lxml import etree


def export_bundle(scene, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    root = etree.fromstring(scene.to_xml().encode())
    for field in ("assetdir", "meshdir", "texturedir"):
        root.find("compiler").set(field, ".")
    files = {}
    for element in root.iter():
        source = element.get("file")
        if source is None:
            continue
        path = (scene.assets / source).resolve()
        if not path.is_relative_to(scene.assets.resolve()):
            raise ValueError("Browser assets must be inside the scene asset root")
        relative = path.relative_to(scene.assets.resolve()).as_posix()
        # Flat unique names work with the browser's virtual filesystem.
        name = hashlib.sha256(relative.encode()).hexdigest()[:16] + path.suffix
        if element.tag in {"mesh", "texture", "hfield", "skin"} and element.get("name") is None:
            element.set("name", Path(source).stem)
        element.set("file", name)
        files[name] = path
    for name, source in files.items():
        shutil.copyfile(source, directory / name)
    (directory / "scene.xml").write_bytes(etree.tostring(root))
    return ("scene.xml", *sorted(files))

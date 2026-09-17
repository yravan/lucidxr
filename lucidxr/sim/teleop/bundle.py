"""Export just the scene's referenced files for Vuer's browser simulator."""

import hashlib
import shutil
from pathlib import Path

from lxml import etree

CLOCK_SENSOR = "lucidxr_recording_clock"


def export_bundle(scene, directory, *, recording=False):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    root = etree.fromstring(scene.to_xml().encode())
    for field in ("assetdir", "meshdir", "texturedir"):
        root.find("compiler").set(field, ".")
    if recording:
        if root.xpath(f"./sensor/*[@name='{CLOCK_SENSOR}']"):
            raise ValueError(f"Reserved recording sensor name: {CLOCK_SENSOR}")
        sensor = root.find("sensor")
        if sensor is None:
            sensor = etree.SubElement(root, "sensor")
        etree.SubElement(sensor, "clock", name=CLOCK_SENSOR)
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

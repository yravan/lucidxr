"""Document-level asset resolution, separate from component composition."""

from pathlib import Path

from lxml import etree

from lucidxr.sim.assets import asset_root


def prepare_xml(xml: str, *, assets: str | Path | None = None) -> str:
    """Resolve assets against one root, independent of the working directory.

    The XML can be saved anywhere and loaded directly by MuJoCo. Passing a
    relocated asset tree changes all bundled file references together.
    """
    directory = asset_root(assets)
    root = etree.fromstring(xml.encode(), parser=etree.XMLParser(remove_blank_text=True))
    if root.tag != "mujoco":
        raise ValueError("Expected a <mujoco> document")
    compiler = root.find("compiler")
    if compiler is None:
        compiler = etree.Element("compiler")
        root.insert(0, compiler)
    for attribute in ("assetdir", "meshdir", "texturedir"):
        compiler.set(attribute, str(directory))
    for element in root.iter():
        filename = element.get("file")
        if filename is None:
            continue
        path = Path(filename)
        if path.is_absolute() and path.is_relative_to(asset_root()):
            path = path.relative_to(asset_root())
            element.set("file", path.as_posix())
        resolved = path if path.is_absolute() else directory / path
        if not resolved.is_file():
            raise FileNotFoundError(f"Missing {element.tag} asset: {resolved}")
    return etree.tostring(root, encoding="unicode", pretty_print=True)

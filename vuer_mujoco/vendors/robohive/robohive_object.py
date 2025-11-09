import os
from pathlib import Path
from lxml import etree

from vuer_mujoco.schemas.schema import Body

_default = f"{Path(__file__).parent.parent.parent.parent.parent.parent.resolve()}/robohive/robohive/simhive"
ROBOHIVE_ROOT = os.getenv("ROBOHIVE_ROOT", _default)
ROBOHIVE_OBJECT_SIM_DIR = f"{ROBOHIVE_ROOT}/object_sim"
ROBOHIVE_FURNITURE_SIM_DIR = f"{ROBOHIVE_ROOT}/furniture_sim"


def retrieve_assets(elem: etree.Element, wd: str):
    if elem.tag in ["mesh", "texture", "material"] and elem.attrib.get("file") is not None:
        file_path = elem.attrib.get("file")
        absolute_file_path = f"{wd}/{file_path}"
        elem.attrib["file"] = absolute_file_path
    for child in elem:
        retrieve_assets(child, wd)


def fix_missing_geom_type(elem: etree.Element):
    if elem.tag == "geom" and ("type" not in elem.attrib):
        elem.attrib["type"] = "mesh"

    for child in elem:
        fix_missing_geom_type(child)


def fuzzy_load(*names: str):
    for n in names:
        try:
            parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
            parsed = etree.parse(n, parser=parser)
        except OSError:
            continue
        return parsed

    raise OSError(f"file is not found among {names}.")


class RobohiveObj(Body):
    assets = "objects"

    _attributes = {
        "name": "object",
    }
    
    def __init__(self, otype, asset_key, *_children, pos=None, quat=None, local_robohive_root=None, name=None, **kwargs):
        if name is None:
            self._attributes["name"] = asset_key
        else:
            self._attributes["name"] = name

        try:
            obj_name, rest = asset_key.split("/", 1)
            body_name = rest + "_body.xml"
        except ValueError:
            obj_name = asset_key
            body_name = "body.xml"

        # process common schema for the object_sim
        try:
            common_xml = fuzzy_load(ROBOHIVE_ROOT + f"/{otype}_sim/common.xml")
            common_root = common_xml.getroot()
        except Exception:
            common_root = tuple()

        # process assets
        asset_xml = fuzzy_load(
            ROBOHIVE_ROOT + f"/{otype}_sim/{obj_name}/asset.xml",
            ROBOHIVE_ROOT + f"/{otype}_sim/{obj_name}/assets.xml",
            ROBOHIVE_ROOT + f"/{otype}_sim/{obj_name}/{obj_name}_asset.xml",
        )
        asset_root = asset_xml.getroot()

        # process body schema
        body_xml = fuzzy_load(
            ROBOHIVE_ROOT + f"/{otype}_sim/{obj_name}/{body_name}",
        )
        body_root = body_xml.getroot()
        body = body_root.find("body")
        if body is not None:
            body.attrib["name"] = f"{self._attributes['name']}/{body.attrib['name']}"
            
        fix_missing_geom_type(body_root)

        search_root = local_robohive_root or ROBOHIVE_ROOT
        retrieve_assets(asset_root, search_root + f"/{otype}_sim")
        
        self._preamble = "\n".join(
            [etree.tostring(elem, encoding="unicode", pretty_print=True) for elem in common_root]
            + [etree.tostring(elem, encoding="unicode", pretty_print=True) for elem in asset_root]
        )
        self._children_raw = "\n".join(
            [etree.tostring(elem, encoding="unicode", pretty_print=True) for elem in body_root])

        super().__init__(*_children, pos=pos, quat=quat, **kwargs)

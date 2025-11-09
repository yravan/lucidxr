from __future__ import annotations
import sys
from pathlib import Path
from typing import List

import lxml
from lxml import etree

from vuer_mujoco.schemas.base import Xml, XmlTemplate
from vuer_mujoco.schemas.utils.tree_merge import merge_many


def mujoco_hash(e: etree.Element) -> str:
    # this means it is a comment component.
    if not isinstance(e.tag, str):  # .func_name == 'Comment':
        return str(e)

    values = dict(
        k=e.attrib.get("key", ""),
        n=e.attrib.get("name", ""),
        c=e.attrib.get("class", ""),
        f=e.attrib.get("file", ""),
        m=e.attrib.get("mesh", ""),
        j=e.attrib.get("joint1", ""),
        j2=e.attrib.get("joint2", ""),
        o=e.attrib.get("object1", ""),
        o2=e.attrib.get("object2", ""),
        pi=e.attrib.get("plugin", ""),
        s=e.attrib.get("site1", ""),
        s2=e.attrib.get("site2", ""),
        b1=e.attrib.get("body1", ""),
        b2=e.attrib.get("body2", ""),
    )
    return f"<{e.tag}[{values}]/>"


# Extract the asset and body XML elements
def recursively_namespace(elem):
    raise DeprecationWarning("This function is deprecated.")
    if isinstance(elem, lxml.etree._Element):
        for key, value in elem.attrib.items():
            if key.startswith("name"):
                elem.attrib[key] = "{name}-" + value
            if key.startswith("body"):
                elem.attrib[key] = "{name}-" + value
            if key.startswith("joint"):
                elem.attrib[key] = "{name}-" + value
            if key.startswith("site"):
                elem.attrib[key] = "{name}-" + value
            if key.startswith("tendon"):
                elem.attrib[key] = "{name}-" + value
            if key == "mesh":
                elem.attrib[key] = "{name}-" + value
            if key == "material":
                elem.attrib[key] = "{name}-" + value
            if key == "texture":
                elem.attrib[key] = "{name}-" + value
            if key.startswith("class"):
                elem.attrib[key] = "{name}-" + value
            if key.startswith("childclass"):
                elem.attrib[key] = "{name}-" + value

        if elem.tag == "mesh" and elem.attrib.get("name") is None and elem.attrib.get("file") is not None:
            elem.attrib["name"] = "{name}-" + Path(elem.attrib.get("file")).stem
        for child in elem:
            recursively_namespace(child)

    if isinstance(elem, str):
        elem = etree.fromstring("<wrapper>" + elem + "</wrapper>")
        recursively_namespace(elem)
        elem = "\n".join([etree.tostring(child, encoding="unicode", pretty_print=True) for child in elem])
        return elem

    return None


class MjNode(XmlTemplate):
    template = """
    <{tag} {attributes}>{children}</{tag}>
    """

    _assets = None

    @property
    def assets(self):
        cwd = Path.cwd()

        print("setter", self.__class__, self.__class__.__module__)

        file_path = sys.modules[self.__class__.__module__].__file__

        asset_path = Path(file_path).parent

        if self._assets:
            asset_path /= self._assets

        try:
            return asset_path.relative_to(cwd)
        except ValueError as e:
            print("\033[91msetting relative path failed\033[0m", e)
            return asset_path.absolute()

        return "."

    @assets.setter
    def assets(self, value=None):
        if value is None:
            return

        self._assets = value

    def __init__(
        self,
        *_children,
        attributes=None,
        preamble: str = None,
        postamble: str = None,
        children: Xml | List[Xml] = None,
        **kwargs,
    ):
        super().__init__(
            *_children,
            preamble=preamble,
            children=children,
            postamble=postamble,
            **attributes or {},
        )

        from vuer_mujoco.schemas.se3.se3_mujoco import Vector3, WXYZ

        self._pos = Vector3(0, 0, 0)
        self._quat = WXYZ(1, 0, 0, 0)

        for k, v in kwargs.items():
            setattr(self, k, v)

        # Ge: this is breaking the insertion box environment.
        # for k in dir(self):
        #     if isinstance(getattr(self, k), str) and k.startswith("_") and k not in ["_minimized", "_xml", "__doc__", "__module__"]:
        #         setattr(self, k, recursively_namespace(getattr(self, k)))

    def join(self, *s):
        return merge_many(*s, hash_fn=mujoco_hash)

    @property
    def _files(self):
        import re

        for seg in [self.preamble, self.children, self.postamble]:
            if not isinstance(seg, str):
                continue
            matches = re.findall(r'file="([^"]*)"', seg)
            for match in matches:
                yield match


class Body(MjNode):
    """
    Robot link element.

    Inside link.content, you can define the body of the link, including the inertial properties, joint properties, and geometry properties.
    Inside link.asset, you can define the material, mesh or texture properties.

    name should be a unique identifier for the link.
    """

    tag = "body"

    def __init__(self, *_children, pos=None, quat=None, **kwargs):
        super().__init__(*_children, **kwargs)

        import vuer_mujoco.schemas.se3.se3_mujoco as m

        if pos:
            self._pos = m.Vector3(*pos)
            # we use reference here to enable auto update.
            self._attributes["pos"] = self._pos
        if quat:
            self._quat = m.WXYZ(*quat)
            # we use reference here to enable auto update
            self._attributes["quat"] = self._quat
        # Maybe add matrix?


class Composite(MjNode):
    """
    Robot link element.

    Inside link.content, you can define the body of the link, including the inertial properties, joint properties, and geometry properties.
    Inside link.asset, you can define the material, mesh or texture properties.

    name should be a unique identifier for the link.
    """

    tag = "composite"

    def __init__(self, *_children, pos=None, quat=None, **kwargs):
        super().__init__(*_children, **kwargs)
        import vuer_mujoco.schemas.se3.se3_mujoco as m

        if pos:
            # We do not use pos, instead we create an attribute for offset.
            self._pos = m.Vector3(*pos)
            # we use reference here to enable auto update.
            self._attributes["offset"] = self._pos


class Mjcf(MjNode):
    """
    This is the root element of the MuJoCo XML file.

    """

    tag = "mujoco"

    def __init__(self, *_children, pos=None, quat=None, **kwargs):
        super().__init__(*_children, **kwargs)

        import vuer_mujoco.schemas.se3.se3_mujoco as m

        # The root MuJoCo model class does not want to include these
        # in the attributes.
        if pos:
            self._pos = m.Vector3(*pos)
        if quat:
            self._quat = m.WXYZ(*quat)

    # _preamble = """
    # <compiler angle="radian" autolimits="true" assetdir="cached" meshdir="cached" texturedir="cached"/>
    # <!--<statistic center="0.2 0 0.4" extent=".65"/>-->
    #
    # <visual>
    #   <headlight diffuse="0.6 0.6 0.6" ambient="0.3 0.3 0.3" specular="0 0 0"/>
    #   <rgba haze="0.15 0.25 0.35 1"/>
    #   <global azimuth="150" elevation="-20" offwidth="1280" offheight="1024"/>
    # </visual>
    #
    # <asset>
    #   <texture type="skybox" builtin="gradient" rgb1="0.3 0.5 0.7" rgb2="0 0 0" width="512" height="3072"/>
    #   <texture type="2d" name="groundplane" builtin="checker" mark="edge" rgb1="0.2 0.3 0.4" rgb2="0.1 0.2 0.3"
    #     markrgb="0.8 0.8 0.8" width="300" height="300"/>
    #   <material name="groundplane" texture="groundplane" texuniform="true" texrepeat="5 5" reflectance="0.2"/>
    # </asset>
    # """

    template = """
    <mujoco {attributes}>
        <default>
            <geom solref="0.003 1" solimp="0.95 0.99 0.001"/>
        </default>
        {preamble}
        <worldbody>
            {children}
        </worldbody>
        {postamble}
    </mujoco>
    """

    def save(self, fname: str):
        from vuer_mujoco.schemas.utils.file import Prettify

        xml_str = self._xml | Prettify()

        with open(fname, "w") as f:
            f.write(xml_str)


# class BoxExample(Body):
#     name = "box-1"
#     """this is a placeholder name."""
#
#     @property
#     def preamble(self):
#         return f"""
#         <asset>
#             <texture name="{self.name}" type="2d" builtin="checker" rgb1="0.2 0.3 0.4" rgb2="0.1 0.2 0.3" mark="cross" width="200" height="200"/>
#             <material name="matplane" reflectance="0.5" texture="texplane" texrepeat="1 1" texuniform="true"/>
#         </asset>
#         """

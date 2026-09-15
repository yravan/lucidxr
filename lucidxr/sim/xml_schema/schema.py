from __future__ import annotations

import re
from typing import List

from lxml import etree

from lucidxr.sim.xml_schema.base import Xml, XmlTemplate
from lucidxr.sim.xml_schema.utils.tree_merge import merge_many


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


class MjNode(XmlTemplate):
    template = """
    <{tag} {attributes}>{children}</{tag}>
    """

    def __init__(
        self,
        *_children,
        attributes=None,
        preamble: str = None,
        postamble: str = None,
        children: Xml | List[Xml] = None,
        **kwargs,
    ):
        # Copy legacy template attributes; never retain a caller's mutable mapping.
        attributes = {**(kwargs.pop("_attributes", None) or {}), **(attributes or {})}
        if self.tag != "mujoco":
            for key in ("name", "childclass"):
                if key in kwargs:
                    attributes[key] = kwargs[key]
        super().__init__(
            *_children,
            preamble=preamble,
            children=children,
            postamble=postamble,
            **attributes or {},
        )

        from lucidxr.sim.xml_schema.transforms.mujoco import WXYZ, Vector3

        self._pos = Vector3(0, 0, 0)
        self._quat = WXYZ(1, 0, 0, 0)

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getattr__(self, name):
        attributes = self.__dict__.get("_attributes", {})
        if name in attributes:
            return attributes[name]
        raise AttributeError(f"{type(self).__name__!s} has no attribute {name!r}")

    def referenced_files(self) -> tuple[str, ...]:
        """Asset references in this component, in declaration order."""
        return tuple(
            dict.fromkeys(re.findall(r'file="([^"\n]*)"', self._xml + self.preamble + self.postamble))
        )

    @property
    def _files(self):
        return iter(self.referenced_files())

    def join(self, *s):
        return merge_many(*s, hash_fn=mujoco_hash)


def comment_out_joints(xml_str: str) -> str:
    """
    Comment out <joint .../> or <joint ...>...</joint> in an MJCF XML string.
    Pure string processing (regex), no XML parser.
    """
    # Matches <joint .../> self-closing tags
    xml_str = re.sub(r"(<joint\b[^>]*/>)", r"<!-- \1 -->", xml_str)

    # Matches <joint ...> ... </joint> block tags (multi-line safe)
    xml_str = re.sub(r"(<joint\b[^>]*>.*?</joint>)", r"<!-- \1 -->", xml_str, flags=re.DOTALL)

    return xml_str


class Group(MjNode):
    """A collection of MJCF components with no enclosing XML element.

    Unlike Body, grouping does not transform children or introduce dynamics.
    Subclasses may use pos/quat as construction origins for their members.
    """

    template = "{children}"

    def __init__(self, *children, pos=None, quat=None, **kwargs):
        super().__init__(*children, **kwargs)
        from lucidxr.sim.xml_schema.transforms.mujoco import WXYZ, Vector3

        if pos is not None:
            self._pos = Vector3(*(map(float, pos.split()) if isinstance(pos, str) else pos))
        if quat is not None:
            self._quat = WXYZ(*(map(float, quat.split()) if isinstance(quat, str) else quat))


class Body(MjNode):
    """
    Robot link element.

    Inside link.content, you can define the body of the link, including the inertial properties, joint properties, and geometry properties.
    Inside link.asset, you can define the material, mesh or texture properties.

    name should be a unique identifier for the link.
    """

    tag = "body"

    def __init__(self, *_children, pos=None, quat=None, remove_joints=False, **kwargs):
        super().__init__(*_children, **kwargs)

        import lucidxr.sim.xml_schema.transforms.mujoco as m

        if pos is not None:
            self._pos = m.Vector3(*(map(float, pos.split()) if isinstance(pos, str) else pos))
            # we use reference here to enable auto update.
            self._attributes["pos"] = self._pos
        if quat is not None:
            self._quat = m.WXYZ(*(map(float, quat.split()) if isinstance(quat, str) else quat))
            # we use reference here to enable auto update
            self._attributes["quat"] = self._quat
        if remove_joints:
            self._children_raw = self._children_raw.replace("<freejoint/>", "")
            self.template = self.template.replace("<freejoint/>", "")
            self._children_raw = comment_out_joints(self._children_raw)
            self.template = comment_out_joints(self.template)
        # Maybe add matrix?


class FreeBody(Body):
    """A body with an unconstrained six-degree-of-freedom joint."""

    def __init__(self, *children, joint_name=None, **kwargs):
        supplied = kwargs.pop("children", None)
        if supplied is not None:
            if children:
                raise TypeError("Use positional children or children=, not both")
            children = (supplied,) if isinstance(supplied, (str, Xml)) else tuple(supplied)
        joint = Xml(tag="freejoint", **({"name": joint_name} if joint_name is not None else {}))
        super().__init__(*children, joint, **kwargs)


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
        import lucidxr.sim.xml_schema.transforms.mujoco as m

        if pos is not None:
            # We do not use pos, instead we create an attribute for offset.
            self._pos = m.Vector3(*(map(float, pos.split()) if isinstance(pos, str) else pos))
            # we use reference here to enable auto update.
            self._attributes["offset"] = self._pos


class Replicate(MjNode):
    """
    This is a replicate element, which can be used to replicate a body or a composite.

    name should be a unique identifier for the link.
    """

    tag = "replicate"



class Mjcf(MjNode):
    """
    This is the root element of the MuJoCo XML file.

    """

    tag = "mujoco"

    def __init__(self, *_children, pos=None, quat=None, **kwargs):
        super().__init__(*_children, **kwargs)

        import lucidxr.sim.xml_schema.transforms.mujoco as m

        # The root MuJoCo model class does not want to include these
        # in the attributes.
        if pos is not None:
            self._pos = m.Vector3(*(map(float, pos.split()) if isinstance(pos, str) else pos))
        if quat is not None:
            self._quat = m.WXYZ(*(map(float, quat.split()) if isinstance(quat, str) else quat))

    template = """
    <mujoco {attributes}>
        {preamble}
        <worldbody>
            {children}
        </worldbody>
        {postamble}
    </mujoco>
    """

    def save(self, fname: str):
        from lucidxr.sim.xml_schema.utils.file import Prettify

        xml_str = self._xml | Prettify()

        with open(fname, "w") as f:
            f.write(xml_str)

"""Light elements use the same attribute serialization as other XML nodes."""

from lucidxr.sim.xml_schema.base import Raw, Xml


def make_light(name="light", *, pos, **attributes) -> Raw:
    return Raw(str(Xml(tag="light", name=name, pos=pos, **attributes)))

"""A free rigid cube, independent of any scene layout."""

from lucidxr.sim.xml_schema.schema import FreeBody


class Cube(FreeBody):
    half_size = 0.025
    mass = 0.25
    rgba = "1 0 0 1"
    _children_raw = """
    <geom name="{name}" type="box" size="{half_size} {half_size} {half_size}"
          rgba="{rgba}" mass="{mass}"/>
    """

    def __init__(self, name="cube", **kwargs):
        super().__init__(name=name, joint_name=name, **kwargs)

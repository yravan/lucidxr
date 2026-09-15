"""Bodies constrained to translation in the XY plane."""

from lucidxr.sim.xml_schema.schema import Body


class XYBody(Body):
    _attributes = {
        "name": "floating-base",
    }
    _children_raw = """
      <joint name="{name}-floating-base_x" type="slide" axis="1 0 0"/>
       <joint name="{name}-floating-base_y" type="slide" axis="0 1 0"/>
    """

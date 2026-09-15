"""Rigid stacking block with a colored top face and a collision marker."""

from lucidxr.sim.xml_schema.schema import Body


class StackingBlock(Body):
    rgba = "0 1 0 1"
    top_rgba = "0 0 1 1"
    _attributes = {"name": "block"}
    _preamble = """
          <asset>
            <material name="{name}-material" rgba="{rgba}" specular="1.0" shininess="1.0" reflectance="0.3"/>
            <material name="{name}-top-material" rgba="{top_rgba}" specular="1.0" shininess="1.0"/>
          </asset>
        """
    _children_raw = """
          <joint name="{name}-cube_joint0" type="free" limited="false" actuatorfrclimited="false"/>
          <geom name="{name}-cube_g0" size="0.021556 0.0218909 0.02073" type="box" rgba="{rgba}"/>
          <geom name="{name}-cube_g0_vis" size="0.021556 0.0218909 0.02073" type="box" contype="0" conaffinity="0" group="1" mass="0" material="{name}-material"/>
          <geom name="{name}-top_face" type="box" size="0.021556 0.0218909 0.001" pos="0 0 0.021" contype="0" conaffinity="0" group="1" mass="0" material="{name}-top-material"/>
          <site name="{name}-cube_default_site" pos="0 0 0" size="0.002" rgba="1 0 0 -1"/>
        """

from vuer_mujoco.schemas.schema import Body


class Table(Body):
    _attributes = {
        "name": "table",
    }
    _preamble = """
    <asset>
      <material name="{name}-table" rgba="0.6 0.54 0.48 1" shininess="0.5"/>
    </asset>
    """
    _children_raw = """
    <geom name="{name}-table" type="box" material="{name}-table" size="0.5 0.7 0.05" pos="0 0 -0.05" solref="0.003 1" solimp="0.95 0.99 0.001" friction="2 0.01 0.002"/>
    """

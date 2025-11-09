from vuer_mujoco.schemas.schema import Body, Xml


class Bagel(Body):
    assets: str = 'bagel'
    end_effector: Xml

    def __init__(self, name: str = "bagel", **kwargs):
        super().__init__(name=name, **kwargs)

    _attributes = {
        "name": "bagel",
        "childclass": "bagel",
        "pos": "0 0 0",
        "quat": "0.707 -0.707 0 0",
    }

    _preamble = """
    <default>
      <default class="{childclass}">
        <default class="{childclass}-visual">
          <geom type="mesh" contype="0" conaffinity="0" group="2"/>
        </default>
        <default class="{childclass}-collision">
          <geom type="box" group="3" contype="1" conaffinity="1"/>
        </default>
      </default>
    </default>

    <asset>
      <mesh file="{assets}/bagel_0.obj" scale="0.05 0.05 0.05"/>
      <mesh file="{assets}/bagel_1.obj" scale="0.05 0.05 0.05"/>
    </asset>
    """

    template = """
    <body {attributes}>
      <freejoint/>
      <inertial mass="0.1" pos="0 0 0" diaginertia="0.00443333156 0.00443333156 0.0072"/>
      <body name="{name}-base">
        <inertial mass="0.1" pos="0 0 0" diaginertia="0.0102675 0.0102675 0.00666"/>
        <geom mesh="bagel_0" class="{childclass}-visual"/>
        <geom mesh="bagel_1" class="{childclass}-visual"/>
        <geom class="{childclass}-collision" mesh="bagel_0"/>
        <geom class="{childclass}-collision" mesh="bagel_1"/>
      </body>
    </body>
    """

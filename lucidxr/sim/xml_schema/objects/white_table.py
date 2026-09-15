from lucidxr.sim.xml_schema.schema import Body


class TableWhiteModern(Body):
    """table"""

    assets: str = "table_white_modern"

    _attributes = {
        "name": "table_white_modern",
        "childclass": "table_white_modern",
        "pos": "0 0 0",
        "quat": "1 0 0 0",
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
      <mesh file="{assets}/white_desk_0.obj" scale="0.2 0.2 0.2"/>
      <mesh file="{assets}/white_desk_1.obj" scale="0.2 0.2 0.2"/>
    </asset>
    """

    template = """
    <body {attributes}>
      <inertial mass="4.0" pos="0 0 0" diaginertia="0.00443333156 0.00443333156 0.0072"/>
      <body name="{name}-base" pos="0 0 0.0815">
        <inertial mass="3.7" pos="0 0 0" diaginertia="0.0102675 0.0102675 0.00666"/>
        <geom mesh="white_desk_0" class="{childclass}-visual"/>
        <!--geom class="{childclass}-collision" mesh="white_desk_0"/-->
        <geom class="{childclass}-collision" type="box" size="1 2 0.05" rgba="1 0 0 0.4" pos="0.7 0 1.55" quat="1 0 0 0"/>
      </body>
      
        <!--body name="{name}-base-collision" pos="0.7 0 1.64">
          <geom type="box" size="1 2 0.05" rgba="1 0 0 0.4" quat="0.707 0 0 0.707"/>
        </body-->
        
      <!--body name="{name}-floor" pos="0 -2 0.0815" quat="0 0.707 0.707 0">
        <inertial mass="3.7" pos="0 0 0" diaginertia="0.0102675 0.0102675 0.00666"/>
        <geom mesh="white_desk_1" class="{childclass}-visual"/>
        <geom class="{childclass}-collision" size="0.6 0.4 0.02" pos="0 0 0"/>
      </body-->
    </body>
    """

    _postamble = """
    """

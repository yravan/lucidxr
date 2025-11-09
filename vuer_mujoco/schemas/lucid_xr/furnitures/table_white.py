from vuer_mujoco.schemas.base import Xml
from vuer_mujoco.schemas.schema import Body
from vuer_mujoco.schemas.robots.ur5e import UR5e

from os.path import join

asset_rel_path = join('schemas', 'lucid_xr', 'furnitures')


class Triad(Body):
    name = ""
    template = """
    <body name="{name}-triad-x" pos="1 0 0">
      <geom type="box" size="0.05 0.05 0.05" rgba="1 0 0 0.5"/>
    </body>
    <body name="{name}-axis-x" pos="0.5 0 0">
      <geom type="box" size="0.5 0.01 0.01" rgba="1 0 0 0.5"/>
    </body>
    
    <body name="{name}-triad-y" pos="0 1 0">
      <geom type="box" size="0.05 0.05 0.05" rgba="0 1 0 0.5"/>
    </body>
    <body name="{name}-axis-y" pos="0 0.5 0">
      <geom type="box" size="0.01 0.5 0.01" rgba="0 1 0 0.5"/>
    </body>
    
    <body name="{name}-triad-z" pos="0 0 1">
      <geom type="box" size="0.05 0.05 0.05" rgba="0 0 1 0.5"/>
    </body>
    <body name="{name}-axis-z" pos="0 0 0.5">
      <geom type="box" size="0.01 0.01 0.5" rgba="0 0 1 0.5"/>
    </body>
    """


class TableDummy(Body):
    template = """
    <body {attributes}>
      <geom type="box" size="{size}" rgba="{rgba}"/>
    </body>
    """


class TableWhiteModern(Body):
    """table"""

    ## relative path from `lucidxr/docs/robots/` where the `ur5e_table_scene.py` is located
    # assets: str = join("../..", asset_rel_path, 'table_white_modern')
    assets: str = 'table_white_modern'
    end_effector: Xml

    def __init__(self, name: str = "table_white_modern", robot: Xml = None, **kwargs):
        super().__init__(name=name, **kwargs)
        self._children = self._children + (robot,)

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


class UR5eForTable(UR5e):
    pass
    # _postamble = """
    # <actuator>
    #   <general class="{childclass}-size3" name="{name}-shoulder_pan" joint="{name}-shoulder_pan_joint"/>
    #   <general class="{childclass}-size3" name="{name}-shoulder_lift" joint="{name}-shoulder_lift_joint"/>
    #   <general class="{childclass}-size3_limited" name="{name}-elbow" joint="{name}-elbow_joint"/>
    #   <general class="{childclass}-size1" name="{name}-wrist_1" joint="{name}-wrist_1_joint"/>
    #   <general class="{childclass}-size1" name="{name}-wrist_2" joint="{name}-wrist_2_joint"/>
    #   <general class="{childclass}-size1" name="{name}-wrist_3" joint="{name}-wrist_3_joint"/>
    # </actuator>
    # """



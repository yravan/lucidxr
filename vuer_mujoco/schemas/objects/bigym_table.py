from vuer_mujoco.schemas.schema import Body


class BigymTable(Body):
    """
    This class represents a Vuer Mug SDF body instance with pre-configured
    assets and attributes. The Signed Distance Field (SDF) is computed
    only once and reused for all instances, ensuring efficient field
    computation regardless of the number of instances.
    """

    assets = "bigym-table"

    _attributes = {
        "name": "bigym-table",
    }

    _preamble = """
    <asset>
      <texture type="2d" name="{name}-table" file="{assets}/table.png"/>
      <material name="{name}-table" specular="0.3" shininess="0.5" rgba="0.62 0.62 0.6 1" texture="{name}-table"/>
      <material name="{name}-table_legs" specular="0.3" shininess="0.5" rgba="1 1 1 1" texture="{name}-table"/>
      <mesh name="{name}-table" file="{assets}/table.obj"/>
      <mesh name="{name}-table_legs" file="{assets}/table_legs.obj"/>
      <mesh name="{name}-table_collision_001" file="{assets}/table_collision_001.obj"/>
      <mesh name="{name}-table_collision_002" file="{assets}/table_collision_002.obj"/>
      <mesh name="{name}-table_collision_003" file="{assets}/table_collision_003.obj"/>
      <mesh name="{name}-table_collision_004" file="{assets}/table_collision_004.obj"/>
      <mesh name="{name}-table_collision_005" file="{assets}/table_collision_005.obj"/>
      <mesh name="{name}-table_collision_006" file="{assets}/table_collision_006.obj"/>
      <mesh name="{name}-table_collision_007" file="{assets}/table_collision_007.obj"/>
    </asset>
    <default>
      <default class="{name}-table">
        <default class="{name}-visual">
          <geom type="mesh" contype="0" conaffinity="0" group="2" euler="1.5708 0 0"/>
        </default>
        <default class="{name}-collision">
          <geom type="mesh" group="3" euler="1.5708 0 0"/>
        </default>
      </default>
    </default>
    """

    _children_raw = """"
    <body name="{name}-table" childclass="{name}-table">
      <geom name="{name}-mesh" mesh="{name}-table" class="{name}-visual" material="{name}-table"/>
      <geom name="{name}-mesh_legs" mesh="{name}-table_legs" class="{name}-visual" material="{name}-table_legs"/>
      <geom name="{name}-collider_001" mesh="{name}-table_collision_001" class="{name}-collision"/>
      <geom name="{name}-collider_002" mesh="{name}-table_collision_002" class="{name}-collision"/>
      <geom name="{name}-collider_003" mesh="{name}-table_collision_003" class="{name}-collision"/>
      <geom name="{name}-collider_004" mesh="{name}-table_collision_004" class="{name}-collision"/>
      <geom name="{name}-collider_005" mesh="{name}-table_collision_005" class="{name}-collision"/>
      <geom name="{name}-collider_006" mesh="{name}-table_collision_006" class="{name}-collision"/>
      <geom name="{name}-collider_007" mesh="{name}-table_collision_007" class="{name}-collision"/>
    </body>
    """

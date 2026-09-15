from lucidxr.sim.xml_schema.schema import Body


class BigymDishDrainer(Body):
    """
    This class represents a Vuer Mug SDF body instance with pre-configured
    assets and attributes. The Signed Distance Field (SDF) is computed
    only once and reused for all instances, ensuring efficient field
    computation regardless of the number of instances.
    """

    assets = "objects/bigym-dishdrainer"

    _attributes = {
        "name": "bigym-dishdrainer",
    }

    _preamble = """
    <default>
      <default class="{name}-dish_drainer">
        <material specular="0.5" shininess="0.25"/>
        <default class="{name}-visual">
          <geom type="mesh" mass="0.1" contype="0" conaffinity="0" group="2" euler="1.5708 0 0"/>
        </default>
        <default class="{name}-collision">
          <geom type="mesh" mass="0" group="3" friction="0.5" euler="1.5708 0 0" priority="1"/>
        </default>
        <site size="0.001" rgba="0.5 0.5 0.5 0.3" group="4"/>
      </default>
    </default>
    <asset>
      <texture type="2d" name="{name}-dish_drainer_diffuse" file="{assets}/drying_rack.png"/>
      <material name="{name}-dish_drainer" texture="{name}-dish_drainer_diffuse"/>
      <mesh name="{name}-rack" file="{assets}/rack.obj"/>
      <mesh name="{name}-rack_collision_001" file="{assets}/rack_collision_001.obj"/>
      <mesh name="{name}-rack_collision_002" file="{assets}/rack_collision_002.obj"/>
      <mesh name="{name}-rack_collision_003" file="{assets}/rack_collision_003.obj"/>
      <mesh name="{name}-rack_collision_004" file="{assets}/rack_collision_004.obj"/>
      <mesh name="{name}-rack_collision_005" file="{assets}/rack_collision_005.obj"/>
      <mesh name="{name}-rack_collision_006" file="{assets}/rack_collision_006.obj"/>
      <mesh name="{name}-rack_collision_007" file="{assets}/rack_collision_007.obj"/>
      <mesh name="{name}-rack_collision_008" file="{assets}/rack_collision_008.obj"/>
      <mesh name="{name}-rack_collision_009" file="{assets}/rack_collision_009.obj"/>
      <mesh name="{name}-rack_collision_010" file="{assets}/rack_collision_010.obj"/>
      <mesh name="{name}-rack_collision_011" file="{assets}/rack_collision_011.obj"/>
      <mesh name="{name}-rack_collision_012" file="{assets}/rack_collision_012.obj"/>
      <mesh name="{name}-rack_collision_013" file="{assets}/rack_collision_013.obj"/>
      <mesh name="{name}-rack_collision_014" file="{assets}/rack_collision_014.obj"/>
      <mesh name="{name}-rack_collision_015" file="{assets}/rack_collision_015.obj"/>
      <mesh name="{name}-rack_collision_016" file="{assets}/rack_collision_016.obj"/>
      <mesh name="{name}-rack_collision_017" file="{assets}/rack_collision_017.obj"/>
      <mesh name="{name}-rack_collision_018" file="{assets}/rack_collision_018.obj"/>
    </asset>
    """

    _children_raw = """
    <body name="{name}-dish_drainer" childclass="{name}-dish_drainer">
      <geom material="{name}-dish_drainer" mesh="{name}-rack" class="{name}-visual"/>
      <geom mesh="{name}-rack_collision_001" class="{name}-collision"/>
      <geom mesh="{name}-rack_collision_002" class="{name}-collision"/>
      <geom mesh="{name}-rack_collision_003" class="{name}-collision"/>
      <geom mesh="{name}-rack_collision_004" class="{name}-collision"/>
      <geom mesh="{name}-rack_collision_005" class="{name}-collision"/>
      <geom mesh="{name}-rack_collision_006" class="{name}-collision"/>
      <geom mesh="{name}-rack_collision_007" class="{name}-collision"/>
      <geom mesh="{name}-rack_collision_008" class="{name}-collision"/>
      <geom mesh="{name}-rack_collision_009" class="{name}-collision"/>
      <geom mesh="{name}-rack_collision_010" class="{name}-collision"/>
      <geom mesh="{name}-rack_collision_011" class="{name}-collision"/>
      <geom mesh="{name}-rack_collision_012" class="{name}-collision"/>
      <geom mesh="{name}-rack_collision_013" class="{name}-collision"/>
      <geom mesh="{name}-rack_collision_014" class="{name}-collision"/>
      <geom mesh="{name}-rack_collision_015" class="{name}-collision"/>
      <geom mesh="{name}-rack_collision_016" class="{name}-collision"/>
      <geom mesh="{name}-rack_collision_017" class="{name}-collision"/>
      <geom mesh="{name}-rack_collision_018" class="{name}-collision"/>
      <!--Use helpers below to align placement of objects in the rack-->
      <site name="{name}-plate_slot_1" pos="0 0.105 0.15" euler="1.5708 0 0"/>
      <site name="{name}-plate_slot_2" pos="0 0.063 0.15" euler="1.5708 0 0"/>
      <site name="{name}-plate_slot_3" pos="0 0.021 0.15" euler="1.5708 0 0"/>
      <site name="{name}-plate_slot_4" pos="0 -0.021 0.15" euler="1.5708 0 0"/>
      <site name="{name}-plate_slot_5" pos="0 -0.063 0.15" euler="1.5708 0 0"/>
      <site name="{name}-plate_slot_6" pos="0 -0.105 0.15" euler="1.5708 0 0"/>
    </body>
    """

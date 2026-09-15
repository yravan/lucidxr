from lucidxr.sim.xml_schema.schema import Body


class BigymPlate(Body):
    """
    This class represents a Vuer Mug SDF body instance with pre-configured
    assets and attributes. The Signed Distance Field (SDF) is computed
    only once and reused for all instances, ensuring efficient field
    computation regardless of the number of instances.
    """

    assets = "objects/bigym-plate"

    _attributes = {
        "name": "bigym-plate",
    }

    _preamble = """
    <asset>
      <material name="{name}-plate" specular="0.5" shininess="0.25"/>
      <mesh name="{name}-plate_01" file="{assets}/plate_01.obj"/>
      <mesh name="{name}-plate_01_collision" file="{assets}/plate_01_collision.obj"/>
    </asset>
    
    <default>
      <default class="{name}-plate">
        <default class="{name}-visual">
          <geom type="mesh" mass="0.4" contype="0" conaffinity="0" group="2" euler="1.5708 0 0"/>
        </default>
        <default class="{name}-collision">
          <geom type="mesh" mass="0" group="3" euler="1.5708 0 0" solimp=".95 .99 0.001" solref="0.004 1"/>
        </default>
      </default>
    </default>
    """

    _children_raw = """
    <body name="{name}-plate" childclass="{name}-plate">
      <geom name="{name}-mesh" material="{name}-plate" mesh="{name}-plate_01" class="{name}-visual"/>
      <geom name="{name}-collider" mesh="{name}-plate_01_collision" class="{name}-collision"/>
    </body>
    """

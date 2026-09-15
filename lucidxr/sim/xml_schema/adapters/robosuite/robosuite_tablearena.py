from lucidxr.sim.xml_schema.schema import Body


class RobosuiteTableArena(Body):
    """
    This class represents a Vuer Mug SDF body instance with pre-configured
    assets and attributes. The Signed Distance Field (SDF) is computed
    only once and reused for all instances, ensuring efficient field
    computation regardless of the number of instances.
    """

    table_pos = "0 0 0.6"
    table_pos_list = [0, 0, 0.6]

    _attributes = {
        "name": "robosuite-tablearena",
    }

    _preamble = """
    <compiler angle="radian" meshdir="meshes/"/>

    <option impratio="20" density="1.2" viscosity="2e-05" cone="elliptic"/>
  
    <size njmax="5000" nconmax="5000"/>
  
    <visual>
      <map znear="0.001"/>
    </visual>
    
    <default>
      <geom group="3"/>
    </default>
  
    <asset>
      <texture type="2d" name="texplane" file="textures/light-gray-floor-tile.png"/>
      <texture type="cube" name="tex-ceramic" file="textures/ceramic.png"/>
      <texture type="cube" name="tex-steel-brushed" file="textures/steel-brushed.png"/>
      <texture type="2d" name="tex-light-gray-plaster" file="textures/light-gray-plaster.png"/>
      <material name="floorplane" texture="texplane" texuniform="true" texrepeat="2 2" specular="0" shininess="0" reflectance="0.01"/>
      <material name="table_ceramic" texture="tex-ceramic" specular="0.2" shininess="0"/>
      <material name="table_legs_metal" texture="tex-steel-brushed" shininess="0.8" reflectance="0.8"/>
      <material name="walls_mat" texture="tex-light-gray-plaster" texuniform="true" texrepeat="3 3" specular="0.1" shininess="0.1"/>
    </asset>
    """

    _children_raw = """
    <geom name="floor" size="3 3 0.125" type="plane" group="1" material="floorplane"/>
    <body name="table" pos="{table_pos}">
      <geom name="table_collision" size="0.75 0.3875 0.025" type="box" rgba="0.5 0.5 0 1"/>
      <geom name="table_visual" size="0.75 0.3875 0.025" type="box" contype="0" conaffinity="0" group="1" material="table_ceramic"/>
      <geom name="table_leg1_visual" size="0.025 0.3" pos="0.65 0.3 -0.3" type="cylinder" contype="0" conaffinity="0" group="1" material="table_legs_metal"/>
      <geom name="table_leg2_visual" size="0.025 0.3" pos="-0.65 0.3 -0.3" type="cylinder" contype="0" conaffinity="0" group="1" material="table_legs_metal"/>
      <geom name="table_leg3_visual" size="0.025 0.3" pos="-0.65 -0.3 -0.3" type="cylinder" contype="0" conaffinity="0" group="1" material="table_legs_metal"/>
      <geom name="table_leg4_visual" size="0.025 0.3" pos="0.65 -0.3 -0.3" type="cylinder" contype="0" conaffinity="0" group="1" material="table_legs_metal"/>
      <site name="table_top" pos="0 0 0.025" size="0.001" rgba="0 0 0 0"/>
    </body>
    """

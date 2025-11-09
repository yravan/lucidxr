from vuer_mujoco.schemas.schema import Body


class RobosuiteBin(Body):
    """
    This class represents a Vuer Mug SDF body instance with pre-configured
    assets and attributes. The Signed Distance Field (SDF) is computed
    only once and reused for all instances, ensuring efficient field
    computation regardless of the number of instances.
    """

    _attributes = {
        "name": "robosuite-bin",
    }

    _preamble = """
    
    <default>
      <geom group="3"/>
    </default>
    <asset>
      <texture type="2d" name="texplane" file="textures/light-gray-floor-tile.png"/>
      <texture type="2d" name="tex-light-wood" file="textures/light-wood.png"/>
      <texture type="cube" name="tex-steel-brushed" file="textures/steel-brushed.png"/>
      <material name="floorplane" texture="texplane" texuniform="true" texrepeat="2 2" specular="0" shininess="0" reflectance="0.01"/>
      <material name="light-wood" texture="tex-light-wood" texuniform="true" texrepeat="15 15"/>
      <material name="table_legs_metal" texture="tex-steel-brushed" shininess="0.8" reflectance="0.8"/>
    </asset>
    """

    _children_raw = """"
    <geom size="0.2 0.25 0.02" type="box" rgba="0.5 0.5 0 1"/>
      <geom size="0.2 0.25 0.02" type="box" contype="0" conaffinity="0" group="1" material="light-wood"/>
      <geom size="0.21 0.01 0.05" pos="0 0.25 0.05" type="box" rgba="0.5 0.5 0 1"/>
      <geom size="0.21 0.01 0.05" pos="0 0.25 0.05" type="box" contype="0" conaffinity="0" group="1" material="light-wood"/>
      <geom size="0.21 0.01 0.05" pos="0 -0.25 0.05" type="box" rgba="0.5 0.5 0 1"/>
      <geom size="0.21 0.01 0.05" pos="0 -0.25 0.05" type="box" contype="0" conaffinity="0" group="1" material="light-wood"/>
      <geom size="0.01 0.25 0.05" pos="0.2 0 0.05" type="box" rgba="0.5 0.5 0 1"/>
      <geom size="0.01 0.25 0.05" pos="0.2 0 0.05" type="box" contype="0" conaffinity="0" group="1" material="light-wood"/>
      <geom size="0.01 0.25 0.05" pos="-0.2 0 0.05" type="box" rgba="0.5 0.5 0 1"/>
      <geom size="0.01 0.25 0.05" pos="-0.2 0 0.05" type="box" contype="0" conaffinity="0" group="1" material="light-wood"/>
      <geom name="{name}-leg1_visual" size="0.01 0.3" pos="0.15 0.2 -0.3" type="cylinder" contype="0" conaffinity="0" group="1" material="table_legs_metal"/>
      <geom name="{name}-leg2_visual" size="0.01 0.3" pos="-0.15 0.2 -0.3" type="cylinder" contype="0" conaffinity="0" group="1" material="table_legs_metal"/>
      <geom name="{name}-leg3_visual" size="0.01 0.3" pos="-0.15 -0.2 -0.3" type="cylinder" contype="0" conaffinity="0" group="1" material="table_legs_metal"/>
      <geom name="{name}-leg4_visual" size="0.01 0.3" pos="0.15 -0.2 -0.3" type="cylinder" contype="0" conaffinity="0" group="1" material="table_legs_metal"/>
    """

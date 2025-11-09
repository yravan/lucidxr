from vuer_mujoco.schemas.schema import Body


class RobosuiteDoor(Body):
    """
    This class represents a Vuer Mug SDF body instance with pre-configured
    assets and attributes. The Signed Distance Field (SDF) is computed
    only once and reused for all instances, ensuring efficient field
    computation regardless of the number of instances.
    """

    _attributes = {
        "name": "robosuite-door",
    }

    _preamble = """
     <asset>
        <texture type="cube" name="Door_dark-wood" file="textures/dark-wood.png"/>
        <texture type="cube" name="Door_metal" file="textures/brass-ambra.png"/>
        <material name="Door_MatMetal" texture="Door_metal" specular="1" shininess="0.3" rgba="0.9 0.9 0.9 1"/>
        <material name="Door_MatDarkWood" texture="Door_dark-wood" texrepeat="3 3" specular="0.4" shininess="0.1"/>
    </asset>
    """

    _children_raw = """"
      <site name="Door_default_site" pos="0 0 0" size="0.002" rgba="1 0 0 0"/>
      <body name="Door_frame" pos="0.1 -0.2 0" quat="0.707388 0 0 0.706825">
        <inertial pos="0.3 0 0" quat="0.5 0.5 0.5 0.5" mass="7.85398" diaginertia="0.923301 0.764585 0.168533"/>
        <geom name="Door_r_frame" size="0.03 0.3" pos="0.555 0 0" type="cylinder" rgba="0.5 0 0 1"/>
        <geom name="Door_l_frame" size="0.03 0.3" pos="0.045 0 0" type="cylinder" rgba="0.5 0 0 1"/>
        <geom name="Door_r_frame_visual" size="0.03 0.3" pos="0.555 0 0" type="cylinder" contype="0" conaffinity="0" group="1" mass="0" rgba="1 1 1 1"/>
        <geom name="Door_l_frame_visual" size="0.03 0.3" pos="0.045 0 0" type="cylinder" contype="0" conaffinity="0" group="1" mass="0" rgba="1 1 1 1"/>
        <body name="Door_door" pos="0.3 0 0">
          <inertial pos="0.0296816 -0.00152345 0" quat="0.701072 0 0 0.713091" mass="2.43455" diaginertia="0.0913751 0.0521615 0.043714"/>
          <joint name="Door_hinge" pos="0.255 0 0" axis="0 0 1" limited="true" range="0 0.4" damping="0.1"/>
          <geom name="Door_panel" size="0.22 0.02 0.29" type="box" friction="1 1 1" rgba="0.5 0 0 1"/>
          <geom name="Door_panel_visual" size="0.22 0.02 0.29" type="box" contype="0" conaffinity="0" group="1" friction="1 1 1" mass="0" material="Door_MatDarkWood"/>
          <body name="Door_latch" pos="-0.175 0 -0.025">
            <inertial pos="-0.017762 0.0138544 0" quat="0.365653 0.605347 -0.36522 0.605365" mass="0.1" diaginertia="0.0483771 0.0410001 0.0111013"/>
            <joint name="Door_latch_joint" pos="0 0 0" axis="0 1 0" stiffness="1" limited="true" range="-1.57 1.57" frictionloss="0.1"/>
            <geom name="Door_handle_base" size="0.025 0.09375" pos="0 -0.03125 0" quat="0.707107 -0.707107 0 0" type="cylinder" rgba="0.5 0 0 1"/>
            <geom name="Door_handle" size="0.075 0.015 0.02" pos="0.075 -0.1 0" type="box" rgba="0.5 0 0 1"/>
            <geom name="Door_latch" size="0.025 0.0125 0.03125" pos="-0.03125 0.05 0" quat="0.707388 0 0.706825 0" type="box" rgba="0.5 0 0 1"/>
            <geom name="Door_latch_tip" size="0.025 0.0125" pos="-0.0625 0.05 0" quat="0.707388 0.706825 0 0" type="cylinder" rgba="0.5 0 0 1"/>
            <geom name="Door_handle_base_visual" size="0.025 0.09375" pos="0 -0.03125 0" quat="0.707107 -0.707107 0 0" type="cylinder" contype="0" conaffinity="0" group="1" mass="0" material="Door_MatMetal"/>
            <geom name="Door_handle_visual" size="0.075 0.015 0.02" pos="0.075 -0.1 0" type="box" contype="0" conaffinity="0" group="1" mass="0" material="Door_MatMetal"/>
            <geom name="Door_latch_visual" size="0.025 0.0125 0.03125" pos="-0.03125 0.05 0" quat="0.707388 0 0.706825 0" type="box" contype="0" conaffinity="0" group="1" mass="0" material="Door_MatMetal"/>
            <geom name="Door_latch_tip_visual" size="0.025 0.0125" pos="-0.0625 0.05 0" quat="0.707388 0.706825 0 0" type="cylinder" contype="0" conaffinity="0" group="1" mass="0" material="Door_MatMetal"/>
            <site name="Door_handle" pos="0.125 -0.1 0" size="0.02" rgba="0 0 1 0"/>
          </body>
        </body>
      </body>
    """

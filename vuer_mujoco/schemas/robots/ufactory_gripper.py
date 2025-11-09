from ..schema import Body


class UfactoryGripper(Body):
    """
    This is the Gripper for the Ufactory Xarm7 robot.
    """

    assets: str = "ufactory_xarm7"

    _attributes = {
        "name": "xarm7",
        "pos": "0 0 0",
        "quat": "1 0 0 0",
        "childclass": "xarm7",
    }
    
    _preamble = """
    <compiler angle="radian" autolimits="true"/>
    <option integrator="implicitfast"/>

    <asset>
      <material name="{name}-white" rgba="1 1 1 1"/>
      <material name="{name}-black" rgba="0.149 0.149 0.149 1"/>

      <mesh file="{assets}/base_link.stl"/>
      <mesh file="{assets}/left_outer_knuckle.stl"/>
      <mesh file="{assets}/left_finger.stl"/>
      <mesh file="{assets}/left_inner_knuckle.stl"/>
      <mesh file="{assets}/right_outer_knuckle.stl"/>
      <mesh file="{assets}/right_finger.stl"/>
      <mesh file="{assets}/right_inner_knuckle.stl"/>
    </asset>

    <default>
      <default class="{childclass}">
        <geom type="mesh" material="{name}-black"/>
        <joint range="0 0.85" axis="1 0 0" frictionloss="1"/>
        <site size="0.001" rgba="1 0 0 1" group="4"/>
        <general biastype="affine" forcerange="-50 50" ctrlrange="0 255" gainprm="0.333" biasprm="0 -100 -10"/>
        <default class="spring_link">
          <joint stiffness="0.05" springref="2.62" damping="0.00125"/>
        </default>
        <default class="driver">
          <joint armature="0.005" damping="0.1" solreflimit="0.005 1"/>
        </default>
        <default class="follower">
          <joint solreflimit="0.005 1"/>
        </default>
      </default>
    </default>
    """

    _children_raw = """
    <inertial pos="-0.00065489 -0.0018497 0.048028" quat="0.997403 -0.0717512 -0.0061836 0.000477479" mass="0.54156"
      diaginertia="0.000471093 0.000332307 0.000254799"/>
    <geom mesh="base_link" material="{name}-white"/>
    <body name="{name}-left_outer_knuckle" pos="0 0.035 0.059098">
      <inertial pos="0 0.021559 0.015181" quat="0.47789 0.87842 0 0" mass="0.033618"
        diaginertia="1.9111e-05 1.79089e-05 1.90167e-06"/>
      <joint name="{name}-left_driver_joint" class="driver"/>
      <geom material="{name}-black" mesh="left_outer_knuckle"/>
      <body name="{name}-left_finger" pos="0 0.035465 0.042039">
        <inertial pos="0 -0.016413 0.029258" quat="0.697634 0.115353 -0.115353 0.697634" mass="0.048304"
          diaginertia="1.88037e-05 1.7493e-05 3.56792e-06"/>
        <joint name="{name}-left_finger_joint" axis="-1 0 0" class="follower"/>
        <geom material="{name}-black" mesh="left_finger"/>
      </body>
    </body>
    <body name="{name}-left_inner_knuckle" pos="0 0.02 0.074098">
      <inertial pos="1.86601e-06 0.0220468 0.0261335" quat="0.664139 -0.242732 0.242713 0.664146" mass="0.0230126"
        diaginertia="8.34216e-06 6.0949e-06 2.75601e-06"/>
      <joint name="{name}-left_inner_knuckle_joint" class="spring_link"/>
      <geom material="{name}-black" mesh="left_inner_knuckle"/>
    </body>
    <body name="{name}-right_outer_knuckle" pos="0 -0.035 0.059098">
      <inertial pos="0 -0.021559 0.015181" quat="0.87842 0.47789 0 0" mass="0.033618"
        diaginertia="1.9111e-05 1.79089e-05 1.90167e-06"/>
      <joint name="{name}-right_driver_joint" axis="-1 0 0" class="driver"/>
      <geom material="{name}-black" mesh="right_outer_knuckle"/>
      <body name="{name}-right_finger" pos="0 -0.035465 0.042039">
        <inertial pos="0 0.016413 0.029258" quat="0.697634 -0.115356 0.115356 0.697634" mass="0.048304"
          diaginertia="1.88038e-05 1.7493e-05 3.56779e-06"/>
        <joint name="{name}-right_finger_joint" class="follower"/>
        <geom material="{name}-black" mesh="right_finger"/>
      </body>
    </body>
    <body name="{name}-right_inner_knuckle" pos="0 -0.02 0.074098">
      <inertial pos="1.866e-06 -0.022047 0.026133" quat="0.66415 0.242702 -0.242721 0.664144" mass="0.023013"
        diaginertia="8.34209e-06 6.0949e-06 2.75601e-06"/>
      <joint name="{name}-right_inner_knuckle_joint" axis="-1 0 0" class="spring_link"/>
      <geom material="{name}-black" mesh="right_inner_knuckle"/>
    </body>
    """

    _postamble = """
    <contact>
      <exclude body1="{name}-right_inner_knuckle" body2="{name}-right_outer_knuckle"/>
      <exclude body1="{name}-right_inner_knuckle" body2="{name}-right_finger"/>
      <exclude body1="{name}-left_inner_knuckle" body2="{name}-left_outer_knuckle"/>
      <exclude body1="{name}-left_inner_knuckle" body2="{name}-left_finger"/>
      <exclude body1="{name}-left_inner_knuckle" body2="{name}"/>
      <exclude body1="{name}-right_inner_knuckle" body2="{name}"/>
      <exclude body1="{name}-left_outer_knuckle" body2="{name}"/>
      <exclude body1="{name}-right_outer_knuckle" body2="{name}"/>
    </contact>

    <tendon>
      <fixed name="{name}-split">
        <joint joint="{name}-right_driver_joint" coef="0.5"/>
        <joint joint="{name}-left_driver_joint" coef="0.5"/>
      </fixed>
    </tendon>

    <equality>
      <connect anchor="0 0.015 0.015" body1="{name}-right_finger" body2="{name}-right_inner_knuckle" solref="0.005 1"/>
      <connect anchor="0 -0.015 0.015" body1="{name}-left_finger" body2="{name}-left_inner_knuckle" solref="0.005 1"/>
      <joint joint1="{name}-left_driver_joint" joint2="{name}-right_driver_joint" polycoef="0 1 0 0 0" solref="0.005 1"/>
    </equality>

    <actuator>
      <general class="{childclass}" name="{name}-fingers_actuator" tendon="{name}-split"/>
    </actuator>
    """
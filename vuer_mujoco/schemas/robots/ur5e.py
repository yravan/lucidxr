from ..base import Xml
from ..schema import Body


class UR5e(Body):
    """
    This is the Gripper for the Ufactory Xarm7 robot.
    """

    assets: str = "ur5e"
    end_effector: Xml

    def __init__(self, *_children, end_effector: Xml = None, **kwargs):
        super().__init__(*_children, **kwargs)
        self.end_effector = end_effector
        self._children = self._children + (end_effector,)

    _attributes = {
        "name": "ur5e",
        "childclass": "ur5e",
        "pos": "0 0 0",
        "quat": "1 0 0 0",
    }

    _preamble = """
    <default>
      <default class="{childclass}">
        <material specular="0.5" shininess="0.25"/>
        <joint axis="0 1 0" range="-6.28319 6.28319" armature="0.1"/>
        <general gaintype="fixed" biastype="affine" ctrlrange="-6.2831 6.2831" gainprm="2000" biasprm="0 -2000 -400"
          forcerange="-150 150"/>
        <default class="{childclass}-size3">
          <default class="{childclass}-size3_limited">
            <joint range="-3.1415 3.1415"/>
            <general ctrlrange="-3.1415 3.1415"/>
          </default>
        </default>
        <default class="{childclass}-size1">
          <general gainprm="500" biasprm="0 -500 -100" forcerange="-28 28"/>
        </default>
        <default class="{childclass}-visual">
          <geom type="mesh" contype="0" conaffinity="0" group="2"/>
        </default>
        <default class="{childclass}-collision">
          <geom type="capsule" group="3"/>
          <default class="{childclass}-eef_collision">
            <geom type="cylinder"/>
          </default>
        </default>
        <site size="0.001" rgba="0.5 0.5 0.5 0.3" group="4"/>
      </default>
    </default>

    <asset>
      <material class="{childclass}" name="{name}-black" rgba="0.033 0.033 0.033 1"/>
      <material class="{childclass}" name="{name}-jointgray" rgba="0.278 0.278 0.278 1"/>
      <material class="{childclass}" name="{name}-linkgray" rgba="0.82 0.82 0.82 1"/>
      <material class="{childclass}" name="{name}-urblue" rgba="0.49 0.678 0.8 1"/>

      <mesh file="{assets}/base_0.obj"/>
      <mesh file="{assets}/base_1.obj"/>
      <mesh file="{assets}/shoulder_0.obj"/>
      <mesh file="{assets}/shoulder_1.obj"/>
      <mesh file="{assets}/shoulder_2.obj"/>
      <mesh file="{assets}/upperarm_0.obj"/>
      <mesh file="{assets}/upperarm_1.obj"/>
      <mesh file="{assets}/upperarm_2.obj"/>
      <mesh file="{assets}/upperarm_3.obj"/>
      <mesh file="{assets}/forearm_0.obj"/>
      <mesh file="{assets}/forearm_1.obj"/>
      <mesh file="{assets}/forearm_2.obj"/>
      <mesh file="{assets}/forearm_3.obj"/>
      <mesh file="{assets}/wrist1_0.obj"/>
      <mesh file="{assets}/wrist1_1.obj"/>
      <mesh file="{assets}/wrist1_2.obj"/>
      <mesh file="{assets}/wrist2_0.obj"/>
      <mesh file="{assets}/wrist2_1.obj"/>
      <mesh file="{assets}/wrist2_2.obj"/>
      <mesh file="{assets}/wrist3.obj"/>
    </asset>
    """

    template = """
    <body {attributes}>
      <inertial mass="4.0" pos="0 0 0" diaginertia="0.00443333156 0.00443333156 0.0072"/>
      <geom mesh="base_0" material="{name}-black" class="{childclass}-visual"/>
      <geom mesh="base_1" material="{name}-jointgray" class="{childclass}-visual"/>
      <body name="{name}-shoulder_link" pos="0 0 0.163">
        <inertial mass="3.7" pos="0 0 0" diaginertia="0.0102675 0.0102675 0.00666"/>
        <joint name="{name}-shoulder_pan_joint" class="{childclass}-size3" axis="0 0 1"/>
        <geom mesh="shoulder_0" material="{name}-urblue" class="{childclass}-visual"/>
        <geom mesh="shoulder_1" material="{name}-black" class="{childclass}-visual"/>
        <geom mesh="shoulder_2" material="{name}-jointgray" class="{childclass}-visual"/>
        <geom class="{childclass}-collision" size="0.06 0.06" pos="0 0 -0.04"/>
        <body name="{name}-upper_arm_link" pos="0 0.138 0" quat="1 0 1 0">
          <inertial mass="8.393" pos="0 0 0.2125" diaginertia="0.133886 0.133886 0.0151074"/>
          <joint name="{name}-shoulder_lift_joint" class="{childclass}-size3"/>
          <geom mesh="upperarm_0" material="{name}-linkgray" class="{childclass}-visual"/>
          <geom mesh="upperarm_1" material="{name}-black" class="{childclass}-visual"/>
          <geom mesh="upperarm_2" material="{name}-jointgray" class="{childclass}-visual"/>
          <geom mesh="upperarm_3" material="{name}-urblue" class="{childclass}-visual"/>
          <geom class="{childclass}-collision" pos="0 -0.04 0" quat="1 1 0 0" size="0.06 0.06"/>
          <geom class="{childclass}-collision" size="0.05 0.2" pos="0 0 0.2"/>
          <body name="{name}-forearm_link" pos="0 -0.131 0.425">
            <inertial mass="2.275" pos="0 0 0.196" diaginertia="0.0311796 0.0311796 0.004095"/>
            <joint name="{name}-elbow_joint" class="{childclass}-size3_limited"/>
            <geom mesh="forearm_0" material="{name}-urblue" class="{childclass}-visual"/>
            <geom mesh="forearm_1" material="{name}-linkgray" class="{childclass}-visual"/>
            <geom mesh="forearm_2" material="{name}-black" class="{childclass}-visual"/>
            <geom mesh="forearm_3" material="{name}-jointgray" class="{childclass}-visual"/>
            <geom class="{childclass}-collision" pos="0 0.08 0" quat="1 1 0 0" size="0.055 0.06"/>
            <geom class="{childclass}-collision" size="0.038 0.19" pos="0 0 0.2"/>
            <body name="{name}-wrist_1_link" pos="0 0 0.392" quat="1 0 1 0">
              <inertial mass="1.219" pos="0 0.127 0" diaginertia="0.0025599 0.0025599 0.0021942"/>
              <joint name="{name}-wrist_1_joint" class="{childclass}-size1"/>
              <geom mesh="wrist1_0" material="{name}-black" class="{childclass}-visual"/>
              <geom mesh="wrist1_1" material="{name}-urblue" class="{childclass}-visual"/>
              <geom mesh="wrist1_2" material="{name}-jointgray" class="{childclass}-visual"/>
              <geom class="{childclass}-collision" pos="0 0.05 0" quat="1 1 0 0" size="0.04 0.07"/>
              <body name="{name}-wrist_2_link" pos="0 0.127 0">
                <inertial mass="1.219" pos="0 0 0.1" diaginertia="0.0025599 0.0025599 0.0021942"/>
                <joint name="{name}-wrist_2_joint" axis="0 0 1" class="{childclass}-size1"/>
                <geom mesh="wrist2_0" material="{name}-black" class="{childclass}-visual"/>
                <geom mesh="wrist2_1" material="{name}-urblue" class="{childclass}-visual"/>
                <geom mesh="wrist2_2" material="{name}-jointgray" class="{childclass}-visual"/>
                <geom class="{childclass}-collision" size="0.04 0.06" pos="0 0 0.04"/>
                <geom class="{childclass}-collision" pos="0 0.02 0.1" quat="1 1 0 0" size="0.04 0.04"/>
                <body name="{name}-wrist_3_link" pos="0 0 0.1">
                  <inertial mass="0.1889" pos="0 0.0771683 0" quat="1 0 0 1"
                    diaginertia="0.000132134 9.90863e-05 9.90863e-05"/>
                  <joint name="{name}-wrist_3_joint" class="{childclass}-size1"/>
                  <geom material="{name}-linkgray" mesh="wrist3" class="{childclass}-visual" pos="0 0 0.0001"/>
                  <geom class="{childclass}-eef_collision" pos="0 0.08 0" quat="1 1 0 0" size="0.04 0.02"/>
                  <site name="{name}-attachment_site" pos="0 0.1 0" quat="-1 1 0 0"/>
                  <body name="{name}-eef" pos="0 0.1 0" quat="-1 1 0 0">
                  {children}
                  </body>
                </body>
              </body>
            </body>
          </body>
        </body>
      </body>
    </body>
    """

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

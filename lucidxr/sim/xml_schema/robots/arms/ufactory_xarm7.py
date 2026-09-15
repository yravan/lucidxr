from lucidxr.sim.xml_schema.schema import Body


class Xarm7(Body):
    """
    This is the Xarm7 robot.

    By default, it will use 7 links defined here.

    efChildren is optional and can be used to add end effector to the robot.
    name is optional, if provided it will be used as the name of the robot and should be unique.
    If not provided, "panada<robot_id> will be used instead, where robot_id is unique.
    """

    assets: str = "robots/ufactory_xarm7"

    _attributes = {
        "name": "xarm7",
        "childclass": "xarm7",
        "pos": "0 0 0",
        "quat": "1 0 0 0",
    }

    _preamble = """
    <option integrator="implicitfast"/>

    <asset>
      <material name="{name}-white" rgba="1 1 1 1"/>
      <material name="{name}-gray" rgba="0.753 0.753 0.753 1"/>

      <mesh file="{assets}/link_base.stl"/>
      <mesh file="{assets}/link1.stl"/>
      <mesh file="{assets}/link2.stl"/>
      <mesh file="{assets}/link3.stl"/>
      <mesh file="{assets}/link4.stl"/>
      <mesh file="{assets}/link5.stl"/>
      <mesh file="{assets}/link6.stl"/>
      <mesh file="{assets}/link7.stl"/>
      <mesh file="{assets}/end_tool.stl"/>
    </asset>
    
    <default>
      <default class="{childclass}">
        <geom type="mesh" material="{name}-white"/>
        <joint axis="0 0 1" range="-6.28319 6.28319" frictionloss="1"/>
        <general biastype="affine" ctrlrange="-6.28319 6.28319"/>
        <default class="size1">
          <joint damping="10"/>
          <general gainprm="1500" biasprm="0 -1500 -150" forcerange="-50 50"/>
        </default>
        <default class="size2">
          <joint damping="5"/>
          <general gainprm="1000" biasprm="0 -1000 -100" forcerange="-30 30"/>
        </default>
        <default class="size3">
          <joint damping="2"/>
          <general gainprm="800" biasprm="0 -800 -80" forcerange="-20 20"/>
        </default>
        <site size="0.001" rgba="1 0 0 1" group="4"/>
      </default>
    </default>
    """

    template = """
    <body name="{name}-link_base" pos="0 0 .12" childclass="{childclass}">
      <inertial pos="-0.021131 -0.0016302 0.056488" quat="0.696843 0.20176 0.10388 0.680376" mass="0.88556"
        diaginertia="0.00382023 0.00335282 0.00167725"/>
      <geom mesh="link_base"/>
      <body name="{name}-link1" pos="0 0 0.267">
        <inertial pos="-0.0002 0.02905 -0.01233" quat="0.978953 -0.202769 -0.00441617 -0.0227264" mass="2.382"
          diaginertia="0.00569127 0.00533384 0.00293865"/>
        <joint name="{name}-joint1" class="size1"/>
        <geom mesh="link1"/>
        <body name="{name}-link2" quat="1 -1 0 0">
          <inertial pos="0.00022 -0.12856 0.01735" quat="0.50198 0.86483 -0.00778841 0.00483285" mass="1.869"
            diaginertia="0.00959898 0.00937717 0.00201315"/>
          <joint name="{name}-joint2" range="-2.059 2.0944" class="size1"/>
          <geom mesh="link2"/>
          <body name="{name}-link3" pos="0 -0.293 0" quat="1 1 0 0">
            <inertial pos="0.0466 -0.02463 -0.00768" quat="0.913819 0.289775 0.281481 -0.0416455" mass="1.6383"
              diaginertia="0.00351721 0.00294089 0.00195868"/>
            <joint name="{name}-joint3" class="size2"/>
            <geom mesh="link3"/>
            <body name="{name}-link4" pos="0.0525 0 0" quat="1 1 0 0">
              <inertial pos="0.07047 -0.11575 0.012" quat="0.422108 0.852026 -0.126025 0.282832" mass="1.7269"
                diaginertia="0.00657137 0.00647948 0.00186763"/>
              <joint name="{name}-joint4" range="-0.19198 3.927" class="size2"/>
              <geom mesh="link4"/>
              <body name="{name}-link5" pos="0.0775 -0.3425 0" quat="1 1 0 0">
                <inertial pos="-0.00032 0.01604 -0.026" quat="0.999311 -0.0304457 0.000577067 0.0212082" mass="1.3203"
                  diaginertia="0.00534729 0.00499076 0.0013489"/>
                <joint name="{name}-joint5" class="size2"/>
                <geom mesh="link5"/>
                <body name="{name}-link6" quat="1 1 0 0">
                  <inertial pos="0.06469 0.03278 0.02141" quat="-0.217672 0.772419 0.16258 0.574069" mass="1.325"
                    diaginertia="0.00245421 0.00221646 0.00107273"/>
                  <joint name="{name}-joint6" range="-1.69297 3.14159" class="size3"/>
                  <geom mesh="link6"/>
                  <body name="{name}-link7" pos="0.076 0.097 0" quat="1 -1 0 0">
                    <inertial pos="0 -0.00677 -0.01098" quat="0.487612 0.512088 -0.512088 0.487612" mass="0.17"
                      diaginertia="0.000132176 9.3e-05 5.85236e-05"/>
                    <joint name="{name}-joint7" class="size3"/>
                    <geom material="{name}-gray" mesh="end_tool"/>
                    <site name="attachment_site"/>
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

    _postamble = """
    <actuator>
      <general name="act1" joint="{name}-joint1" class="size1"/>
      <general name="act2" joint="{name}-joint2" class="size1" ctrlrange="-2.059 2.0944"/>
      <general name="act3" joint="{name}-joint3" class="size2"/>
      <general name="act4" joint="{name}-joint4" class="size2" ctrlrange="-0.19198 3.927"/>
      <general name="act5" joint="{name}-joint5" class="size2"/>
      <general name="act6" joint="{name}-joint6" class="size3" ctrlrange="-1.69297 3.14159"/>
      <general name="act7" joint="{name}-joint7" class="size3"/>
    </actuator>
    """

    def __init__(self, *_children, end_effector: Body = None, **rest):
        # Ge: we do the super call here to reduce boilerplate code.
        super().__init__(*_children, **rest)

        self._children = (*(self._children or []), end_effector)

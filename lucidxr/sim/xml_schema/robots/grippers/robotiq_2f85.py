from lucidxr.sim.xml_schema.schema import Body
from lucidxr.sim.xml_schema.transforms.mujoco import WXYZ, Vector3


class Robotiq2F85(Body):
    """
    This is the Gripper for the Ufactory Xarm7 robot.
    """

    assets: str = "robots/robotiq_2f85"
    mocap_quat = WXYZ(0, 0, 1, 0)

    pos = Vector3(0, 0, -0.002)
    classname = "2f85"

    _attributes = {
        "name": "base_mount",
        "pos": "0 0 -0.002",
    }

    _mocaps_raw = """
    <body mocap="true" name="{name}-mocap" pos="{mocap_pos}" quat="{mocap_quat}">
      <site name="{name}-mocap-site" size="0.002" type="sphere" rgba="0.13 0.3 0.2 1"/>
    </body>
    """

    # set the mass to 0.01 when used in the helicopter environment.
    gripper_mass = 0.777441

    # <option cone="elliptic" impratio="10"/>
    _preamble = """
    <asset>
      <material class="{classname}" name="{classname}-metal" rgba="0.58 0.58 0.58 1"/>
      <material class="{classname}" name="{classname}-silicone" rgba="0.1882 0.1882 0.1882 1"/>
      <material class="{classname}" name="{classname}-gray" rgba="0.4627 0.4627 0.4627 1"/>
      <material class="{classname}" name="{classname}-black" rgba="0.149 0.149 0.149 1"/>

      <mesh class="{classname}" file="{assets}/base_mount.stl"/>
      <mesh class="{classname}" file="{assets}/base.stl"/>
      <mesh class="{classname}" file="{assets}/driver.stl"/>
      <mesh class="{classname}" file="{assets}/coupler.stl"/>
      <mesh class="{classname}" file="{assets}/follower.stl"/>
      <mesh class="{classname}" file="{assets}/pad.stl"/>
      <mesh class="{classname}" file="{assets}/silicone_pad.stl"/>
      <mesh class="{classname}" file="{assets}/spring_link.stl"/>
    </asset>

    <default>
      <default class="{classname}">
        <mesh scale="0.001 0.001 0.001"/>
        <general biastype="affine"/>

        <joint axis="1 0 0"/>
        <default class="{classname}-driver">
          <joint range="0 0.8" armature="0.005" damping="0.1" solimplimit="0.95 0.99 0.001" solreflimit="0.005 1"/>
        </default>
        <default class="{classname}-follower">
          <joint range="-0.872664 0.872664" armature="0.001" pos="0 -0.018 0.0065" solimplimit="0.95 0.99 0.001" solreflimit="0.005 1"/>
        </default>
        <default class="{classname}-spring_link">
          <joint range="-0.29670597283 0.8" armature="0.001" stiffness="0.05" springref="2.62" damping="0.00125"/>
        </default>
        <default class="{classname}-coupler">
          <joint range="-1.57 0" armature="0.001" solimplimit="0.95 0.99 0.001" solreflimit="0.005 1"/>
        </default>

        <default class="{classname}-visual">
          <geom type="mesh" contype="0" conaffinity="0" group="0"/>
        </default>
        <default class="{classname}-collision">
          <geom type="mesh" group="3"/>
          <default class="{classname}-pad_box1">
            <geom mass="0" type="box" pos="0 -0.0026 0.028125" size="0.011 0.004 0.009375" friction="4"
              solimp="0.95 0.99 0.001" solref="0.004 1" priority="1" rgba="0.55 0.55 0.55 1"/>
          </default>
          <default class="{classname}-pad_box2">
            <geom mass="0" type="box" pos="0 -0.0026 0.009375" size="0.011 0.004 0.009375" friction="3"
              solimp="0.95 0.99 0.001" solref="0.004 1" priority="1" rgba="0.45 0.45 0.45 1"/>
          </default>
        </default>
      </default>
    </default>
    """

    wrist_mount = ""

    _children_raw = """
    <geom class="{classname}-visual" mesh="base_mount" material="{classname}-black"/>
    <geom class="{classname}-collision" mesh="base_mount"/>
    <body name="{name}-base" pos="0 0 0.0038" quat="1 0 0 0">
      <inertial mass="{gripper_mass}" pos="0 -2.70394e-05 0.0354675" quat="1 -0.00152849 0 0"
        diaginertia="0.000260285 0.000225381 0.000152708"/>
      <geom class="{classname}-visual" mesh="base" material="{classname}-black"/>
      <geom class="{classname}-collision" mesh="base"/>
      <site name="{name}-pinch" pos="0 0 0.145" type="sphere" rgba="0.9 0.0 0.0 1" size="0.002"/>
      {wrist_mount}
      <!-- Right-hand side 4-bar linkage -->
      <body name="{name}-right_driver" pos="0 0.0306011 0.054904">
        <inertial mass="0.00899563" pos="2.96931e-12 0.0177547 0.00107314" quat="0.681301 0.732003 0 0"
          diaginertia="1.72352e-06 1.60906e-06 3.22006e-07"/>
        <joint name="{name}-right_driver_joint" class="{classname}-driver"/>
        <geom class="{classname}-visual" mesh="driver" material="{classname}-gray"/>
        <geom class="{classname}-collision" mesh="driver"/>
        <body name="{name}-right_coupler" pos="0 0.0315 -0.0041">
          <inertial mass="0.0140974" pos="0 0.00301209 0.0232175" quat="0.705636 -0.0455904 0.0455904 0.705636"
            diaginertia="4.16206e-06 3.52216e-06 8.88131e-07"/>
          <joint name="{name}-right_coupler_joint" class="{classname}-coupler"/>
          <geom class="{classname}-visual" mesh="coupler" material="{classname}-black"/>
          <geom class="{classname}-collision" mesh="coupler"/>
        </body>
      </body>
      <body name="{name}-right_spring_link" pos="0 0.0132 0.0609">
        <inertial mass="0.0221642" pos="-8.65005e-09 0.0181624 0.0212658" quat="0.663403 -0.244737 0.244737 0.663403"
          diaginertia="8.96853e-06 6.71733e-06 2.63931e-06"/>
        <joint name="{name}-right_spring_link_joint" class="{classname}-spring_link"/>
        <geom class="{classname}-visual" mesh="spring_link" material="{classname}-black"/>
        <geom class="{classname}-collision" mesh="spring_link"/>
        <body name="{name}-right_follower" pos="0 0.055 0.0375">
          <inertial mass="0.0125222" pos="0 -0.011046 0.0124786" quat="1 0.1664 0 0"
            diaginertia="2.67415e-06 2.4559e-06 6.02031e-07"/>
          <joint name="{name}-right_follower_joint" class="{classname}-follower"/>
          <geom class="{classname}-visual" mesh="follower" material="{classname}-black"/>
          <geom class="{classname}-collision" mesh="follower"/>
          <body name="{name}-right_pad" pos="0 -0.0189 0.01352">
            <geom class="{classname}-pad_box1" name="{name}-right_pad1"/>
            <geom class="{classname}-pad_box2" name="{name}-right_pad2"/>
            <inertial mass="0.0035" pos="0 -0.0025 0.0185" quat="0.707107 0 0 0.707107"
              diaginertia="4.73958e-07 3.64583e-07 1.23958e-07"/>
            <geom class="{classname}-visual" mesh="pad"/>
            <body name="{name}-right_silicone_pad">
              <geom class="{classname}-visual" mesh="silicone_pad" material="{classname}-black"/>
            </body>
          </body>
        </body>
      </body>
      <!-- Left-hand side 4-bar linkage -->
      <body name="{name}-left_driver" pos="0 -0.0306011 0.054904" quat="0 0 0 1">
        <inertial mass="0.00899563" pos="0 0.0177547 0.00107314" quat="0.681301 0.732003 0 0"
          diaginertia="1.72352e-06 1.60906e-06 3.22006e-07"/>
        <joint name="{name}-left_driver_joint" class="{classname}-driver"/>
        <geom class="{classname}-visual" mesh="driver" material="{classname}-gray"/>
        <geom class="{classname}-collision" mesh="driver"/>
        <body name="{name}-left_coupler" pos="0 0.0315 -0.0041">
          <inertial mass="0.0140974" pos="0 0.00301209 0.0232175" quat="0.705636 -0.0455904 0.0455904 0.705636"
            diaginertia="4.16206e-06 3.52216e-06 8.88131e-07"/>
          <joint name="{name}-left_coupler_joint" class="{classname}-coupler"/>
          <geom class="{classname}-visual" mesh="coupler" material="{classname}-black"/>
          <geom class="{classname}-collision" mesh="coupler"/>
        </body>
      </body>
      <body name="{name}-left_spring_link" pos="0 -0.0132 0.0609" quat="0 0 0 1">
        <inertial mass="0.0221642" pos="-8.65005e-09 0.0181624 0.0212658" quat="0.663403 -0.244737 0.244737 0.663403"
          diaginertia="8.96853e-06 6.71733e-06 2.63931e-06"/>
        <joint name="{name}-left_spring_link_joint" class="{classname}-spring_link"/>
        <geom class="{classname}-visual" mesh="spring_link" material="{classname}-black"/>
        <geom class="{classname}-collision" mesh="spring_link"/>
        <body name="{name}-left_follower" pos="0 0.055 0.0375">
          <inertial mass="0.0125222" pos="0 -0.011046 0.0124786" quat="1 0.1664 0 0"
            diaginertia="2.67415e-06 2.4559e-06 6.02031e-07"/>
          <joint name="{name}-left_follower_joint" class="{classname}-follower"/>
          <geom class="{classname}-visual" mesh="follower" material="{classname}-black"/>
          <geom class="{classname}-collision" mesh="follower"/>
          <body name="{name}-left_pad" pos="0 -0.0189 0.01352">
            <geom class="{classname}-pad_box1" name="{name}-left_pad1"/>
            <geom class="{classname}-pad_box2" name="{name}-left_pad2"/>
            <inertial mass="0.0035" pos="0 -0.0025 0.0185" quat="1 0 0 1"
              diaginertia="4.73958e-07 3.64583e-07 1.23958e-07"/>
            <geom class="{classname}-visual" mesh="pad"/>
            <body name="{name}-left_silicone_pad">
              <geom class="{classname}-visual" mesh="silicone_pad" material="{classname}-black"/>
            </body>
          </body>
        </body>
      </body>
    </body> 
    """

    _postamble = """
    <contact>
      <exclude body1="{name}-base" body2="{name}-left_driver"/>
      <exclude body1="{name}-base" body2="{name}-right_driver"/>
      <exclude body1="{name}-base" body2="{name}-left_spring_link"/>
      <exclude body1="{name}-base" body2="{name}-right_spring_link"/>
      <exclude body1="{name}-right_coupler" body2="{name}-right_follower"/>
      <exclude body1="{name}-left_coupler" body2="{name}-left_follower"/>
    </contact>

    <!--
      This adds stability to the model by having a tendon that distributes the forces between both
      joints, such that the equality constraint doesn't have to do that much work in order to equalize
      both joints. Since both joints share the same sign, we split the force between both equally by
      setting coef=0.5
    -->
    <tendon>
      <fixed name="{name}-split">
        <joint joint="{name}-right_driver_joint" coef="0.5"/>
        <joint joint="{name}-left_driver_joint" coef="0.5"/>
      </fixed>
    </tendon>

    <equality>
      <connect anchor="0 0 0" body1="{name}-right_follower" body2="{name}-right_coupler" solimp="0.95 0.99 0.001" solref="0.005 1"/>
      <connect anchor="0 0 0" body1="{name}-left_follower" body2="{name}-left_coupler" solimp="0.95 0.99 0.001" solref="0.005 1"/>
      <joint joint1="{name}-right_driver_joint" joint2="{name}-left_driver_joint" polycoef="0 1 0 0 0" solimp="0.95 0.99 0.001"
        solref="0.005 1"/>
      <weld name="{name}-control" site1="{name}-mocap-site" site2="{name}-pinch" solref="0.003 1" solimp="0.9 0.95 0.001"/>
    </equality>

    <!--
      The general actuator below is a customized position actuator (with some damping) where
      gainprm[0] != kp (see http://mujoco.org/book/modeling.html#position).
      The reason why gainprm[0] != kp is because the control input range has to be re-scaled to
      [0, 255]. The joint range is currently set at [0, 0.8], the control range is [0, 255] and
      kp = 100. Tau = Kp * scale * control_input - Kp * error, max(Kp * scale * control_input) = 0.8,
      hence scale = 0.8 * 100 / 255
    -->
    <actuator>
      <general class="{classname}" name="{name}-fingers_actuator" tendon="{name}-split" forcerange="-5 5" ctrlrange="0 1"
        gainprm="80 0 0" biasprm="0 -100 -10"/>
    </actuator>
    """

    def __init__(self, *_children, mocap_pos=None, mocap_quat=None, **kwargs):
        super().__init__(*_children, **kwargs)
        if mocap_pos is None:
            self.mocap_pos = self._pos + [0, 0, -0.15]
        else:
            self.mocap_pos = mocap_pos

        if mocap_quat is not None:
            self.mocap_quat = WXYZ(*mocap_quat)

        values = self._format_dict()
        self._mocaps = self._mocaps_raw.format(**values)

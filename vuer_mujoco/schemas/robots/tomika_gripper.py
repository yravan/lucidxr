from ..schema import Body
from ..se3.se3_mujoco import WXYZ


class TomikaGripper(Body):
    assets = "tomika_gripper"
    mocap_quat = WXYZ(0, 0, 1, 0)
    classname = "tomika"

    _attributes = {
        "name": "tomika_gripper",
        "childclass": "tomika_gripper",
        "pos": "0 0 0.107",
        "quat": "0.9238795 0 0 -0.3826834",
    }

    # need to selectively show or hide the geoms in the render.
    _mocaps_raw = """
    <body mocap="true" name="{name}-mocap" pos="{mocap_pos}" quat="{mocap_quat}">
      <site name="{name}-mocap-site" size="0.002" type="sphere" rgba="0.13 0.3 0.2 1"/>
    </body>
    """

    def __init__(self, mode="render", mocap_pos=None, **kwargs):
        super().__init__(**kwargs)

        ### ge: we dynamically decide what to show visually. This is just
        ### an example
        if mode == "render":
            opacity = 0.0
        else:
            opacity = 0.9

        self.mocap_pos = mocap_pos or [0, 0, -0.15]
        print("mocap_pos", [mocap_pos])
        values = self._format_dict()
        self._mocaps = self._mocaps_raw.format(opacity=opacity, **values)

    _preamble = """
    <default>
        <default class="{childclass}">
          <material specular="0.5" shininess="0.25"/>
          <joint armature="0.1" damping="1" axis="0 0 1" range="-2.8973 2.8973"/>
          <general dyntype="none" biastype="affine" ctrlrange="-2.8973 2.8973" forcerange="-87 87"/>
          <default class="finger">
            <joint axis="0 1 0" type="slide" range="0 0.04"/>
          </default>

          <default class="{childclass}-visual">
            <geom type="mesh" contype="0" conaffinity="0" group="2"/>
          </default>
          <default class="{childclass}-collision">
            <geom type="mesh" group="3"/>
            <default class="fingertip_pad_collision_1">
              <geom type="box" size="0.0085 0.004 0.0085" pos="0 0.0055 0.0445"/>
            </default>
            <default class="fingertip_pad_collision_2">
              <geom type="box" size="0.003 0.002 0.003" pos="0.0055 0.002 0.05"/>
            </default>
            <default class="fingertip_pad_collision_3">
              <geom type="box" size="0.003 0.002 0.003" pos="-0.0055 0.002 0.05"/>
            </default>
            <default class="fingertip_pad_collision_4">
              <geom type="box" size="0.003 0.002 0.0035" pos="0.0055 0.002 0.0395"/>
            </default>
            <default class="fingertip_pad_collision_5">
              <geom type="box" size="0.003 0.002 0.0035" pos="-0.0055 0.002 0.0395"/>
            </default>
          </default>
        </default>
    </default>

    <asset>
        <material class="{childclass}" name="{classname}-white" rgba="1 1 1 1"/>
        <material class="{childclass}" name="{classname}-off_white" rgba="0.901961 0.921569 0.929412 1"/>
        <material class="{childclass}" name="{classname}-black" rgba="0.25 0.25 0.25 1"/>
        <material class="{childclass}" name="{classname}-green" rgba="0 1 0 1"/>
        <material class="{childclass}" name="{classname}-light_blue" rgba="0.039216 0.541176 0.780392 1"/>
    
        <!-- Hand collision mesh -->
        <mesh name="hand_c" file="{assets}/hand.stl"/>
        
        <!-- Hand visual mesh -->
        <mesh file="{assets}/hand_0.obj"/>
        <mesh file="{assets}/hand_1.obj"/>
        <mesh file="{assets}/hand_2.obj"/>
        <mesh file="{assets}/hand_3.obj"/>
        <mesh file="{assets}/hand_4.obj"/>
        <mesh file="{assets}/finger_0.obj"/>
        <mesh file="{assets}/finger_1.obj"/>
    </asset>
    """
    wrist_mount = ""
    _children_raw = """
    <inertial mass="0.73" pos="-0.01 0 0.03" diaginertia="0.001 0.0025 0.0017"/>
    <geom mesh="hand_0" material="{classname}-off_white" class="{childclass}-visual"/>
    <geom mesh="hand_1" material="{classname}-black" class="{childclass}-visual"/>
    <geom mesh="hand_2" material="{classname}-black" class="{childclass}-visual"/>
    <geom mesh="hand_3" material="{classname}-white" class="{childclass}-visual"/>
    <geom mesh="hand_4" material="{classname}-off_white" class="{childclass}-visual"/>
    <geom mesh="hand_c" class="{childclass}-collision"/>
    <site name="{name}-pinch" pos="0 0 0.11" type="sphere" rgba="0.9 0.0 0.0 1" size="0.002"/>
    {wrist_mount}
    <body name="{name}-left_finger" pos="0 0 0.0584">
        <inertial mass="0.015" pos="0 0 0" diaginertia="2.375e-6 2.375e-6 7.5e-7"/>
        <joint name="{name}-finger_joint1" class="finger"/>
        <geom mesh="finger_0" material="{classname}-off_white" class="{childclass}-visual"/>
        <geom mesh="finger_1" material="{classname}-black" class="{childclass}-visual"/>
        <geom mesh="finger_0" class="{childclass}-collision"/>
        <geom class="fingertip_pad_collision_1"/>
        <geom class="fingertip_pad_collision_2"/>
        <geom class="fingertip_pad_collision_3"/>
        <geom class="fingertip_pad_collision_4"/>
        <geom class="fingertip_pad_collision_5"/>
    </body>
    <body name="{name}-right_finger" pos="0 0 0.0584" quat="0 0 0 1">
        <inertial mass="0.015" pos="0 0 0" diaginertia="2.375e-6 2.375e-6 7.5e-7"/>
        <joint name="{name}-finger_joint2" class="finger"/>
        <geom mesh="finger_0" material="{classname}-off_white" class="{childclass}-visual"/>
        <geom mesh="finger_1" material="{classname}-black" class="{childclass}-visual"/>
        <geom mesh="finger_0" class="{childclass}-collision"/>
        <geom class="fingertip_pad_collision_1"/>
        <geom class="fingertip_pad_collision_2"/>
        <geom class="fingertip_pad_collision_3"/>
        <geom class="fingertip_pad_collision_4"/>
        <geom class="fingertip_pad_collision_5"/>
    </body>
    """

    ### The
    #
    # <!-- Remap original ctrlrange (0, 0.04) to (0, 255): 0.04 * 100 / 255 = 0.01568627451 -->
    # <general class="{childclass}" name="{name}-actuator8" tendon="{name}-split" forcerange="-100 100"
    # ctrlrange="0 255" gainprm="0.01568627451 0 0" biasprm="0 -100 -10"/>

    _postamble = """
    <tendon>
        <fixed name="{name}-split">
            <joint joint="{name}-finger_joint1" coef="0.5"/>
            <joint joint="{name}-finger_joint2" coef="0.5"/>
        </fixed>
    </tendon>

    <equality>
        <joint joint1="{name}-finger_joint1" joint2="{name}-finger_joint2" solimp="0.95 0.99 0.001" solref="0.005 1"/>
        <weld name="{name}-control" site1="{name}-mocap-site" site2="{name}-pinch"/>
    </equality>
    <actuator>
        <!-- Remap original ctrlrange (0, 0.04) to (0, 255): 0.04 * 100 / 255 = 0.01568627451 -->
        <general class="{childclass}" name="{name}-actuator8" tendon="{name}-split" forcerange="-100 100" 
                 ctrlrange="0 1" gainprm="4 0 0" biasprm="0 -100 -10"/>
    </actuator>
    """

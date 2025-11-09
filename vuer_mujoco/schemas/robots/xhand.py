from vuer_mujoco.schemas.schema import Body
from vuer_mujoco.schemas.utils.file import Prettify


class XHandLeft(Body):
    assets: str = "x_hand"
    forearm_body: bool = False
    show_mocap: bool = True
    site_alpha:float = 0.0
    classname="x_hand"
    default_pos = [0.00000000, 0.00000000, 0.20624829]

    _attributes = {
        "name": "left_hand_link",
        "pos": "0.00000000 0.00000000 0.20624829",
        "quat": "0.7071 0.7071 0 0",
        "childclass": "robot",
    }

    _mocaps_raw = """
        <body mocap="true" name="left-wrist" pos="{pos_wrist}" quat="1 0 0 0">
          <site name="left-wrist-mocap-site" rgba="0.658 0.411 0.75 {site_alpha}" size=".01"/>
        </body>
        
        <body mocap="true" name="left-index-finger-tip" pos="{pos_index}" quat="1 0 0 0">
          <site name="left-index-finger-tip-mocap-site" rgba="1 0 0 {site_alpha}" size=".01"/> <!-- Red -->
        </body>
        
        <body mocap="true" name="left-middle-finger-tip" pos="{pos_middle}" quat="1 0 0 0">
          <site name="left-middle-finger-tip-mocap-site" rgba="0 1 0 {site_alpha}" size=".01"/> <!-- Green -->
        </body>
        
        <body mocap="true" name="left-ring-finger-tip" pos="{pos_ring}" quat="1 0 0 0">
          <site name="left-ring-finger-tip-mocap-site" rgba="0 0 1 {site_alpha}" size=".01"/> <!-- Blue -->
        </body>
        
        <body mocap="true" name="left-pinky-finger-tip" pos="{pos_pinky}" quat="0 0 -1 0">
          <site name="left-pinky-finger-tip-mocap-site" rgba="1 1 0 {site_alpha}" size=".01"/> <!-- Yellow -->
        </body>
        
        <body mocap="true" name="left-thumb-tip" pos="{pos_thumb}" quat="0 1 0 0">
          <site name="left-thumb-tip-mocap-site" rgba="1 0.5 0 {site_alpha}" size=".01"/> <!-- Orange -->
        </body>
    """

    def __init__(self, *_children, **kwargs):
        super().__init__(*_children, **kwargs)

        self.pos_wrist = self._pos + [0.0, 0, 0.205] - self.default_pos
        self.pos_index = self._pos + [0.0275, 0.1725, 0.195] - self.default_pos
        self.pos_middle = self._pos + [0.0075, 0.1725, 0.195] - self.default_pos
        self.pos_ring = self._pos + [-0.0125, 0.1725, 0.195] - self.default_pos
        self.pos_pinky = self._pos + [-0.0325, 0.1725, 0.155] - self.default_pos
        self.pos_thumb = self._pos + [0.13, 0.03, 0.185] - self.default_pos
        if self.show_mocap:
            self.site_alpha = 1.0
        else:
            self.site_alpha = 0

        if self.forearm_body:
            raise NotImplementedError("forearm_body is not implemented yet.")

        values = self._format_dict()
        self._mocaps = self._mocaps_raw.format(**values)
        self._children_raw = self._children_raw.format(**values)

    _preamble = """
     <compiler angle="radian" meshdir="assets" texturedir="assets" autolimits="true"/>
      <default>
        <default class="robot">
          <default class="motor">
            <joint />
            <motor />
          </default>
          <default class="visual">
            <geom rgba="1 1 1 1" material="visualgeom" contype="0" conaffinity="0" group="2" />
          </default>
          <default class="collision">
            <geom rgba="1 1 1 1" material="collision_material" condim="3" contype="0" conaffinity="1" priority="1" group="1" solref="0.005 1" friction="1 0.01 0.01" />
            <equality solimp="0.99 0.999 1e-05" solref="0.005 1" />
          </default>
        </default>
      </default>
      <asset>
        <material name="RAL_9005_Jet_Black" rgba="0.055 0.055 0.063 1" />
        <material name="RAL_9003_Signal_White" rgba="0.941 0.941 0.941 1" />
        <material name="default_material" rgba="0.7 0.7 0.7 1" />
        <material name="collision_material" rgba="1.0 0.28 0.1 0.9" />
        <mesh name="left_hand_link.STL" file="xhand_left/left_hand_link.STL" />
        <mesh name="left_hand_ee_link.STL" file="xhand_left/left_hand_ee_link.STL" />
        <mesh name="left_hand_back_link.STL" file="xhand_left/left_hand_back_link.STL" />
        <mesh name="left_hand_thumb_bend_link.STL" file="xhand_left/left_hand_thumb_bend_link.STL" />
        <mesh name="left_hand_thumb_rota_link1.STL" file="xhand_left/left_hand_thumb_rota_link1.STL" />
        <mesh name="left_hand_thumb_rotaback_link1.STL" file="xhand_left/left_hand_thumb_rotaback_link1.STL" />
        <mesh name="left_hand_thumb_rota_link2.STL" file="xhand_left/left_hand_thumb_rota_link2.STL" />
        <mesh name="left_hand_thumb_rotaback_link2.STL" file="xhand_left/left_hand_thumb_rotaback_link2.STL" />
        <mesh name="left_hand_thumb_rota_tip.STL" file="xhand_left/left_hand_thumb_rota_tip.STL" />
        <mesh name="left_hand_index_bend_link.STL" file="xhand_left/left_hand_index_bend_link.STL" />
        <mesh name="left_hand_index_rota_link1.STL" file="xhand_left/left_hand_index_rota_link1.STL" />
        <mesh name="left_hand_index_rotaback_link1.STL" file="xhand_left/left_hand_index_rotaback_link1.STL" />
        <mesh name="left_hand_index_rota_link2.STL" file="xhand_left/left_hand_index_rota_link2.STL" />
        <mesh name="left_hand_index_rotaback_link2.STL" file="xhand_left/left_hand_index_rotaback_link2.STL" />
        <mesh name="left_hand_index_rota_tip.STL" file="xhand_left/left_hand_index_rota_tip.STL" />
        <mesh name="left_hand_mid_link1.STL" file="xhand_left/left_hand_mid_link1.STL" />
        <mesh name="left_hand_midback_link1.STL" file="xhand_left/left_hand_midback_link1.STL" />
        <mesh name="left_hand_mid_link2.STL" file="xhand_left/left_hand_mid_link2.STL" />
        <mesh name="left_hand_midback_link2.STL" file="xhand_left/left_hand_midback_link2.STL" />
        <mesh name="left_hand_mid_tip.STL" file="xhand_left/left_hand_mid_tip.STL" />
        <mesh name="left_hand_ring_link1.STL" file="xhand_left/left_hand_ring_link1.STL" />
        <mesh name="left_hand_ringback_link1.STL" file="xhand_left/left_hand_ringback_link1.STL" />
        <mesh name="left_hand_ring_link2.STL" file="xhand_left/left_hand_ring_link2.STL" />
        <mesh name="left_hand_ringback_link2.STL" file="xhand_left/left_hand_ringback_link2.STL" />
        <mesh name="left_hand_ring_tip.STL" file="xhand_left/left_hand_ring_tip.STL" />
        <mesh name="left_hand_pinky_link1.STL" file="xhand_left/left_hand_pinky_link1.STL" />
        <mesh name="left_hand_pinkyback_link1.STL" file="xhand_left/left_hand_pinkyback_link1.STL" />
        <mesh name="left_hand_pinky_link2.STL" file="xhand_left/left_hand_pinky_link2.STL" />
        <mesh name="left_hand_pinkyback_link2.STL" file="xhand_left/left_hand_pinkyback_link2.STL" />
        <mesh name="left_hand_pinky_tip.STL" file="xhand_left/left_hand_pinky_tip.STL" />
      </asset>
    """
    wrist_mount = ""
    forearm_xml = ""

    _children_raw = """
          <freejoint name="{name}-floating_base" />
          <geom rgba="1 1 1 1" name="left_hand_link_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_link.STL" class="collision" />
          <geom rgba="1 1 1 1" name="left_hand_link_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="left_hand_link.STL" class="visual" />
          <body name="left_hand_ee_link" pos="0 0 -0.065" quat="1.0 0.0 0.0 0.0">
            <inertial pos="-9.14235300816632E-20 6.87814821208628E-18 0" quat="1.0 0.0 0.0 0.0" mass="0.00000565" diaginertia="1e-11 1e-11 1e-11" />
            <geom rgba="1 1 1 1" name="left_hand_ee_link_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_ee_link.STL" class="collision" />
            <geom rgba="1 1 1 1" name="left_hand_ee_link_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="left_hand_ee_link.STL" class="visual" />
          </body>
          <body name="left_hand_back_link" pos="0 0 -0.065" quat="1.0 0.0 0.0 0.0">
            <inertial pos="-0.00206614328070064 0.0140092020913419 0.000644119291874204" quat="1.0 0.0 0.0 0.0" mass="0.00000020" diaginertia="1e-11 1e-11 1e-11" />
            <geom rgba="1 1 1 1" name="left_hand_back_link_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_back_link.STL" class="collision" />
            <geom rgba="1 1 1 1" name="left_hand_back_link_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9003_Signal_White" type="mesh" mesh="left_hand_back_link.STL" class="visual" />
          </body>
          <body name="left_hand_thumb_bend_link" pos="0.0228 -0.0095 -0.0305" quat="1.0 0.0 0.0 0.0">
            <joint name="left_hand_thumb_bend_joint" type="hinge" ref="0.0" class="motor" range="0 1.832" axis="0 0 -1" />
            <inertial pos="0.0144315029292586 0.00116653625408803 -6.50665966587562E-05" quat="1.0 0.0 0.0 0.0" mass="0.0118729" diaginertia="6.2e-07 1.6e-06 1.62e-06" />
            <geom rgba="1 1 1 1" name="left_hand_thumb_bend_link_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_thumb_bend_link.STL" class="collision" />
            <geom rgba="1 1 1 1" name="left_hand_thumb_bend_link_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="left_hand_thumb_bend_link.STL" class="visual" />
            <body name="left_hand_thumb_rota_link1" pos="0.028599 -0.0083177 0.00178" quat="0.991239538700108 -0.1304994696550749 0.0026560308583164923 -0.020174509595553045">
              <joint name="left_hand_thumb_rota_joint1" type="hinge" ref="0.0" class="motor" range="-0.698 1.745" axis="0 1 0" />
              <inertial pos="0.028699400584835 0.000353013004294657 -0.0013521057380018" quat="1.0 0.0 0.0 0.0" mass="0.13268494" diaginertia="1.702e-05 3.592e-05 4.285e-05" />
              <geom rgba="1 1 1 1" name="left_hand_thumb_rota_link1_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_thumb_rota_link1.STL" class="collision" />
              <geom rgba="1 1 1 1" name="left_hand_thumb_rota_link1_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="left_hand_thumb_rota_link1.STL" class="visual" />
              <body name="left_hand_thumb_rotaback_link1" pos="0.0553000000000004 0 0" quat="1.0 0.0 0.0 0.0">
                <inertial pos="-0.0296284435379629 -0.00145635345487384 0.00757347054072984" quat="1.0 0.0 0.0 0.0" mass="0.00000006" diaginertia="1e-11 1e-11 1e-11" />
                <geom rgba="1 1 1 1" name="left_hand_thumb_rotaback_link1_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_thumb_rotaback_link1.STL" class="collision" />
                <geom rgba="1 1 1 1" name="left_hand_thumb_rotaback_link1_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9003_Signal_White" type="mesh" mesh="left_hand_thumb_rotaback_link1.STL" class="visual" />
              </body>
              <body name="left_hand_thumb_rota_link2" pos="0.0553 0 0" quat="1.0 0.0 0.0 0.0">
                <joint name="left_hand_thumb_rota_joint2" type="hinge" ref="0.0" class="motor" range="0 1.745" axis="0 1 0" />
                <inertial pos="0.0228414266462457 0.000460794125797265 -0.000578251645405752" quat="1.0 0.0 0.0 0.0" mass="0.03536566" diaginertia="3.53e-06 7.85e-06 8.98e-06" />
                <geom rgba="1 1 1 1" name="left_hand_thumb_rota_link2_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_thumb_rota_link2.STL" class="collision" />
                <geom rgba="1 1 1 1" name="left_hand_thumb_rota_link2_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="left_hand_thumb_rota_link2.STL" class="visual" />
                <body name="left_hand_thumb_rotaback_link2" pos="0.0499881470979494 0 0" quat="1.0 0.0 0.0 0.0">
                  <inertial pos="-0.0256682291910944 0.000513274886833534 0.00926148645051527" quat="1.0 0.0 0.0 0.0" mass="0.00000004" diaginertia="1e-11 1e-11 1e-11" />
                  <geom rgba="1 1 1 1" name="left_hand_thumb_rotaback_link2_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_thumb_rotaback_link2.STL" class="collision" />
                  <geom rgba="1 1 1 1" name="left_hand_thumb_rotaback_link2_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9003_Signal_White" type="mesh" mesh="left_hand_thumb_rotaback_link2.STL" class="visual" />
                </body>
                <body name="left_hand_thumb_rota_tip" pos="0.0499881470979494 0 0" quat="1.0 0.0 0.0 0.0">
                  <inertial pos="-8.32667268468867E-17 1.04083408558608E-17 2.28983498828939E-16" quat="1.0 0.0 0.0 0.0" mass="0.00000565" diaginertia="1e-11 1e-11 1e-11" />
                  <geom rgba="1 1 1 1" name="left_hand_thumb_rota_tip_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_thumb_rota_tip.STL" class="collision" />
                  <geom rgba="1 1 1 1" name="left_hand_thumb_rota_tip_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="left_hand_thumb_rota_tip.STL" class="visual" />
                </body>
              </body>
            </body>
          </body>
          <body name="left_hand_index_bend_link" pos="0.0265 -0.0065 -0.0899" quat="1.0 0.0 0.0 0.0">
            <joint name="left_hand_index_bend_joint" type="hinge" ref="0.0" class="motor" range="-0.174 0.174" axis="0 -1 0" />
            <inertial pos="-0.000388464456994867 0.000992075604557427 -0.00970333167554097" quat="1.0 0.0 0.0 0.0" mass="0.06910833" diaginertia="1.74e-05 1.677e-05 3.45e-06" />
            <geom rgba="1 1 1 1" name="left_hand_index_bend_link_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="left_hand_index_bend_link.STL" class="visual" />
            <body name="left_hand_index_rota_link1" pos="0 0 -0.0178" quat="1.0 0.0 0.0 0.0">
              <joint name="left_hand_index_joint1" type="hinge" ref="0.0" class="motor" range="0 1.919" axis="-1 0 0" />
              <inertial pos="-3.58049083604185E-05 -0.00053041759210529 -0.0332784671157223" quat="1.0 0.0 0.0 0.0" mass="0.06298297" diaginertia="1.738e-05 1.686e-05 3.2e-06" />
              <geom rgba="1 1 1 1" name="left_hand_index_rota_link1_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_index_rota_link1.STL" class="collision" />
              <geom rgba="1 1 1 1" name="left_hand_index_rota_link1_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="left_hand_index_rota_link1.STL" class="visual" />
              <body name="left_hand_index_rotaback_link1" pos="0 0 -0.0558000000000001" quat="1.0 0.0 0.0 0.0">
                <inertial pos="0.00014803463945353 0.0115948039961551 0.0241234085631844" quat="1.0 0.0 0.0 0.0" mass="0.00000002" diaginertia="1e-11 1e-11 1e-11" />
                <geom rgba="1 1 1 1" name="left_hand_index_rotaback_link1_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_index_rotaback_link1.STL" class="collision" />
                <geom rgba="1 1 1 1" name="left_hand_index_rotaback_link1_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9003_Signal_White" type="mesh" mesh="left_hand_index_rotaback_link1.STL" class="visual" />
              </body>
              <body name="left_hand_index_rota_link2" pos="0 0 -0.0558" quat="1.0 0.0 0.0 0.0">
                <joint name="left_hand_index_joint2" type="hinge" ref="0.0" class="motor" range="0 1.919" axis="-1 0 0" />
                <inertial pos="0.000248361662016118 -0.00119905190206697 -0.0213789854478661" quat="1.0 0.0 0.0 0.0" mass="0.01588724" diaginertia="2.77e-06 2.83e-06 8.5e-07" />
                <geom rgba="1 1 1 1" name="left_hand_index_rota_link2_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_index_rota_link2.STL" class="collision" />
                <geom rgba="1 1 1 1" name="left_hand_index_rota_link2_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="left_hand_index_rota_link2.STL" class="visual" />
                <body name="left_hand_index_rotaback_link2" pos="0 0 -0.0422482924089404" quat="1.0 0.0 0.0 0.0">
                  <inertial pos="-0.000157950438605944 0.00758843721876324 0.017665521085575" quat="1.0 0.0 0.0 0.0" mass="0.00000001" diaginertia="1e-11 1e-11 1e-11" />
                  <geom rgba="1 1 1 1" name="left_hand_index_rotaback_link2_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_index_rotaback_link2.STL" class="collision" />
                  <geom rgba="1 1 1 1" name="left_hand_index_rotaback_link2_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9003_Signal_White" type="mesh" mesh="left_hand_index_rotaback_link2.STL" class="visual" />
                </body>
                <body name="left_hand_index_rota_tip" pos="0 0 -0.0422482924089404" quat="1.0 0.0 0.0 0.0">
                  <inertial pos="-1.00613961606655E-16 1.90819582357449E-17 0" quat="1.0 0.0 0.0 0.0" mass="0.00000565" diaginertia="1e-11 1e-11 1e-11" />
                  <geom rgba="1 1 1 1" name="left_hand_index_rota_tip_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_index_rota_tip.STL" class="collision" />
                  <geom rgba="1 1 1 1" name="left_hand_index_rota_tip_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="left_hand_index_rota_tip.STL" class="visual" />
                </body>
              </body>
            </body>
          </body>
          <body name="left_hand_mid_link1" pos="0.004 -0.0065 -0.1082" quat="1.0 0.0 0.0 0.0">
            <joint name="left_hand_mid_joint1" type="hinge" ref="0.0" class="motor" range="0 1.919" axis="-1 0 0" />
            <inertial pos="-3.58049083603916E-05 -0.000530417592105155 -0.0332784671157224" quat="1.0 0.0 0.0 0.0" mass="0.06298297" diaginertia="1.738e-05 1.686e-05 3.2e-06" />
            <geom rgba="1 1 1 1" name="left_hand_mid_link1_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_mid_link1.STL" class="collision" />
            <geom rgba="1 1 1 1" name="left_hand_mid_link1_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="left_hand_mid_link1.STL" class="visual" />
            <body name="left_hand_midback_link1" pos="0 0 -0.0558000000000001" quat="1.0 0.0 0.0 0.0">
              <inertial pos="0.000148034858018445 0.0115948038778314 0.024123407735519" quat="1.0 0.0 0.0 0.0" mass="0.00000002" diaginertia="1e-11 1e-11 1e-11" />
              <geom rgba="1 1 1 1" name="left_hand_midback_link1_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_midback_link1.STL" class="collision" />
              <geom rgba="1 1 1 1" name="left_hand_midback_link1_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9003_Signal_White" type="mesh" mesh="left_hand_midback_link1.STL" class="visual" />
            </body>
            <body name="left_hand_mid_link2" pos="0 0 -0.0558" quat="1.0 0.0 0.0 0.0">
              <joint name="left_hand_mid_joint2" type="hinge" ref="0.0" class="motor" range="0 1.919" axis="-1 0 0" />
              <inertial pos="0.000248361662016048 -0.00119905190206678 -0.0213789854478656" quat="1.0 0.0 0.0 0.0" mass="0.01588724" diaginertia="2.77e-06 2.83e-06 8.5e-07" />
              <geom rgba="1 1 1 1" name="left_hand_mid_link2_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_mid_link2.STL" class="collision" />
              <geom rgba="1 1 1 1" name="left_hand_mid_link2_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="left_hand_mid_link2.STL" class="visual" />
              <body name="left_hand_midback_link2" pos="0 0 -0.0422482924089403" quat="1.0 0.0 0.0 0.0">
                <inertial pos="-0.000157950438634382 0.00758843721877263 0.0176655210856587" quat="1.0 0.0 0.0 0.0" mass="0.00000001" diaginertia="1e-11 1e-11 1e-11" />
                <geom rgba="1 1 1 1" name="left_hand_midback_link2_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_midback_link2.STL" class="collision" />
                <geom rgba="1 1 1 1" name="left_hand_midback_link2_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9003_Signal_White" type="mesh" mesh="left_hand_midback_link2.STL" class="visual" />
              </body>
              <body name="left_hand_mid_tip" pos="0 0 -0.0422482924089403" quat="1.0 0.0 0.0 0.0">
                <inertial pos="-1.90819582357449E-17 1.55257751099924E-16 0" quat="1.0 0.0 0.0 0.0" mass="0.00000565" diaginertia="1e-11 1e-11 1e-11" />
                <geom rgba="1 1 1 1" name="left_hand_mid_tip_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_mid_tip.STL" class="collision" />
                <geom rgba="1 1 1 1" name="left_hand_mid_tip_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="left_hand_mid_tip.STL" class="visual" />
              </body>
            </body>
          </body>
          <body name="left_hand_ring_link1" pos="-0.016 -0.0065 -0.1052" quat="1.0 0.0 0.0 0.0">
            <joint name="left_hand_ring_joint1" type="hinge" ref="0.0" class="motor" range="0 1.919" axis="-1 0 0" />
            <inertial pos="-3.58049083603491E-05 -0.000530417592105894 -0.0332784671157224" quat="1.0 0.0 0.0 0.0" mass="0.06298297" diaginertia="1.738e-05 1.686e-05 3.2e-06" />
            <geom rgba="1 1 1 1" name="left_hand_ring_link1_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_ring_link1.STL" class="collision" />
            <geom rgba="1 1 1 1" name="left_hand_ring_link1_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="left_hand_ring_link1.STL" class="visual" />
            <body name="left_hand_ringback_link1" pos="0 0 -0.0558000000000001" quat="1.0 0.0 0.0 0.0">
              <inertial pos="0.000148033930314071 0.0115948038916307 0.0241234089720673" quat="1.0 0.0 0.0 0.0" mass="0.00000002" diaginertia="1e-11 1e-11 1e-11" />
              <geom rgba="1 1 1 1" name="left_hand_ringback_link1_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_ringback_link1.STL" class="collision" />
              <geom rgba="1 1 1 1" name="left_hand_ringback_link1_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9003_Signal_White" type="mesh" mesh="left_hand_ringback_link1.STL" class="visual" />
            </body>
            <body name="left_hand_ring_link2" pos="0 0 -0.0558" quat="1.0 0.0 0.0 0.0">
              <joint name="left_hand_ring_joint2" type="hinge" ref="0.0" class="motor" range="0 1.919" axis="-1 0 0" />
              <inertial pos="0.000248361662016028 -0.0011990519020675 -0.0213789854478657" quat="1.0 0.0 0.0 0.0" mass="0.01588724" diaginertia="2.77e-06 2.83e-06 8.5e-07" />
              <geom rgba="1 1 1 1" name="left_hand_ring_link2_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_ring_link2.STL" class="collision" />
              <geom rgba="1 1 1 1" name="left_hand_ring_link2_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="left_hand_ring_link2.STL" class="visual" />
              <body name="left_hand_ringback_link2" pos="0 0 -0.0422482924089404" quat="1.0 0.0 0.0 0.0">
                <inertial pos="-0.000157950438606443 0.00758843721877125 0.0176655210856417" quat="1.0 0.0 0.0 0.0" mass="0.00000001" diaginertia="1e-11 1e-11 1e-11" />
                <geom rgba="1 1 1 1" name="left_hand_ringback_link2_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_ringback_link2.STL" class="collision" />
                <geom rgba="1 1 1 1" name="left_hand_ringback_link2_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9003_Signal_White" type="mesh" mesh="left_hand_ringback_link2.STL" class="visual" />
              </body>
              <body name="left_hand_ring_tip" pos="0 0 -0.0422482924089404" quat="1.0 0.0 0.0 0.0">
                <inertial pos="-4.85722573273506E-17 -5.31692745386891E-16 0" quat="1.0 0.0 0.0 0.0" mass="0.00000565" diaginertia="1e-11 1e-11 1e-11" />
                <geom rgba="1 1 1 1" name="left_hand_ring_tip_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_ring_tip.STL" class="collision" />
                <geom rgba="1 1 1 1" name="left_hand_ring_tip_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="left_hand_ring_tip.STL" class="visual" />
              </body>
            </body>
          </body>
          <body name="left_hand_pinky_link1" pos="-0.036 -0.0065 -0.1022" quat="1.0 0.0 0.0 0.0">
            <joint name="left_hand_pinky_joint1" type="hinge" ref="0.0" class="motor" range="0 1.919" axis="-1 0 0" />
            <inertial pos="-3.58049083603318E-05 -0.000530417592106195 -0.0332784671157224" quat="1.0 0.0 0.0 0.0" mass="0.06298297" diaginertia="1.738e-05 1.686e-05 3.2e-06" />
            <geom rgba="1 1 1 1" name="left_hand_pinky_link1_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_pinky_link1.STL" class="collision" />
            <geom rgba="1 1 1 1" name="left_hand_pinky_link1_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="left_hand_pinky_link1.STL" class="visual" />
            <body name="left_hand_pinkyback_link1" pos="0 0 -0.0558000000000001" quat="1.0 0.0 0.0 0.0">
              <inertial pos="0.000148034877008783 0.0115948040346325 0.024123408080182" quat="1.0 0.0 0.0 0.0" mass="0.00000002" diaginertia="1e-11 1e-11 1e-11" />
              <geom rgba="1 1 1 1" name="left_hand_pinkyback_link1_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_pinkyback_link1.STL" class="collision" />
              <geom rgba="1 1 1 1" name="left_hand_pinkyback_link1_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9003_Signal_White" type="mesh" mesh="left_hand_pinkyback_link1.STL" class="visual" />
            </body>
            <body name="left_hand_pinky_link2" pos="0 0 -0.0558" quat="1.0 0.0 0.0 0.0">
              <joint name="left_hand_pinky_joint2" type="hinge" ref="0.0" class="motor" range="1.0 1.919" axis="-1 0 0" />
              <inertial pos="0.000248361696242753 -0.00119905185762272 -0.0213789857007834" quat="1.0 0.0 0.0 0.0" mass="0.01588724" diaginertia="2.77e-06 2.83e-06 8.5e-07" />
              <geom rgba="1 1 1 1" name="left_hand_pinky_link2_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_pinky_link2.STL" class="collision" />
              <geom rgba="1 1 1 1" name="left_hand_pinky_link2_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="left_hand_pinky_link2.STL" class="visual" />
              <body name="left_hand_pinkyback_link2" pos="0 0 -0.0422482924089405" quat="1.0 0.0 0.0 0.0">
                <inertial pos="-0.0001579504385983 0.00758843721876557 0.0176655210856048" quat="1.0 0.0 0.0 0.0" mass="0.00000001" diaginertia="1e-11 1e-11 1e-11" />
                <geom rgba="1 1 1 1" name="left_hand_pinkyback_link2_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_pinkyback_link2.STL" class="collision" />
                <geom rgba="1 1 1 1" name="left_hand_pinkyback_link2_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9003_Signal_White" type="mesh" mesh="left_hand_pinkyback_link2.STL" class="visual" />
              </body>
              <body name="left_hand_pinky_tip" pos="0 0 -0.0422482924089405" quat="1.0 0.0 0.0 0.0">
                <inertial pos="1.38777878078145E-17 -8.84708972748172E-16 2.77555756156289E-17" quat="1.0 0.0 0.0 0.0" mass="0.00000565" diaginertia="1e-11 1e-11 1e-11" />
                <geom rgba="1 1 1 1" name="left_hand_pinky_tip_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="left_hand_pinky_tip.STL" class="collision" />
                <geom rgba="1 1 1 1" name="left_hand_pinky_tip_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="left_hand_pinky_tip.STL" class="visual" />
              </body>
            </body>
          </body>
          <site name="left_hand_link_site" pos="0 0 0" quat="1 0 0 0" rgba="0.8 0.8 0.8 {site_alpha}"/>
        """

    _postamble = """
      <actuator>
        <motor name="left_hand_thumb_bend_joint_ctrl" joint="left_hand_thumb_bend_joint" class="motor" />
        <motor name="left_hand_thumb_rota_joint1_ctrl" joint="left_hand_thumb_rota_joint1" class="motor" />
        <motor name="left_hand_thumb_rota_joint2_ctrl" joint="left_hand_thumb_rota_joint2" class="motor" />
        <motor name="left_hand_index_bend_joint_ctrl" joint="left_hand_index_bend_joint" class="motor" />
        <motor name="left_hand_index_joint1_ctrl" joint="left_hand_index_joint1" class="motor" />
        <motor name="left_hand_index_joint2_ctrl" joint="left_hand_index_joint2" class="motor" />
        <motor name="left_hand_mid_joint1_ctrl" joint="left_hand_mid_joint1" class="motor" />
        <motor name="left_hand_mid_joint2_ctrl" joint="left_hand_mid_joint2" class="motor" />
        <motor name="left_hand_ring_joint1_ctrl" joint="left_hand_ring_joint1" class="motor" />
        <motor name="left_hand_ring_joint2_ctrl" joint="left_hand_ring_joint2" class="motor" />
        <motor name="left_hand_pinky_joint1_ctrl" joint="left_hand_pinky_joint1" class="motor" />
        <motor name="left_hand_pinky_joint2_ctrl" joint="left_hand_pinky_joint2" class="motor" />
      </actuator>
      <contact>
        <exclude body1="{name}" body2="left_hand_ee_link" />
        <exclude body1="{name}" body2="left_hand_back_link" />
        <exclude body1="{name}" body2="left_hand_thumb_bend_link" />
        <exclude body1="left_hand_thumb_bend_link" body2="left_hand_thumb_rota_link1" />
        <exclude body1="left_hand_thumb_rota_link1" body2="left_hand_thumb_rotaback_link1" />
        <exclude body1="left_hand_thumb_rota_link1" body2="left_hand_thumb_rota_link2" />
        <exclude body1="left_hand_thumb_rota_link2" body2="left_hand_thumb_rotaback_link2" />
        <exclude body1="left_hand_thumb_rota_link2" body2="left_hand_thumb_rota_tip" />
        <exclude body1="left_hand_index_rota_link1" body2="left_hand_index_rotaback_link1" />
        <exclude body1="left_hand_index_rota_link1" body2="left_hand_index_rota_link2" />
        <exclude body1="left_hand_index_rota_link2" body2="left_hand_index_rotaback_link2" />
        <exclude body1="left_hand_index_rota_link2" body2="left_hand_index_rota_tip" />
        <exclude body1="{name}" body2="left_hand_mid_link1" />
        <exclude body1="left_hand_mid_link1" body2="left_hand_midback_link1" />
        <exclude body1="left_hand_mid_link1" body2="left_hand_mid_link2" />
        <exclude body1="left_hand_mid_link2" body2="left_hand_midback_link2" />
        <exclude body1="left_hand_mid_link2" body2="left_hand_mid_tip" />
        <exclude body1="{name}" body2="left_hand_ring_link1" />
        <exclude body1="left_hand_ring_link1" body2="left_hand_ringback_link1" />
        <exclude body1="left_hand_ring_link1" body2="left_hand_ring_link2" />
        <exclude body1="left_hand_ring_link2" body2="left_hand_ringback_link2" />
        <exclude body1="left_hand_ring_link2" body2="left_hand_ring_tip" />
        <exclude body1="{name}" body2="left_hand_pinky_link1" />
        <exclude body1="left_hand_pinky_link1" body2="left_hand_pinkyback_link1" />
        <exclude body1="left_hand_pinky_link1" body2="left_hand_pinky_link2" />
        <exclude body1="left_hand_pinky_link2" body2="left_hand_pinkyback_link2" />
        <exclude body1="left_hand_pinky_link2" body2="left_hand_pinky_tip" />
      </contact>
      <equality>
        <weld body1="{name}" body2="left-wrist"/>
        <weld body1="left_hand_index_rota_tip" body2="left-index-finger-tip"/>
        <weld body1="left_hand_mid_tip" body2="left-middle-finger-tip"/>
        <weld body1="left_hand_ring_tip" body2="left-ring-finger-tip"/>
        <weld body1="left_hand_pinky_tip" body2="left-pinky-finger-tip"/>
        <weld body1="left_hand_thumb_rota_tip" body2="left-thumb-tip"/>
      </equality>
      <sensor>
        <framepos name="left_hand_link_site_pos" objtype="site" objname="left_hand_link_site" />
        <framequat name="left_hand_link_site_quat" objtype="site" objname="left_hand_link_site" />
        <framelinvel name="left_hand_link_site_linvel" objtype="site" objname="left_hand_link_site" />
        <frameangvel name="left_hand_link_site_angvel" objtype="site" objname="left_hand_link_site" />
        <velocimeter name="left_hand_link_site_vel" site="left_hand_link_site" />
      </sensor>
    """



class XHandRight(Body):
    assets: str = "x_hand"
    forearm_body: bool = False
    show_mocap: bool = False
    site_alpha: float = 0.0
    classname="x_hand"
    default_pos = [0.00000000, 0.00000000, 0.20624829]

    _attributes = {
        "name": "right_hand_link",
        "pos": "0.00000000 0.00000000 0.20624829",
        "quat": "0.7071 0.7071 0 0",
        "childclass": "robot",
    }

    _mocaps_raw = """
        <body mocap="true" name="right-wrist" pos="{pos_wrist}" quat="0 0 1 0">
            <site name="right-wrist-mocap-site" rgba="0.658 0.411 0.75 {site_alpha}" size=".01"/>
        </body>

        <body mocap="true" name="right-index-finger-tip" pos="{pos_index}" quat="0 0 1 0">
            <site name="right-index-finger-tip-mocap-site" rgba="1 0 0 {site_alpha}" size=".01"/> <!-- Red -->
        </body>

        <body mocap="true" name="right-middle-finger-tip" pos="{pos_middle}" quat="0 0 1 0">
            <site name="right-middle-finger-tip-mocap-site" rgba="0 1 0 {site_alpha}" size=".01"/> <!-- Green -->
        </body>

        <body mocap="true" name="right-ring-finger-tip" pos="{pos_ring}" quat="0 0 1 0">
            <site name="right-ring-finger-tip-mocap-site" rgba="0 0 1 {site_alpha}" size=".01"/> <!-- Blue -->
        </body>

        <body mocap="true" name="right-pinky-finger-tip" pos="{pos_pinky}" quat="0 0 1 0">
            <site name="right-pinky-finger-tip-mocap-site" rgba="1 1 0 {site_alpha}" size=".01"/> <!-- Yellow -->
        </body>

        <body mocap="true" name="right-thumb-tip" pos="{pos_thumb}" quat="0 0 1 0">
            <site name="right-thumb-tip-mocap-site" rgba="1 0.5 0 {site_alpha}" size=".01"/> <!-- Orange -->
        </body>
    """

    def __init__(self, *_children, **kwargs):
        super().__init__(*_children, **kwargs)

        self.pos_wrist = self._pos + [0.0, 0, 0.205] - self.default_pos
        self.pos_index = self._pos + [0.0275, 0.1725, 0.215] - self.default_pos
        self.pos_middle = self._pos + [0.0075, 0.1725, 0.215] - self.default_pos
        self.pos_ring = self._pos + [-0.0125, 0.1725, 0.215] - self.default_pos
        self.pos_pinky = self._pos + [-0.0325, 0.1725, 0.215] - self.default_pos
        self.pos_thumb = self._pos + [0.13, 0.03, 0.225] - self.default_pos
        if self.show_mocap:
            self.site_alpha = 1.0
        else:
            self.site_alpha = 0

        if self.forearm_body:
            raise NotImplementedError("forearm_body is not implemented yet.")

        values = self._format_dict()
        self._mocaps = self._mocaps_raw.format(**values)
        self._children_raw = self._children_raw.format(**values)

    _preamble = """
      <compiler angle="radian" meshdir="assets" texturedir="assets" autolimits="true"/>
      <default>
        <default class="robot">
          <default class="motor">
            <joint />
            <motor />
          </default>
          <default class="visual">
            <geom rgba="1 1 1 1" material="visualgeom" contype="0" conaffinity="0" group="2" />
          </default>
          <default class="collision">
            <geom rgba="1 1 1 1" material="collision_material" condim="3" contype="0" conaffinity="1" priority="1" group="1" solref="0.005 1" friction="1 0.01 0.01" />
            <equality solimp="0.99 0.999 1e-05" solref="0.005 1" />
          </default>
        </default>
      </default>
      <asset>
        <material name="RAL_9005_Jet_Black" rgba="0.055 0.055 0.063 1" />
        <material name="RAL_9003_Signal_White" rgba="0.941 0.941 0.941 1" />
        <material name="default_material" rgba="0.7 0.7 0.7 1" />
        <material name="collision_material" rgba="1.0 0.28 0.1 0.9" />
        <mesh name="right_hand_link.STL" file="xhand_right/right_hand_link.STL" />
        <mesh name="right_hand_ee_link.STL" file="xhand_right/right_hand_ee_link.STL" />
        <mesh name="right_hand_back_link.STL" file="xhand_right/right_hand_back_link.STL" />
        <mesh name="right_hand_thumb_bend_link.STL" file="xhand_right/right_hand_thumb_bend_link.STL" />
        <mesh name="right_hand_thumb_rota_link1.STL" file="xhand_right/right_hand_thumb_rota_link1.STL" />
        <mesh name="right_hand_thumb_rotaback_link1.STL" file="xhand_right/right_hand_thumb_rotaback_link1.STL" />
        <mesh name="right_hand_thumb_rota_link2.STL" file="xhand_right/right_hand_thumb_rota_link2.STL" />
        <mesh name="right_hand_thumb_rotaback_link2.STL" file="xhand_right/right_hand_thumb_rotaback_link2.STL" />
        <mesh name="right_hand_thumb_rota_tip.STL" file="xhand_right/right_hand_thumb_rota_tip.STL" />
        <mesh name="right_hand_index_bend_link.STL" file="xhand_right/right_hand_index_bend_link.STL" />
        <mesh name="right_hand_index_rota_link1.STL" file="xhand_right/right_hand_index_rota_link1.STL" />
        <mesh name="right_hand_index_rotaback_link1.STL" file="xhand_right/right_hand_index_rotaback_link1.STL" />
        <mesh name="right_hand_index_rota_link2.STL" file="xhand_right/right_hand_index_rota_link2.STL" />
        <mesh name="right_hand_index_rotaback_link2.STL" file="xhand_right/right_hand_index_rotaback_link2.STL" />
        <mesh name="right_hand_index_rota_tip.STL" file="xhand_right/right_hand_index_rota_tip.STL" />
        <mesh name="right_hand_mid_link1.STL" file="xhand_right/right_hand_mid_link1.STL" />
        <mesh name="right_hand_midback_link1.STL" file="xhand_right/right_hand_midback_link1.STL" />
        <mesh name="right_hand_mid_link2.STL" file="xhand_right/right_hand_mid_link2.STL" />
        <mesh name="right_hand_midback_link2.STL" file="xhand_right/right_hand_midback_link2.STL" />
        <mesh name="right_hand_mid_tip.STL" file="xhand_right/right_hand_mid_tip.STL" />
        <mesh name="right_hand_ring_link1.STL" file="xhand_right/right_hand_ring_link1.STL" />
        <mesh name="right_hand_ringback_link1.STL" file="xhand_right/right_hand_ringback_link1.STL" />
        <mesh name="right_hand_ring_link2.STL" file="xhand_right/right_hand_ring_link2.STL" />
        <mesh name="right_hand_ringback_link2.STL" file="xhand_right/right_hand_ringback_link2.STL" />
        <mesh name="right_hand_ring_tip.STL" file="xhand_right/right_hand_ring_tip.STL" />
        <mesh name="right_hand_pinky_link1.STL" file="xhand_right/right_hand_pinky_link1.STL" />
        <mesh name="right_hand_pinkyback_link1.STL" file="xhand_right/right_hand_pinkyback_link1.STL" />
        <mesh name="right_hand_pinky_link2.STL" file="xhand_right/right_hand_pinky_link2.STL" />
        <mesh name="right_hand_pinkyback_link2.STL" file="xhand_right/right_hand_pinkyback_link2.STL" />
        <mesh name="right_hand_pinky_tip.STL" file="xhand_right/right_hand_pinky_tip.STL" />
      </asset>
    """
    wrist_mount = ""
    forearm_xml = ""

    _children_raw = """
          <freejoint name="{name}-floating_base" />
          <geom rgba="1 1 1 1" name="right_hand_link_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_link.STL" class="collision" />
          <geom rgba="1 1 1 1" name="right_hand_link_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="right_hand_link.STL" class="visual" />
          <body name="right_hand_ee_link" pos="0 0 -0.065" quat="1.0 0.0 0.0 0.0">
            <inertial pos="2.48510213245214E-19 -8.08284973285247E-18 0" quat="1.0 0.0 0.0 0.0" mass="0.00000565" diaginertia="1e-11 1e-11 1e-11" />
            <geom rgba="1 1 1 1" name="right_hand_ee_link_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_ee_link.STL" class="collision" />
            <geom rgba="1 1 1 1" name="right_hand_ee_link_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="right_hand_ee_link.STL" class="visual" />
          </body>
          <body name="right_hand_back_link" pos="0 0 -0.065" quat="1.0 0.0 0.0 0.0">
            <inertial pos="-0.00149243508011096 -0.0140081556490721 0.000647100828228067" quat="1.0 0.0 0.0 0.0" mass="0.00000020" diaginertia="1e-11 1e-11 1e-11" />
            <geom rgba="1 1 1 1" name="right_hand_back_link_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_back_link.STL" class="collision" />
            <geom rgba="1 1 1 1" name="right_hand_back_link_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9003_Signal_White" type="mesh" mesh="right_hand_back_link.STL" class="visual" />
          </body>
          <body name="right_hand_thumb_bend_link" pos="0.0228 0.0095 -0.0305" quat="1.0 0.0 0.0 0.0">
            <joint name="right_hand_thumb_bend_joint" type="hinge" ref="0.0" class="motor" range="0 1.832" axis="0 0 1" />
            <inertial pos="0.0144358799903648 -0.00116534489100676 -5.40665183231849E-05" quat="1.0 0.0 0.0 0.0" mass="0.01174632" diaginertia="6.2e-07 1.6e-06 1.62e-06" />
            <geom rgba="1 1 1 1" name="right_hand_thumb_bend_link_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_thumb_bend_link.STL" class="collision" />
            <geom rgba="1 1 1 1" name="right_hand_thumb_bend_link_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="right_hand_thumb_bend_link.STL" class="visual" />
            <body name="right_hand_thumb_rota_link1" pos="0.028599 0.0083177 0.00178" quat="0.991239538700108 0.1304994696550749 0.0026560308583164923 0.020174509595553045">
              <joint name="right_hand_thumb_rota_joint1" type="hinge" ref="0.0" class="motor" range="-0.698 1.745" axis="0 1 0" />
              <inertial pos="0.0287681482733488 -0.00036176529547633 -0.00133929681686046" quat="1.0 0.0 0.0 0.0" mass="0.13266642" diaginertia="1.699e-05 3.679e-05 4.374e-05" />
              <geom rgba="1 1 1 1" name="right_hand_thumb_rota_link1_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_thumb_rota_link1.STL" class="collision" />
              <geom rgba="1 1 1 1" name="right_hand_thumb_rota_link1_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="right_hand_thumb_rota_link1.STL" class="visual" />
              <body name="right_hand_thumb_rotaback_link1" pos="0.0553000000000007 0 0" quat="1.0 0.0 0.0 0.0">
                <inertial pos="-0.0296289408411864 0.0014334239435258 0.00759117850867843" quat="1.0 0.0 0.0 0.0" mass="0.00000006" diaginertia="1e-11 1e-11 1e-11" />
                <geom rgba="1 1 1 1" name="right_hand_thumb_rotaback_link1_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_thumb_rotaback_link1.STL" class="collision" />
                <geom rgba="1 1 1 1" name="right_hand_thumb_rotaback_link1_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9003_Signal_White" type="mesh" mesh="right_hand_thumb_rotaback_link1.STL" class="visual" />
              </body>
              <body name="right_hand_thumb_rota_link2" pos="0.0553 0 0" quat="1.0 0.0 0.0 0.0">
                <joint name="right_hand_thumb_rota_joint2" type="hinge" ref="0.0" class="motor" range="0 1.745" axis="0 1 0" />
                <inertial pos="0.0225340009927979 -0.000881600697645881 -0.000614548321208525" quat="1.0 0.0 0.0 0.0" mass="0.04336091" diaginertia="3.88e-06 9.02e-06 1.046e-05" />
                <geom rgba="1 1 1 1" name="right_hand_thumb_rota_link2_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_thumb_rota_link2.STL" class="collision" />
                <geom rgba="1 1 1 1" name="right_hand_thumb_rota_link2_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="right_hand_thumb_rota_link2.STL" class="visual" />
                <body name="right_hand_thumb_rotaback_link2" pos="0.0502276499414862 0 0" quat="1.0 0.0 0.0 0.0">
                  <inertial pos="-0.0258393463672562 -0.000532639688528967 0.00924631171368789" quat="1.0 0.0 0.0 0.0" mass="0.00000004" diaginertia="1e-11 1e-11 1e-11" />
                  <geom rgba="1 1 1 1" name="right_hand_thumb_rotaback_link2_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_thumb_rotaback_link2.STL" class="collision" />
                  <geom rgba="1 1 1 1" name="right_hand_thumb_rotaback_link2_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9003_Signal_White" type="mesh" mesh="right_hand_thumb_rotaback_link2.STL" class="visual" />
                </body>
                <body name="right_hand_thumb_rota_tip" pos="0.0502276499414862 0 0" quat="1.0 0.0 0.0 0.0">
                  <inertial pos="8.32667268468867E-17 -8.67361737988404E-19 -5.55111512312578E-17" quat="1.0 0.0 0.0 0.0" mass="0.00000565" diaginertia="1e-11 1e-11 1e-11" />
                  <geom rgba="1 1 1 1" name="right_hand_thumb_rota_tip_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_thumb_rota_tip.STL" class="collision" />
                  <geom rgba="1 1 1 1" name="right_hand_thumb_rota_tip_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="right_hand_thumb_rota_tip.STL" class="visual" />
                </body>
              </body>
            </body>
          </body>
          <body name="right_hand_index_bend_link" pos="0.0265 0.0065 -0.0899" quat="1.0 0.0 0.0 0.0">
            <joint name="right_hand_index_bend_joint" type="hinge" ref="0.0" class="motor" range="-0.174 0.174" axis="0 -1 0" />
            <inertial pos="0.000118997558760787 -0.000715851164577269 -0.0111903014853532" quat="1.0 0.0 0.0 0.0" mass="0.06910833" diaginertia="1.74e-05 1.677e-05 3.45e-06" />
            <geom rgba="1 1 1 1" name="right_hand_index_bend_link_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_index_bend_link.STL" class="collision" />
            <geom rgba="1 1 1 1" name="right_hand_index_bend_link_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="right_hand_index_bend_link.STL" class="visual" />
            <body name="right_hand_index_rota_link1" pos="0 0 -0.0178" quat="1.0 0.0 0.0 0.0">
              <joint name="right_hand_index_joint1" type="hinge" ref="0.0" class="motor" range="0 1.919" axis="1 0 0" />
              <inertial pos="0.000133008106573459 0.000632930512954057 -0.0355868719939061" quat="1.0 0.0 0.0 0.0" mass="0.06298297" diaginertia="1.738e-05 1.686e-05 3.2e-06" />
              <geom rgba="1 1 1 1" name="right_hand_index_rota_link1_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_index_rota_link1.STL" class="collision" />
              <geom rgba="1 1 1 1" name="right_hand_index_rota_link1_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="right_hand_index_rota_link1.STL" class="visual" />
              <body name="right_hand_index_rotaback_link1" pos="0 0 -0.0557999999999955" quat="1.0 0.0 0.0 0.0">
                <inertial pos="-0.000148035114615745 -0.0115948040516035 0.0241234077593065" quat="1.0 0.0 0.0 0.0" mass="0.00000002" diaginertia="1e-11 1e-11 1e-11" />
                <geom rgba="1 1 1 1" name="right_hand_index_rotaback_link1_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_index_rotaback_link1.STL" class="collision" />
                <geom rgba="1 1 1 1" name="right_hand_index_rotaback_link1_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9003_Signal_White" type="mesh" mesh="right_hand_index_rotaback_link1.STL" class="visual" />
              </body>
              <body name="right_hand_index_rota_link2" pos="0 0 -0.0558" quat="1.0 0.0 0.0 0.0">
                <joint name="right_hand_index_joint2" type="hinge" ref="0.0" class="motor" range="0 1.919" axis="1 0 0" />
                <inertial pos="-0.000248361661985549 0.00119905190206764 -0.0213789854478675" quat="1.0 0.0 0.0 0.0" mass="0.01588724" diaginertia="2.77e-06 2.83e-06 8.5e-07" />
                <geom rgba="1 1 1 1" name="right_hand_index_rota_link2_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_index_rota_link2.STL" class="collision" />
                <geom rgba="1 1 1 1" name="right_hand_index_rota_link2_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="right_hand_index_rota_link2.STL" class="visual" />
                <body name="right_hand_index_rotaback_link2" pos="0 0 -0.0422482924089416" quat="1.0 0.0 0.0 0.0">
                  <inertial pos="0.00015795043863779 -0.00758843721876498 0.017665521085611" quat="1.0 0.0 0.0 0.0" mass="0.00000001" diaginertia="1e-11 1e-11 1e-11" />
                  <geom rgba="1 1 1 1" name="right_hand_index_rotaback_link2_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_index_rotaback_link2.STL" class="collision" />
                  <geom rgba="1 1 1 1" name="right_hand_index_rotaback_link2_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9003_Signal_White" type="mesh" mesh="right_hand_index_rotaback_link2.STL" class="visual" />
                </body>
                <body name="right_hand_index_rota_tip" pos="0 0 -0.0422482924089416" quat="1.0 0.0 0.0 0.0">
                  <inertial pos="3.70675712346724E-14 8.65627014512427E-16 -8.32667268468867E-16" quat="1.0 0.0 0.0 0.0" mass="0.00000565" diaginertia="1e-11 1e-11 1e-11" />
                  <geom rgba="1 1 1 1" name="right_hand_index_rota_tip_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_index_rota_tip.STL" class="collision" />
                  <geom rgba="1 1 1 1" name="right_hand_index_rota_tip_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="right_hand_index_rota_tip.STL" class="visual" />
                </body>
              </body>
            </body>
          </body>
          <body name="right_hand_mid_link1" pos="0.004 0.0065 -0.1082" quat="1.0 0.0 0.0 0.0">
            <joint name="right_hand_mid_joint1" type="hinge" ref="0.0" class="motor" range="0 1.919" axis="1 0 0" />
            <inertial pos="3.58049083993136E-05 0.000530417592106078 -0.0332784671157236" quat="1.0 0.0 0.0 0.0" mass="0.06298297" diaginertia="1.738e-05 1.686e-05 3.2e-06" />
            <geom rgba="1 1 1 1" name="right_hand_mid_link1_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_mid_link1.STL" class="collision" />
            <geom rgba="1 1 1 1" name="right_hand_mid_link1_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="right_hand_mid_link1.STL" class="visual" />
            <body name="right_hand_midback_link1" pos="0 0 -0.0558" quat="1.0 0.0 0.0 0.0">
              <inertial pos="-0.000148035028410428 -0.0115948040189855 0.0241234086343709" quat="1.0 0.0 0.0 0.0" mass="0.00000002" diaginertia="1e-11 1e-11 1e-11" />
              <geom rgba="1 1 1 1" name="right_hand_midback_link1_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_midback_link1.STL" class="collision" />
              <geom rgba="1 1 1 1" name="right_hand_midback_link1_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9003_Signal_White" type="mesh" mesh="right_hand_midback_link1.STL" class="visual" />
            </body>
            <body name="right_hand_mid_link2" pos="0 0 -0.0558" quat="1.0 0.0 0.0 0.0">
              <joint name="right_hand_mid_joint2" type="hinge" ref="0.0" class="motor" range="0 1.919" axis="1 0 0" />
              <inertial pos="-0.000248364601983051 0.00119905076177324 -0.0213789908421273" quat="1.0 0.0 0.0 0.0" mass="0.01624108" diaginertia="2.81e-06 2.87e-06 8.6e-07" />
              <geom rgba="1 1 1 1" name="right_hand_mid_link2_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_mid_link2.STL" class="collision" />
              <geom rgba="1 1 1 1" name="right_hand_mid_link2_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="right_hand_mid_link2.STL" class="visual" />
              <body name="right_hand_midback_link2" pos="0 0 -0.042248" quat="1.0 0.0 0.0 0.0">
                <inertial pos="0.000157950438652398 -0.00758843721877396 0.0176655210856773" quat="1.0 0.0 0.0 0.0" mass="0.00000001" diaginertia="1e-11 1e-11 1e-11" />
                <geom rgba="1 1 1 1" name="right_hand_midback_link2_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_midback_link2.STL" class="collision" />
                <geom rgba="1 1 1 1" name="right_hand_midback_link2_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9003_Signal_White" type="mesh" mesh="right_hand_midback_link2.STL" class="visual" />
              </body>
              <body name="right_hand_mid_tip" pos="0 0 -0.0422482924089417" quat="1.0 0.0 0.0 0.0">
                <inertial pos="5.97126514900737E-14 5.86336534880161E-16 -8.32667268468867E-16" quat="1.0 0.0 0.0 0.0" mass="0.00000565" diaginertia="1e-11 1e-11 1e-11" />
                <geom rgba="1 1 1 1" name="right_hand_mid_tip_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_mid_tip.STL" class="collision" />
                <geom rgba="1 1 1 1" name="right_hand_mid_tip_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="right_hand_mid_tip.STL" class="visual" />
              </body>
            </body>
          </body>
          <body name="right_hand_ring_link1" pos="-0.016 0.0065 -0.1052" quat="1.0 0.0 0.0 0.0">
            <joint name="right_hand_ring_joint1" type="hinge" ref="0.0" class="motor" range="0 1.919" axis="1 0 0" />
            <inertial pos="3.58049083615322E-05 0.000530417592105594 -0.0332784671157224" quat="1.0 0.0 0.0 0.0" mass="0.06298297" diaginertia="1.738e-05 1.686e-05 3.2e-06" />
            <geom rgba="1 1 1 1" name="right_hand_ring_link1_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_ring_link1.STL" class="collision" />
            <geom rgba="1 1 1 1" name="right_hand_ring_link1_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="right_hand_ring_link1.STL" class="visual" />
            <body name="right_hand_ringback_link1" pos="0 0 -0.0558000000000002" quat="1.0 0.0 0.0 0.0">
              <inertial pos="-0.000148033469798928 -0.0115948018402145 0.0241234223266379" quat="1.0 0.0 0.0 0.0" mass="0.00000002" diaginertia="1e-11 1e-11 1e-11" />
              <geom rgba="1 1 1 1" name="right_hand_ringback_link1_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_ringback_link1.STL" class="collision" />
              <geom rgba="1 1 1 1" name="right_hand_ringback_link1_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9003_Signal_White" type="mesh" mesh="right_hand_ringback_link1.STL" class="visual" />
            </body>
            <body name="right_hand_ring_link2" pos="0 0 -0.0558" quat="1.0 0.0 0.0 0.0">
              <joint name="right_hand_ring_joint2" type="hinge" ref="0.0" class="motor" range="0 1.919" axis="1 0 0" />
              <inertial pos="-0.000248364602035429 0.00119905076177346 -0.0213789908421257" quat="1.0 0.0 0.0 0.0" mass="0.01624108" diaginertia="2.81e-06 2.87e-06 8.6e-07" />
              <geom rgba="1 1 1 1" name="right_hand_ring_link2_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_ring_link2.STL" class="collision" />
              <geom rgba="1 1 1 1" name="right_hand_ring_link2_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="right_hand_ring_link2.STL" class="visual" />
              <body name="right_hand_ringback_link2" pos="0 0 -0.0422482924089403" quat="1.0 0.0 0.0 0.0">
                <inertial pos="0.000157950438638532 -0.00758843721878611 0.0176655210858899" quat="1.0 0.0 0.0 0.0" mass="0.00000001" diaginertia="1e-11 1e-11 1e-11" />
                <geom rgba="1 1 1 1" name="right_hand_ringback_link2_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_ringback_link2.STL" class="collision" />
                <geom rgba="1 1 1 1" name="right_hand_ringback_link2_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9003_Signal_White" type="mesh" mesh="right_hand_ringback_link2.STL" class="visual" />
              </body>
              <body name="right_hand_ring_tip" pos="0 0 -0.0422482924089403" quat="1.0 0.0 0.0 0.0">
                <inertial pos="1.22818422099158E-15 1.69135538907739E-16 0" quat="1.0 0.0 0.0 0.0" mass="0.00000565" diaginertia="1e-11 1e-11 1e-11" />
                <geom rgba="1 1 1 1" name="right_hand_ring_tip_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_ring_tip.STL" class="collision" />
                <geom rgba="1 1 1 1" name="right_hand_ring_tip_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="right_hand_ring_tip.STL" class="visual" />
              </body>
            </body>
          </body>
          <body name="right_hand_pinky_link1" pos="-0.036 0.0065 -0.1022" quat="1.0 0.0 0.0 0.0">
            <joint name="right_hand_pinky_joint1" type="hinge" ref="0.0" class="motor" range="0 1.919" axis="1 0 0" />
            <inertial pos="3.58049083611298E-05 0.000530417592105422 -0.0332784671157224" quat="1.0 0.0 0.0 0.0" mass="0.06298297" diaginertia="1.738e-05 1.686e-05 3.2e-06" />
            <geom rgba="1 1 1 1" name="right_hand_pinky_link1_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_pinky_link1.STL" class="collision" />
            <geom rgba="1 1 1 1" name="right_hand_pinky_link1_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="right_hand_pinky_link1.STL" class="visual" />
            <body name="right_hand_pinkyback_link1" pos="0 0 -0.0558000000000001" quat="1.0 0.0 0.0 0.0">
              <inertial pos="-0.000148034891232163 -0.0115948044185708 0.0241234089219646" quat="1.0 0.0 0.0 0.0" mass="0.00000002" diaginertia="1e-11 1e-11 1e-11" />
              <geom rgba="1 1 1 1" name="right_hand_pinkyback_link1_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_pinkyback_link1.STL" class="collision" />
              <geom rgba="1 1 1 1" name="right_hand_pinkyback_link1_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9003_Signal_White" type="mesh" mesh="right_hand_pinkyback_link1.STL" class="visual" />
            </body>
            <body name="right_hand_pinky_link2" pos="0 0 -0.0558" quat="1.0 0.0 0.0 0.0">
              <joint name="right_hand_pinky_joint2" type="hinge" ref="0.0" class="motor" range="0 1.919" axis="1 0 0" />
              <inertial pos="-0.000248361662015334 0.0011990519020671 -0.0213789854478658" quat="1.0 0.0 0.0 0.0" mass="0.01624108" diaginertia="2.81e-06 2.87e-06 8.6e-07" />
              <geom rgba="1 1 1 1" name="right_hand_pinky_link2_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_pinky_link2.STL" class="collision" />
              <geom rgba="1 1 1 1" name="right_hand_pinky_link2_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="right_hand_pinky_link2.STL" class="visual" />
              <body name="right_hand_pinkyback_link2" pos="0 0 -0.0422482924089404" quat="1.0 0.0 0.0 0.0">
                <inertial pos="0.00015795043861809 -0.00758843721877113 0.0176655210856609" quat="1.0 0.0 0.0 0.0" mass="0.00000001" diaginertia="1e-11 1e-11 1e-11" />
                <geom rgba="1 1 1 1" name="right_hand_pinkyback_link2_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_pinkyback_link2.STL" class="collision" />
                <geom rgba="1 1 1 1" name="right_hand_pinkyback_link2_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9003_Signal_White" type="mesh" mesh="right_hand_pinkyback_link2.STL" class="visual" />
              </body>
              <body name="right_hand_pinky_tip" pos="0 0 -0.0422482924089404" quat="1.0 0.0 0.0 0.0">
                <inertial pos="6.17561557447743E-16 8.67361737988404E-18 0" quat="1.0 0.0 0.0 0.0" mass="0.00000565" diaginertia="1e-11 1e-11 1e-11" />
                <geom rgba="1 1 1 1" name="right_hand_pinky_tip_collision" pos="0 0 0" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="right_hand_pinky_tip.STL" class="collision" />
                <geom rgba="1 1 1 1" name="right_hand_pinky_tip_visual" pos="0 0 0" quat="1.0 0.0 0.0 0.0" material="RAL_9005_Jet_Black" type="mesh" mesh="right_hand_pinky_tip.STL" class="visual" />
              </body>
            </body>
          </body>
          <site name="right_hand_link_site" pos="0 0 0" quat="1 0 0 0" rgba="0.8 0.8 0.8 {site_alpha}" />
        """

    _postamble = """
      <actuator>
        <motor name="right_hand_thumb_bend_joint_ctrl" joint="right_hand_thumb_bend_joint" class="motor" />
        <motor name="right_hand_thumb_rota_joint1_ctrl" joint="right_hand_thumb_rota_joint1" class="motor" />
        <motor name="right_hand_thumb_rota_joint2_ctrl" joint="right_hand_thumb_rota_joint2" class="motor" />
        <motor name="right_hand_index_bend_joint_ctrl" joint="right_hand_index_bend_joint" class="motor" />
        <motor name="right_hand_index_joint1_ctrl" joint="right_hand_index_joint1" class="motor" />
        <motor name="right_hand_index_joint2_ctrl" joint="right_hand_index_joint2" class="motor" />
        <motor name="right_hand_mid_joint1_ctrl" joint="right_hand_mid_joint1" class="motor" />
        <motor name="right_hand_mid_joint2_ctrl" joint="right_hand_mid_joint2" class="motor" />
        <motor name="right_hand_ring_joint1_ctrl" joint="right_hand_ring_joint1" class="motor" />
        <motor name="right_hand_ring_joint2_ctrl" joint="right_hand_ring_joint2" class="motor" />
        <motor name="right_hand_pinky_joint1_ctrl" joint="right_hand_pinky_joint1" class="motor" />
        <motor name="right_hand_pinky_joint2_ctrl" joint="right_hand_pinky_joint2" class="motor" />
      </actuator>
    
      <contact>
        <exclude body1="{name}" body2="right_hand_ee_link" />
        <exclude body1="{name}" body2="right_hand_back_link" />
        <exclude body1="{name}" body2="right_hand_thumb_bend_link" />
        <exclude body1="right_hand_thumb_bend_link" body2="right_hand_thumb_rota_link1" />
        <exclude body1="right_hand_thumb_rota_link1" body2="right_hand_thumb_rotaback_link1" />
        <exclude body1="right_hand_thumb_rota_link1" body2="right_hand_thumb_rota_link2" />
        <exclude body1="right_hand_thumb_rota_link2" body2="right_hand_thumb_rotaback_link2" />
        <exclude body1="right_hand_thumb_rota_link2" body2="right_hand_thumb_rota_tip" />
        <exclude body1="{name}" body2="right_hand_index_bend_link" />
        <exclude body1="right_hand_index_bend_link" body2="right_hand_index_rota_link1" />
        <exclude body1="right_hand_index_rota_link1" body2="right_hand_index_rotaback_link1" />
        <exclude body1="right_hand_index_rota_link1" body2="right_hand_index_rota_link2" />
        <exclude body1="right_hand_index_rota_link2" body2="right_hand_index_rotaback_link2" />
        <exclude body1="right_hand_index_rota_link2" body2="right_hand_index_rota_tip" />
        <exclude body1="{name}" body2="right_hand_mid_link1" />
        <exclude body1="right_hand_mid_link1" body2="right_hand_midback_link1" />
        <exclude body1="right_hand_mid_link1" body2="right_hand_mid_link2" />
        <exclude body1="right_hand_mid_link2" body2="right_hand_midback_link2" />
        <exclude body1="right_hand_mid_link2" body2="right_hand_mid_tip" />
        <exclude body1="{name}" body2="right_hand_ring_link1" />
        <exclude body1="right_hand_ring_link1" body2="right_hand_ringback_link1" />
        <exclude body1="right_hand_ring_link1" body2="right_hand_ring_link2" />
        <exclude body1="right_hand_ring_link2" body2="right_hand_ringback_link2" />
        <exclude body1="right_hand_ring_link2" body2="right_hand_ring_tip" />
        <exclude body1="{name}" body2="right_hand_pinky_link1" />
        <exclude body1="right_hand_pinky_link1" body2="right_hand_pinkyback_link1" />
        <exclude body1="right_hand_pinky_link1" body2="right_hand_pinky_link2" />
        <exclude body1="right_hand_pinky_link2" body2="right_hand_pinkyback_link2" />
        <exclude body1="right_hand_pinky_link2" body2="right_hand_pinky_tip" />
      </contact>
    
      <equality>
        <weld body1="{name}" body2="right-wrist"/>
        <weld body1="right_hand_index_rota_tip" body2="right-index-finger-tip"/>
        <weld body1="right_hand_mid_tip" body2="right-middle-finger-tip"/>
        <weld body1="right_hand_ring_tip" body2="right-ring-finger-tip"/>
        <weld body1="right_hand_pinky_tip" body2="right-pinky-finger-tip"/>
        <weld body1="right_hand_thumb_rota_tip" body2="right-thumb-tip"/>
      </equality>
    
      <sensor>
        <framepos name="right_hand_link_site_pos" objtype="site" objname="right_hand_link_site" />
        <framequat name="right_hand_link_site_quat" objtype="site" objname="right_hand_link_site" />
        <framelinvel name="right_hand_link_site_linvel" objtype="site" objname="right_hand_link_site" />
        <frameangvel name="right_hand_link_site_angvel" objtype="site" objname="right_hand_link_site" />
        <velocimeter name="right_hand_link_site_vel" site="right_hand_link_site" />
      </sensor>
    """


if __name__ == "__main__":
    left_hand = XHandLeft()
    right_hand = XHandRight()
    # print(left_hand._xml  | Prettify())
    print(right_hand._xml | Prettify())

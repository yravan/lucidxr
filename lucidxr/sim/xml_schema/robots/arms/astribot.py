# from utils.transform import compose
# from lucidxr.sim.xml_schema.scene_components.cameras.rig import make_camera_rig
# from lucidxr.sim.xml_schema.scene_components.lighting import make_lighting_rig
# from lucidxr.sim.xml_schema.transforms.mujoco import Vector3, WXYZ

from lucidxr.sim.xml_schema.base import Xml
from lucidxr.sim.xml_schema.schema import Body


class Astribot(Body):
    """
    This is the Gripper for the Ufactory Xarm7 robot.
    """

    assets: str = "robots/astribot"
    end_effector: Xml

    _attributes = {
        "name": "astribot",
        "pos": "0 0 0",
        "quat": "1 0 0 0",
    }

    _mocaps_raw = """
    <body name="{name}-head_target" pos="{head_mocap_pos}" quat="{head_mocap_quat}" mocap="true">
      <!--<geom type="sphere" size=".06" contype="0" conaffinity="0" rgba=".6 .3 .3 .2"/>-->
      <site name="{name}-head_target_site" type="sphere" size="0.01" quat="0.707 -0.707 0 0" rgba="0 0 1 1" group="1"/>
    </body>
    <body name="{name}-arm_right_tool_target" pos="{right_mocap_pos}" quat="{right_mocap_quat}" mocap="true">
      <!--<geom type="sphere" size=".06" contype="0" conaffinity="0" rgba=".6 .3 .3 .2"/>-->
      <site name="{name}-arm_right_tool_target_site" type="sphere" size="0.01" rgba="0 0 1 1" group="1"/>
    </body>
    """

    _postamble = """
    <equality>
      <weld name="{name}-arm_right_tool-weld" site1="{name}-arm_right_tool" site2="{name}-arm_right_tool_target_site" solref="0.003 1" solimp="0.9 0.95 0.001"/>
      <!--<weld name="{name}-head-weld" site1="{name}-head_target_site" site2="{name}-head"/>-->
    </equality>
    """

    _preamble = """
    <default>
      <!--<joint limited="true"/>-->
      <site size="0.005 0 0" rgba="0.4 0.9 0.4 1"/>
      <general ctrllimited="true" ctrlrange="-6.2831 6.2831" forcelimited="true" biastype="affine"/>
    </default>
    
    <asset>
      <mesh name="{name}-astribot_torso_base_link" content_type="model/stl" file="{assets}/astribot_torso_base_link.STL"/>
      <mesh name="{name}-wheel_RF_Link" content_type="model/stl" file="{assets}/wheel_RF_Link.STL"/>
      <mesh name="{name}-wheel_LF_Link" content_type="model/stl" file="{assets}/wheel_LF_Link.STL"/>
      <mesh name="{name}-wheel_RR_Link" content_type="model/stl" file="{assets}/wheel_RR_Link.STL"/>
      <mesh name="{name}-wheel_LR_Link" content_type="model/stl" file="{assets}/wheel_LR_Link.STL"/>
      <mesh name="{name}-astribot_torso_link_1" content_type="model/stl" file="{assets}/astribot_torso_link_1.STL"/>
      <mesh name="{name}-astribot_torso_link_2" content_type="model/stl" file="{assets}/astribot_torso_link_2.STL"/>
      <mesh name="{name}-astribot_torso_link_3" content_type="model/stl" file="{assets}/astribot_torso_link_3.STL"/>
      <mesh name="{name}-astribot_torso_link_4" content_type="model/stl" file="{assets}/astribot_torso_link_4.STL"/>
      <mesh name="{name}-astribot_head_base_link" content_type="model/stl" file="{assets}/astribot_head_base_link.STL"/>
      <mesh name="{name}-astribot_head_link_1" content_type="model/stl" file="{assets}/astribot_head_link_1.STL"/>
      <mesh name="{name}-astribot_head_link_2" content_type="model/stl" file="{assets}/astribot_head_link_2.STL"/>
      <mesh name="{name}-astribot_arm_left_base_link" content_type="model/stl" file="{assets}/astribot_arm_left_base_link.STL"/>
      <mesh name="{name}-astribot_arm_right_base_link" content_type="model/stl" file="{assets}/astribot_arm_right_base_link.STL"/>
      <mesh name="{name}-astribot_arm_link_1" content_type="model/stl" file="{assets}/astribot_arm_link_1.STL"/>
      <mesh name="{name}-astribot_arm_left_link_2" content_type="model/stl" file="{assets}/astribot_arm_left_link_2.STL"/>
      <mesh name="{name}-astribot_arm_link_3" content_type="model/stl" file="{assets}/astribot_arm_link_3.STL"/>
      <mesh name="{name}-astribot_arm_link_4" content_type="model/stl" file="{assets}/astribot_arm_link_4.STL"/>
      <mesh name="{name}-astribot_arm_link_5" content_type="model/stl" file="{assets}/astribot_arm_link_5.STL"/>
      <mesh name="{name}-astribot_arm_link_6" content_type="model/stl" file="{assets}/astribot_arm_link_6.STL"/>
      <mesh name="{name}-astribot_arm_link_7" content_type="model/stl" file="{assets}/astribot_arm_link_7.STL"/>
      <mesh name="{name}-astribot_arm_right_link_2" content_type="model/stl" file="{assets}/astribot_arm_right_link_2.STL"/>
      <mesh name="{name}-gripper_base_link" content_type="model/stl" file="{assets}/astribot_gripper_base_link.STL"/>
      <mesh name="{name}-gripper_L1_Link" content_type="model/stl" file="{assets}/astribot_gripper_L1_Link.STL"/>
      <mesh name="{name}-gripper_L11_Link" content_type="model/stl" file="{assets}/astribot_gripper_L11_Link.STL"/>
      <mesh name="{name}-gripper_L2_Link" content_type="model/stl" file="{assets}/astribot_gripper_L2_Link.STL"/>
      <mesh name="{name}-gripper_R1_Link" content_type="model/stl" file="{assets}/astribot_gripper_R1_Link.STL"/>
      <mesh name="{name}-gripper_R11_Link" content_type="model/stl" file="{assets}/astribot_gripper_R11_Link.STL"/>
      <mesh name="{name}-gripper_R2_Link" content_type="model/stl" file="{assets}/astribot_gripper_R2_Link.STL"/>
    </asset>
    """

    template = """
    <body {attributes}>
      <!--<camera name="third-person" pos="2.205 -1.936 2.187" xyaxes="0.657 0.754 -0.000 -0.354 0.308 0.883"/>-->
      <camera name="third-person" pos="-1.904 -4.026 3.227" xyaxes="0.910 -0.415 0.000 0.183 0.401 0.898"/>
      <inertial pos="-0.0076187 -0.0020711 0.013725" quat="0.019455 0.708067 -0.0183173 0.70564" mass="6.7123" diaginertia="0.148701 0.08243 0.079229"/>
      <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-astribot_torso_base_link"/>
      <body name="{name}-wheel_RF_Link" pos="0.216347 -0.216347 -0.015" quat="0.270599 0.65328 -0.2706 0.653282">
        <inertial pos="2.7624e-07 -1.7583e-07 0.014539" quat="0.270598 0.653281 -0.270598 0.653281" mass="0.56418" diaginertia="0.0015639 0.000831884 0.000831876"/>
        <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-wheel_RF_Link"/>
      </body>
      <body name="{name}-wheel_LF_Link" pos="0.216347 0.216347 -0.015" quat="0.270599 -0.65328 -0.2706 -0.653282">
        <inertial pos="2.7617e-07 -1.7589e-07 0.014539" quat="0.270598 0.653281 -0.270598 0.653281" mass="0.56418" diaginertia="0.0015639 0.000831884 0.000831876"/>
        <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-wheel_LF_Link"/>
      </body>
      <body name="{name}-wheel_RR_Link" pos="-0.216347 -0.211347 -0.015" quat="0.65328 0.270597 -0.653283 0.270598">
        <inertial pos="-2.7619e-07 1.7583e-07 0.014539" quat="0.270598 0.653281 -0.270598 0.653281" mass="0.56418" diaginertia="0.0015639 0.000831884 0.000831876"/>
        <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-wheel_RR_Link"/>
      </body>
      <body name="{name}-wheel_LR_Link" pos="-0.216347 0.211347 -0.015" quat="0.65328 -0.270597 -0.653283 -0.270598">
        <inertial pos="0.0019998 -0.0070713 0.014539" quat="0.653281 0.270598 -0.653281 0.270598" mass="0.56418" diaginertia="0.0015639 0.000831884 0.000831876"/>
        <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-wheel_LR_Link"/>
      </body>
      <body name="{name}-astribot_torso_link_1" pos="0 0 0.12" quat="0.499998 -0.5 0.5 0.500002">
        <inertial pos="-0.15249 0.00021066 -0.0033476" quat="0.488335 0.4894 0.510843 0.510936" mass="7.3766" diaginertia="0.148533 0.14268 0.0286014"/>
        <joint name="{name}-astribot_torso_joint_1" pos="0 0 0" axis="0 0 1" range="0 0.01"  limited="true"/>
        <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-astribot_torso_link_1"/>
        <body name="{name}-astribot_torso_link_2" pos="-0.38 0 0">
          <inertial pos="-0.22214 0.028873 0.00059024" quat="0.0851505 0.715372 -0.0840248 0.688427" mass="5.6183" diaginertia="0.0175257 0.0129591 0.00795872"/>
          <joint name="{name}-astribot_torso_joint_2" pos="0 0 0" axis="0 0 1" range="0 0.01"  limited="true"/>
          <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-astribot_torso_link_2"/>
          <body name="{name}-astribot_torso_link_3" pos="-0.39 0 0">
            <inertial pos="-0.017519 0.00059523 0.00025821" quat="0.00834705 0.708024 0.00970003 0.706073" mass="0.49013" diaginertia="0.000380401 0.000365211 0.000222118"/>
              <site name="{name}-hip" type="sphere" size="0.05" pos="0 0 0"/>
            <joint name="{name}-astribot_torso_joint_3" pos="0 0 0" axis="0 0 1" range="-0.1 0.3"  limited="true"/>
            <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-astribot_torso_link_3"/>
            <body name="{name}-astribot_torso_link_4" quat="0.499998 0.5 -0.500002 -0.5">
              <inertial pos="0.0012784 -5.5993e-05 0.27195" quat="0.996969 0.00493705 -0.0512405 -0.0583368" mass="4.53954" diaginertia="0.0365744 0.0324277 0.0165454"/>
              <joint name="{name}-astribot_torso_joint_4" pos="0 0 0" axis="0 0 1" range="-0.45 0.45"  limited="true"/>
              <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-astribot_torso_link_4"/>
              <geom pos="0 0 0.46765" quat="1 0 0 0" type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-astribot_head_base_link"/>
              <geom pos="0 0.06449 0.36823" quat="0.579228 -0.40558 -0.40558 -0.579228" type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-astribot_arm_left_base_link"/>
              <geom pos="0 -0.06449 0.36823" quat="0.579228 0.40558 -0.40558 0.579228" type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-astribot_arm_right_base_link"/>
              <body name="{name}-astribot_head_link_1" pos="0 0 0.46765">
                <inertial pos="3.191e-05 -0.00038566 -0.0257991" quat="0.710346 -0.0335656 0.0294335 0.702436" mass="0.139106" diaginertia="4.79716e-05 4.56699e-05 3.77084e-05"/>
                <joint name="{name}-astribot_head_joint_1" pos="0 0 0" axis="0 0 1" range="0.0 0.01" limited="true"/>
                <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-astribot_head_link_1"/>
                <body name="{name}-astribot_head_link_2" quat="0.707105 -0.707108 0 0">
                  <inertial pos="0.00705824 -0.144726 -0.00061724" quat="0.696314 0.714797 -0.0643815 -0.00814535" mass="0.970124" diaginertia="0.00559994 0.00544762 0.00147305"/>
                    <site name="{name}-head" type="sphere" size="0.01" pos="0 0 0"/>
                  <joint name="{name}-astribot_head_joint_2" pos="0 0 0" axis="0 0 1" range="0.3 0.31" limited="true"/>
                  <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-astribot_head_link_2"/>
                  <camera name="astribot_head_left" pos="0.06 -0.16 0.035" quat="0 -0.707107 0 0.707107" fovy="60"/>
                    <camera name="astribot_head_right" pos="0.06 -0.16 -0.035" quat="0 -0.707107 0 0.707107" fovy="60"/>
                  <body name="{name}-astribot_head_camera_base_link" pos="0.09 0 0.08" quat="0 0 -1 0">
                </body>
                </body>
              </body>
              <body name="{name}-astribot_arm_left_link_1" pos="-2.29129e-09 0.150002 0.399354" quat="0.579228 -0.40558 -0.40558 -0.579228">
                <inertial pos="-3.38727e-10 -8.2617e-10 -0.0532426" quat="0.707107 0 0 0.707107" mass="0.209778" diaginertia="0.000323596 0.000323124 7.65561e-05"/>
                <joint name="{name}-astribot_arm_left_joint_1" pos="0 0 0" axis="0 0 1" range="-3.1 3.1" limited="true" damping="5" springref="0" stiffness="10"/> <!-- damping="5" springref="0" stiffness="600"/> -->
                <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-astribot_arm_link_1"/>
                <body name="{name}-astribot_arm_left_link_2" quat="0.707105 0.707108 0 0">
                  <inertial pos="-0.0121217 0.0368181 -0.01357" quat="0.791518 0.59161 0.1486 -0.0376264" mass="0.457087" diaginertia="0.000807391 0.00073487 0.00052421"/>
                  <joint name="{name}-astribot_arm_left_joint_2" pos="0 0 0" axis="0 0 1" range="-1.53 0.46" limited="true" damping="5" springref="0" stiffness="10"/> <!-- damping="5" springref="0" stiffness="120" -->
                  <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-astribot_arm_left_link_2"/>
                  <body name="{name}-astribot_arm_left_link_3" pos="0 0.05 0" quat="0.499998 0.5 -0.500002 -0.5">
                    <inertial pos="0.011039 0.000213501 0.240357" quat="0.998444 -0.0037731 0.0555468 0.00311159" mass="0.494215" diaginertia="0.00242787 0.00227335 0.000529931"/>
                    <joint name="{name}-astribot_arm_left_joint_3" pos="0 0 0" axis="0 0 1" range="-3.1 3.1" limited="true" damping="5" springref="-1.57" stiffness="10"/> <!-- damping="5" springref="-1.57" stiffness="600"/> -->
                    <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-astribot_arm_link_3"/>
                    <body name="{name}-astribot_arm_left_link_4" pos="0.03 0 0.309" quat="0.707105 -0.707108 0 0">
                      <inertial pos="7.03915e-06 -0.0168079 -2.59557e-05" quat="0.499707 0.500293 -0.499963 0.500037" mass="0.0997012" diaginertia="0.000116272 9.25243e-05 6.45973e-05"/>
                      <joint name="{name}-astribot_arm_left_joint_4" pos="0 0 0" axis="0 0 1" range="0.7 2.61" limited="true" damping="5"/> <!-- damping="5" -->
                      <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-astribot_arm_link_4"/>
                      <body name="{name}-astribot_arm_left_link_5" quat="0.707105 0.707108 0 0">
                        <inertial pos="-0.000298311 -6.59706e-05 0.195471" quat="0.999978 -0.00282806 0.00595135 0.000919051" mass="0.294855" diaginertia="0.000598295 0.000503604 0.00018486"/>
                        <joint name="{name}-astribot_arm_left_joint_5" pos="0 0 0" axis="0 0 1" range="-2.56 2.56" limited="true" damping="5"/> <!-- damping="5" -->
                        <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-astribot_arm_link_5"/>
                        <body name="{name}-astribot_arm_left_link_6" pos="0 0 0.277" quat="0.707105 -0.707108 0 0">
                          <inertial pos="-1.38286e-05 -2.85328e-08 -1.00704e-08" quat="0.500001 0.499999 0.499999 0.500001" mass="0.0256707" diaginertia="1.67925e-05 1.38505e-05 6.16131e-06"/>
                          <joint name="{name}-astribot_arm_left_joint_6" pos="0 0 0" axis="0 0 1" range="-3 3" limited="true" damping="5"/> <!-- damping="5" -->
                          <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-astribot_arm_link_6"/>
                          <body name="{name}-astribot_arm_left_link_7" quat="0.707105 0 0.707108 0">
                            <inertial pos="0.000159114 -0.00122462 0.0544212" quat="0.996987 -0.0775686 -0.000749819 0.000654519" mass="0.738617" diaginertia="0.00194624 0.00124628 0.000900314"/>
                            <joint name="{name}-astribot_arm_left_joint_7" pos="0 0 0" axis="0 0 1" range="-1.53 1.53" limited="true" damping="5"/> <!-- damping="5" -->
                            <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-astribot_arm_link_7"/>
                            <site name="{name}-arm_left_tool" pos="0 -0.15 0" type="sphere" size="0.01"/>
                            <site name="{name}-force_torque_sensor_left" pos="0 0 0"/>
                            <body name="{name}-astribot_arm_left_tool_link" pos="0 -0.048 0" quat="0.707107 0.707107 0 0">
                                {children}
                            </body>
                          </body>
                        </body>
                      </body>
                    </body>
                  </body>
                </body>
              </body>
              <body name="{name}-astribot_arm_right_link_1" pos="-2.29129e-09 -0.150002 0.399354" quat="0.579228 0.40558 -0.40558 0.579228">
                <inertial pos="-3.38727e-10 -8.2617e-10 -0.0532426" quat="0.707107 0 0 0.707107" mass="0.209778" diaginertia="0.000323596 0.000323124 7.65561e-05"/>
                <joint name="{name}-astribot_arm_right_joint_1" pos="0 0 0" axis="0 0 1" range="-3.1 3.1" limited="true" damping="5"/>
                <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-astribot_arm_link_1"/>
                <body name="{name}-astribot_arm_right_link_2" quat="0.707105 0.707108 0 0">
                  <inertial pos="-0.0121217 0.0368181 -0.01357" quat="0.791518 0.59161 0.1486 -0.0376264" mass="0.457087" diaginertia="0.000807391 0.00073487 0.00052421"/>
                  <joint name="{name}-astribot_arm_right_joint_2" pos="0 0 0" axis="0 0 1" range="-0.46 0.46" limited="true" damping="5"/>
                  <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-astribot_arm_right_link_2"/>
                  <body name="{name}-astribot_arm_right_link_3" pos="0 0.05 0" quat="0.499998 0.5 -0.500002 -0.5">
                    <inertial pos="0.011039 0.000213501 0.240357" quat="0.998444 -0.0037731 0.0555468 0.00311159" mass="0.494215" diaginertia="0.00242787 0.00227335 0.000529931"/>
                    <joint name="{name}-astribot_arm_right_joint_3" pos="0 0 0" axis="0 0 1" range="-3.1 3.1" limited="true" damping="5" springref="1.57" stiffness="10"/>
                    <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-astribot_arm_link_3"/>
                    <body name="{name}-astribot_arm_right_link_4" pos="0.03 0 0.309" quat="0.707105 -0.707108 0 0">
                      <inertial pos="7.03915e-06 -0.0168079 -2.59557e-05" quat="0.499707 0.500293 -0.499963 0.500037" mass="0.0997012" diaginertia="0.000116272 9.25243e-05 6.45973e-05"/>
                      <joint name="{name}-astribot_arm_right_joint_4" pos="0 0 0" axis="0 0 1" range="0.5 2.61" limited="true"/>
                      <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-astribot_arm_link_4"/>
                      <body name="{name}-astribot_arm_right_link_5" quat="0.707105 0.707108 0 0">
                        <inertial pos="-0.000298311 -6.59706e-05 0.195471" quat="0.999978 -0.00282806 0.00595135 0.000919051" mass="0.294855" diaginertia="0.000598295 0.000503604 0.00018486"/>
                        <joint name="{name}-astribot_arm_right_joint_5" pos="0 0 0" axis="0 0 1" range="-2 2" limited="true"/>
                        <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-astribot_arm_link_5"/>
                        <body name="{name}-astribot_arm_right_link_6" pos="0 0 0.277" quat="0.707105 -0.707108 0 0">
                          <inertial pos="-1.38286e-05 -2.85328e-08 -1.00704e-08" quat="0.500001 0.499999 0.499999 0.500001" mass="0.0256707" diaginertia="1.67925e-05 1.38505e-05 6.16131e-06"/>
                          <joint name="{name}-astribot_arm_right_joint_6" pos="0 0 0" axis="0 0 1" range="-0.76 0.76" limited="true"/>
                          <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-astribot_arm_link_6"/>
                          <body name="{name}-astribot_arm_right_link_7" quat="0.707105 0 0.707108 0">
                            <inertial pos="0.000159114 -0.00122462 0.0544212" quat="0.996987 -0.0775686 -0.000749819 0.000654519" mass="0.738617" diaginertia="0.00194624 0.00124628 0.000900314"/>
                            <joint name="{name}-astribot_arm_right_joint_7" pos="0 0 0" axis="0 0 1" range="-1.53 1.53" limited="true"/>
                            <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="1 1 1 1" mesh="{name}-astribot_arm_link_7"/>
                            <site name="{name}-arm_right_tool" pos="0 -0.18 0" size="0.01" xyaxes="0 0 -1 1 0 0"/>
                              <body name="{name}-astribot_arm_right_tool_link" pos="0 -0.048 0" quat="0.707107 0.707107 0 0">
                                  <camera name="astribot_arm_right_effector" pos="0 0.16 -0.05" quat="1.28555e-06 3.28254e-07 0.968912 0.247404" fovy="60"/>
                              </body>
                              <site name="{name}-force_torque_sensor_right" pos="0 0 0"/>
                          </body>
                        </body>
                      </body>
                    </body>
                  </body>
                </body>
              </body>
            </body>
          </body>
        </body>
      </body>
    </body>
    """

    def __init__(self, *_children, end_effector: Xml = None, head_mocap_quat=None, **kwargs):
        super().__init__(*_children, **kwargs)
        self.end_effector = end_effector if end_effector is not None else ""
        self._children = self._children + (self.end_effector,)

        self.head_mocap_pos = self._pos + [0, 0, 1.5]
        # self.right_mocap_pos = self._pos + [0.45, -0.21, 0.75]
        self.right_mocap_pos = self._pos + [0.06, -0.257, 0.58]
        self.right_mocap_quat = " ".join([str(x) for x in [0.0664525, -0.865559, 0.142244, -0.475561]])

        self.head_mocap_quat = " ".join(
            str(x) for x in (head_mocap_quat if head_mocap_quat is not None else (1, 0, 0, 0))
        )

        values = self._format_dict()

        self._mocaps = self._mocaps_raw.format(**values)

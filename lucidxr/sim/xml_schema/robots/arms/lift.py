
import lucidxr.sim.xml_schema.transforms.mujoco as m
from lucidxr.sim.xml_schema.base import Xml
from lucidxr.sim.xml_schema.schema import Body


class Lift(Body):
    """
    This is LIFT from ARX
    """

    assets: str = "robots/lift"
    end_effector: Xml = None

    def __init__(
        self,
        *_children,
        end_effector: Xml = None,
        mocap_pos=None,
        right_hand=True,
        left_hand=True,
        head=True,
        **kwargs,
    ):
        super().__init__(*_children, **kwargs)
        self.end_effector = end_effector
        if end_effector:
            self._children = self._children + (end_effector,)

        # 0.5114, 0.37265
        # [0.36575, 0, 0.36065]
        if mocap_pos is None:
            self.mocap_pos = m.transform_point(self._pos, self._quat, [0.455, 0, 0.36065])
        else:
            self.mocap_pos = mocap_pos

        # self._children = self._children + (self.mocap_pos,)

        self.mocap_pos_right = m.transform_point(self._pos, self._quat, [-0.35, 0.275, 0.5])
        self.mocap_pos_left = m.transform_point(self._pos, self._quat, [-0.35, -0.275, 0.5])
        self.mocap_pos_head = m.transform_point(self._pos, self._quat, [-0.3, 0.0, 0.65])

        self._attributes = {
            "name": "lift",
            "childclass": "lift",
            "pos": self._pos,
            "quat": self._quat if self._quat else "1 0 0 0",
        }

        values = self._format_dict()

        self._mocaps_body = ""
        self._mocaps_equality = ""

        if left_hand:
            self._mocaps_body += self.left_arm_mocap
            self._mocaps_equality += self.left_mocap_equality
        if right_hand:
            self._mocaps_body += self.right_arm_mocap
            self._mocaps_equality += self.right_mocap_equality
        if head:
            self._mocaps_body += self.head_mocap
            self._mocaps_equality += self.head_mocap_equality

        self._mocaps = self._mocaps_body.format(**values)

    left_arm_mocap = """
    <body mocap="true" name="{name}-mocap-1" pos="{mocap_pos_left}">
      <site name="{name}-mocap-site-1" size=".075" type="sphere" rgba="0.13 0.3 0.2 1"/>
    </body>
    """

    right_arm_mocap = """
    <body mocap="true" name="{name}-mocap-2" pos="{mocap_pos_right}">
      <site name="{name}-mocap-site-2" size=".075" type="sphere" rgba="0.13 0.3 0.2 1"/>
    </body>
    """

    head_mocap = """
    <body mocap="true" name="{name}-mocap-3" pos="{mocap_pos_head}">
      <site name="{name}-mocap-site-3" size=".075" type="sphere" rgba="0.13 0.3 0.2 1"/>
    </body>
    """

    # _mocaps_body = """
    # <body mocap="true" name="{name}-mocap-1" pos="{mocap_pos_left}">
    #   <site name="{name}-mocap-site-1" size=".075" type="sphere" rgba="0.13 0.3 0.2 1"/>
    # </body>
    # <body mocap="true" name="{name}-mocap-2" pos="{mocap_pos_right}">
    #   <site name="{name}-mocap-site-2" size=".075" type="sphere" rgba="0.13 0.3 0.2 1"/>
    # </body>
    # <body mocap="true" name="{name}-mocap-3" pos="{mocap_pos_head}">
    #   <site name="{name}-mocap-site-3" size=".075" type="sphere" rgba="0.13 0.3 0.2 1"/>
    # </body>
    # """

    left_mocap_equality = """
    <equality>
        <weld body1="{name}-left_arm_link6" body2="{name}-mocap-1"/>
    </equality>
    """

    right_mocap_equality = """
    <equality>
        <weld body1="{name}-right_arm_link6" body2="{name}-mocap-2"/>
        <joint joint1="{name}-right_catch_joint1"
         joint2="{name}-right_catch_joint2"
         polycoef="0 -1 0 0 0"
         solimp="0.95 0.99 0.001" solref="0.005 1"/>
    </equality>
    """

    head_mocap_equality = """
    <equality>
        <weld body1="{name}-h_link2_1" body2="{name}-mocap-3"/>
    </equality>
    """

    # _mocaps_equality = """
    # <equality>
    #     <weld body1="{name}-right_arm_link6" body2="{name}-mocap-1"/>
    #     <weld body1="{name}-left_arm_link6" body2="{name}-mocap-2"/>
    #     <weld body1="{name}-h_link2_1" body2="{name}-mocap-3"/>
    #     <joint joint1="{name}-right_catch_joint1"
    #      joint2="{name}-right_catch_joint2"
    #      polycoef="0 -1 0 0 0"
    #      solimp="0.95 0.99 0.001" solref="0.005 1"/>
    # </equality>
    # """

    _preamble = """
      <default>
        <default class="{childclass}">
          <default class="{childclass}-motor">
            <joint />
            <motor />
          </default>
          <default class="{childclass}-visual">
            <geom material="{name}-visualgeom" contype="0" conaffinity="0" group="2" />
          </default>
          <default class="{childclass}-collision">
            <geom material="{name}-collision_material" condim="3" contype="0" conaffinity="1" priority="1" group="1" solref="0.005 1" friction="1 0.01 0.01" />
            <equality solimp="0.99 0.999 1e-05" solref="0.005 1" />
          </default>
        </default>
      </default>
      <default>
          <general biastype="affine"/>
      </default>

      <compiler angle="radian" />

      <asset>
        <material name="{name}-silver" rgba="0.700 0.700 0.700 1.000" />
        <material name="{name}-default_material" rgba="0.7 0.7 0.7 1" />
        <material name="{name}-collision_material" rgba="1.0 0.28 0.1 0" />
        <mesh name="{name}-base_link.stl" file="{assets}/base_link.stl" scale="0.001 0.001 0.001"/>
        <mesh name="{name}-wheel_1.stl" file="{assets}/wheel_1.stl" scale="0.001 0.001 0.001"/>
        <mesh name="{name}-wheel_2.stl" file="{assets}/wheel_2.stl" scale="0.001 0.001 0.001"/>
        <mesh name="{name}-wheel_3.stl" file="{assets}/wheel_3.stl" scale="0.001 0.001 0.001"/>
        <mesh name="{name}-lift.stl" file="{assets}/lift.stl" scale="0.001 0.001 0.001"/>
        <mesh name="{name}-h_base.stl" file="{assets}/h_base.stl" scale="0.001 0.001 0.001"/>
        <mesh name="{name}-h_link1.stl" file="{assets}/h_link1.stl" scale="0.001 0.001 0.001"/>
        <mesh name="{name}-h_link2.stl" file="{assets}/h_link2.stl" scale="0.001 0.001 0.001"/>
        <mesh name="{name}-arm_base_link.stl" file="{assets}/arm_base_link.stl" scale="0.001 0.001 0.001"/>
        <mesh name="{name}-arm_link1.stl" file="{assets}/arm_link1.stl" scale="0.001 0.001 0.001"/>
        <mesh name="{name}-arm_link2.stl" file="{assets}/arm_link2.stl" scale="0.001 0.001 0.001"/>
        <mesh name="{name}-arm_link3.stl" file="{assets}/arm_link3.stl" scale="0.001 0.001 0.001"/>
        <mesh name="{name}-arm_link4.stl" file="{assets}/arm_link4.stl" scale="0.001 0.001 0.001"/>
        <mesh name="{name}-arm_link5.stl" file="{assets}/arm_link5.stl" scale="0.001 0.001 0.001"/>
        <mesh name="{name}-arm_link6.stl" file="{assets}/arm_link6.stl" scale="0.001 0.001 0.001"/>
        <mesh name="{name}-arm_left_catch.stl" file="{assets}/arm_left_catch.stl" scale="0.001 0.001 0.001"/>
        <mesh name="{name}-arm_right_catch.stl" file="{assets}/arm_right_catch.stl" scale="0.001 0.001 0.001"/>
      </asset>
    """

    template = """
         <body {attributes}>
          <joint name="{name}-floating_base" />
          <geom name="{name}-base_link_collision" pos="-0.02589436313797319 -0.09143146519519073 0.05911679497216196" quat="0.7071067811865492 -9.243919350500756e-15 5.357940515258378e-15 -0.7071067811865459" type="mesh" mesh="{name}-base_link.stl"  class="{childclass}-collision" />
          <geom name="{name}-base_link_visual" pos="-0.02589436313797319 -0.09143146519519073 0.05911679497216196" quat="0.7071067811865492 -9.243919350500756e-15 5.357940515258378e-15 -0.7071067811865459" material="{name}-silver" type="mesh" mesh="{name}-base_link.stl"  class="{childclass}-visual" />
          <body name="{name}-wheel_1" pos="-0.182349 0.315838 0.03" quat="1.0 0.0 0.0 0.0">
            <joint name="{name}-joint_wheel1" type="hinge" ref="0.0" class="{childclass}-motor" axis="-0.5 0.866025 0.0" />
            <inertial pos="-0.0013052205916280202 0.0022598671755268973 1.318970376112949e-07" quat="1.0 0.0 0.0 0.0" mass="4.24803000494366" diaginertia="0.008031 0.010834 0.006629" />
            <geom name="{name}-wheel_1_collision" pos="0.182349 -0.315838 -0.03" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="{name}-wheel_1.stl"  class="{childclass}-collision" />
            <geom name="{name}-wheel_1_visual" pos="0.182349 -0.315838 -0.03" quat="1.0 0.0 0.0 0.0" material="{name}-silver" type="mesh" mesh="{name}-wheel_1.stl"  class="{childclass}-visual" />
          </body>
          <body name="{name}-wheel_2" pos="-0.182349 -0.315838 0.03" quat="1.0 0.0 0.0 0.0">
            <joint name="{name}-joint_wheel2" type="hinge" ref="0.0" class="{childclass}-motor" axis="-0.5 -0.866025 0.0" />
            <inertial pos="-0.0013052205916208315 -0.0022598671755325594 -1.318970357273852e-07" quat="1.0 0.0 0.0 0.0" mass="4.24803000494366" diaginertia="0.008031 0.010834 0.006629" />
            <geom name="{name}-wheel_2_collision" pos="0.182349 0.315838 -0.03" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="{name}-wheel_2.stl"  class="{childclass}-collision" />
            <geom name="{name}-wheel_2_visual" pos="0.182349 0.315838 -0.03" quat="1.0 0.0 0.0 0.0" material="{name}-silver" type="mesh" mesh="{name}-wheel_2.stl"  class="{childclass}-visual" />
          </body>
          <body name="{name}-wheel_3" pos="0.364699 0.0 0.03" quat="1.0 0.0 0.0 0.0">
            <joint name="{name}-joint_wheel3" type="hinge" ref="0.0" class="{childclass}-motor" axis="1.0 0.0 -0.0" />
            <inertial pos="0.0026089441594678298 -1.3189703553351252e-07 2.8695680726054107e-07" quat="1.0 0.0 0.0 0.0" mass="4.24803000494366" diaginertia="0.012235 0.006629 0.006629" />
            <geom name="{name}-wheel_3_collision" pos="-0.364699 -0.0 -0.03" quat="1.0 0.0 0.0 0.0" type="mesh" mesh="{name}-wheel_3.stl"  class="{childclass}-collision" />
            <geom name="{name}-wheel_3_visual" pos="-0.364699 -0.0 -0.03" quat="1.0 0.0 0.0 0.0" material="{name}-silver" type="mesh" mesh="{name}-wheel_3.stl"  class="{childclass}-visual" />
          </body>
          <body name="{name}-lift_1" pos="0.022199 0.07 0.233" quat="1.0 0.0 0.0 0.0">
            <joint name="{name}-joint_lift" type="slide" ref="0.0" class="{childclass}-motor" range="0.0 0.86" axis="0.0 0.0 1.0" />
            <inertial pos="-0.13956899916103924 -0.07061717818525884 0.07323798891482189" quat="1.0 0.0 0.0 0.0" mass="17.38744536890084" diaginertia="0.187458 0.178157 0.29708" />
            <geom name="{name}-lift_1_collision" pos="0.23377630259911772 -0.9431740063510481 1.8984630014809656" quat="-1.7328692910742418e-15 -0.7071067811865492 0.7071067811865459 -2.447501880171311e-15" type="mesh" mesh="{name}-lift.stl"  class="{childclass}-collision" />
            <geom name="{name}-lift_1_visual" pos="0.23377630259911772 -0.9431740063510481 1.8984630014809656" quat="-1.7328692910742418e-15 -0.7071067811865492 0.7071067811865459 -2.447501880171311e-15" material="{name}-silver" type="mesh" mesh="{name}-lift.stl"  class="{childclass}-visual" />
            <body name="{name}-h_base_link" pos="-0.258786 -0.07000 0.220008" quat="2.6794896585028633e-08 0.0 0.9999999999999997 0.0">
              <inertial pos="-0.0020743076738515215 -1.5307881645835308e-08 -0.024619861716967787" quat="1.0 0.0 0.0 0.0" mass="0.9930933606993821" diaginertia="0.000391 0.000452 0.000532" />
              <geom name="{name}-h_base_link_collision" pos="-0.08527048097893797 -0.1374690238644495 1.311881544560024" quat="1.0 -3.076315244210524e-15 -3.8077180297680804e-16 -4.7649818118999294e-14" type="mesh" mesh="{name}-h_base.stl"  class="{childclass}-collision" />
              <geom name="{name}-h_base_link_visual" pos="-0.08527048097893797 -0.1374690238644495 1.311881544560024" quat="1.0 -3.076315244210524e-15 -3.8077180297680804e-16 -4.7649818118999294e-14" material="{name}-silver" type="mesh" mesh="{name}-h_base.stl"  class="{childclass}-visual" />
              <body name="{name}-h_link1_1" pos="0.0 0.0 -0.046" quat="1.0 0.0 0.0 0.0">
                <joint name="{name}-joint_h_1" type="hinge" ref="0.0" class="{childclass}-motor" axis="0.0 -0.0 1.0" />
                <inertial pos="-1.3121512495483172e-08 -0.0017956601536253606 -0.0404485568834118" quat="1.0 0.0 0.0 0.0" mass="1.1585686692835446" diaginertia="0.000714 0.000677 0.000524" />
                <geom name="{name}-h_link1_1_collision" pos="-0.12236311194583296 0.2951630600814396 -0.7084366619197162" quat="3.73575297935565e-14 -3.024304153546938e-14 -0.7071067811865475 0.7071067811865477" type="mesh" mesh="{name}-h_link1.stl"  class="{childclass}-collision" />
                <geom name="{name}-h_link1_1_visual" pos="-0.12236311194583296 0.2951630600814396 -0.7084366619197162" quat="3.73575297935565e-14 -3.024304153546938e-14 -0.7071067811865475 0.7071067811865477" material="{name}-silver" type="mesh" mesh="{name}-h_link1.stl"  class="{childclass}-visual" />
                <body name="{name}-h_link2_1" pos="0.0 0.025 -0.047" quat="1.0 0.0 0.0 0.0">
                  <joint name="{name}-joint_h_2" type="hinge" ref="0.0" class="{childclass}-motor" axis="-0.0 -1.0 0.0" />
                  <inertial pos="0.03081593597576142 -0.022504711493597663 -0.0659240377971316" quat="1.0 0.0 0.0 0.0" mass="1.5752562353484625" diaginertia="0.004555 0.004541 0.00636" />
                  <geom name="{name}-h_link2_1_collision" pos="-0.08527048097895003 -0.16246902386446574 1.4048815445600387" quat="1.0 -1.3749689411803468e-16 5.09054604025389e-15 -4.6182286204091326e-14" type="mesh" mesh="{name}-h_link2.stl"  class="{childclass}-collision" />
                  <geom name="{name}-h_link2_1_visual" pos="-0.08527048097895003 -0.16246902386446574 1.4048815445600387" quat="1.0 -1.3749689411803468e-16 5.09054604025389e-15 -4.6182286204091326e-14" material="{name}-silver" type="mesh" mesh="{name}-h_link2.stl"  class="{childclass}-visual" />
                </body>
              </body>
            </body>
            <body name="{name}-left_arm_base_link" pos="-0.193501 -0.32000 0.083998" quat="2.6794896585028633e-08 0.0 0.9999999999999997 0.0">
              <inertial pos="-0.0001456050150032109 -7.271800715889125e-05 -0.03159354340734995" quat="1.0 0.0 0.0 0.0" mass="1.1276471378072246" diaginertia="0.000524 0.000527 0.000538" />
              <geom name="{name}-left_arm_base_link_collision" pos="0.007409306349121554 -0.041273942276757764 -0.09300023656190275" quat="0.5213338044737345 -0.5213338044734593 -0.47771441710840734 0.4777144171081144" type="mesh" mesh="{name}-arm_base_link.stl"  class="{childclass}-collision" />
              <geom name="{name}-left_arm_base_link_visual" pos="0.007409306349121554 -0.041273942276757764 -0.09300023656190275" quat="0.5213338044737345 -0.5213338044734593 -0.47771441710840734 0.4777144171081144" material="{name}-silver" type="mesh" mesh="{name}-arm_base_link.stl"  class="{childclass}-visual" />
              <body name="{name}-left_arm_link1" pos="0.0 0.0 -0.0565" quat="1.0 0.0 0.0 0.0">
                <joint name="{name}-left_arm_joint1" type="hinge" ref="0.0" class="{childclass}-motor" axis="-0.0 -0.0 1.0" />
                <inertial pos="0.005695029028846315 0.007271965833248688 -0.020896953872813907" quat="1.0 0.0 0.0 0.0" mass="0.2814477837021216" diaginertia="0.000303 0.000139 0.00028" />
                <geom name="{name}-left_arm_link1_collision" pos="0.003959285303010329 -0.0003463925796654088 0.026992272292183782" quat="0.5213338044737351 -0.5213338044734588 -0.47771441710840556 0.47771441710811624" type="mesh" mesh="{name}-arm_link1.stl"  class="{childclass}-collision" />
                <geom name="{name}-left_arm_link1_visual" pos="0.003959285303010329 -0.0003463925796654088 0.026992272292183782" quat="0.5213338044737351 -0.5213338044734588 -0.47771441710840556 0.47771441710811624" material="{name}-silver" type="mesh" mesh="{name}-arm_link1.stl"  class="{childclass}-visual" />
                <body name="{name}-left_arm_link2" pos="0.022299 0.025403 -0.047" quat="1.0 0.0 0.0 0.0">
                  <joint name="{name}-left_arm_joint2" type="hinge" ref="0.0" class="{childclass}-motor" axis="0.087156 0.996195 0.0" />
                  <inertial pos="-0.13152163105173825 -0.014795828980240422 3.909377899950772e-05" quat="1.0 0.0 0.0 0.0" mass="3.2738322976375356" diaginertia="0.002162 0.043867 0.044191" />
                  <geom name="{name}-left_arm_link2_collision" pos="-0.018339714696967803 -0.02574939257965983 0.07399227229217917" quat="0.5213338044737443 -0.5213338044734502 -0.47771441710839796 0.4777144171081229" type="mesh" mesh="{name}-arm_link2.stl"  class="{childclass}-collision" />
                  <geom name="{name}-left_arm_link2_visual" pos="-0.018339714696967803 -0.02574939257965983 0.07399227229217917" quat="0.5213338044737443 -0.5213338044734502 -0.47771441710839796 0.4777144171081229" material="{name}-silver" type="mesh" mesh="{name}-arm_link2.stl"  class="{childclass}-visual" />
                  <body name="{name}-left_arm_link3" pos="-0.262996 0.023009 0.0" quat="1.0 0.0 0.0 0.0">
                    <joint name="{name}-left_arm_joint3" type="hinge" ref="0.0" class="{childclass}-motor" axis="0.087156 0.996195 0.0" />
                    <inertial pos="0.1464097574775916 -0.03950335038970569 -0.055156332017432905" quat="1.0 0.0 0.0 0.0" mass="2.8273308884294726" diaginertia="0.002779 0.026162 0.025936" />
                    <geom name="{name}-left_arm_link3_collision" pos="0.24465628530304592 -0.04875839257959501 0.07399227229217889" quat="0.5213338044737441 -0.52133380447345 -0.4777144171083982 0.4777144171081231" type="mesh" mesh="{name}-arm_link3.stl"  class="{childclass}-collision" />
                    <geom name="{name}-left_arm_link3_visual" pos="0.24465628530304592 -0.04875839257959501 0.07399227229217889" quat="0.5213338044737441 -0.52133380447345 -0.4777144171083982 0.4777144171081231" material="{name}-silver" type="mesh" mesh="{name}-arm_link3.stl"  class="{childclass}-visual" />
                    <body name="{name}-left_arm_link4" pos="0.244067 -0.021403 -0.06" quat="1.0 0.0 0.0 0.0">
                      <joint name="{name}-left_arm_joint4" type="hinge" ref="0.0" class="{childclass}-motor" axis="0.087156 0.996195 0.0" />
                      <inertial pos="0.039690032456672866 -0.025382085939758787 -0.033369810917050824" quat="1.0 0.0 0.0 0.0" mass="0.3614635103426687" diaginertia="0.000648 0.000701 0.000483" />
                      <geom name="{name}-left_arm_link4_collision" pos="0.0005892853030446308 -0.027355392579593747 0.13399227229218344" quat="0.5213338044737443 -0.5213338044734501 -0.47771441710839807 0.477714417108123" type="mesh" mesh="{name}-arm_link4.stl"  class="{childclass}-collision" />
                      <geom name="{name}-left_arm_link4_visual" pos="0.0005892853030446308 -0.027355392579593747 0.13399227229218344" quat="0.5213338044737443 -0.5213338044734501 -0.47771441710839807 0.477714417108123" material="{name}-silver" type="mesh" mesh="{name}-arm_link4.stl"  class="{childclass}-visual" />
                      <body name="{name}-left_arm_link5" pos="0.067612 -0.033219 -0.0845" quat="1.0 0.0 0.0 0.0">
                        <joint name="{name}-left_arm_joint5" type="hinge" ref="0.0" class="{childclass}-motor" axis="0.0 0.0 -1.0" />
                        <inertial pos="0.0035114951739801253 -0.00032438367383951644 0.05339769316683546" quat="1.0 0.0 0.0 0.0" mass="1.682735565009155" diaginertia="0.002208 0.002158 0.000703" />
                        <geom name="{name}-left_arm_link5_collision" pos="0.030052794300312463 -0.05494208160627965 -0.057241042913650286" quat="0.7781655406314117 5.330121110899127e-14 3.1363692581466355e-13 -0.6280592260080435" type="mesh" mesh="{name}-arm_link5.stl"  class="{childclass}-collision" />
                        <geom name="{name}-left_arm_link5_visual" pos="0.030052794300312463 -0.05494208160627965 -0.057241042913650286" quat="0.7781655406314117 5.330121110899127e-14 3.1363692581466355e-13 -0.6280592260080435" material="{name}-silver" type="mesh" mesh="{name}-arm_link5.stl"  class="{childclass}-visual" />
                        <body name="{name}-left_arm_link6" pos="0.02884 -0.002523 0.0845" quat="1.0 0.0 0.0 0.0">
                          <joint name="{name}-left_arm_joint6" type="hinge" ref="0.0" class="{childclass}-motor" axis="-0.996195 0.087156 0.0" />
                          <inertial pos="0.04606151123037028 -0.00403375833742786 -0.02029844922950161" quat="1.0 0.0 0.0 0.0" mass="1.6175866280512115" diaginertia="0.002554 0.002684 0.001423" />
                          <geom name="{name}-left_arm_link6_collision" pos="0.07015096496844125 -0.0940377631493199 0.017299995001154284" quat="2.077741045466414e-13 -0.7372773368101248 -0.6755902076156596 -1.9444558750972757e-13" type="mesh" mesh="{name}-arm_link6.stl"  class="{childclass}-collision" />
                          <geom name="{name}-left_arm_link6_visual" pos="0.07015096496844125 -0.0940377631493199 0.017299995001154284" quat="2.077741045466414e-13 -0.7372773368101248 -0.6755902076156596 -1.9444558750972757e-13" material="{name}-silver" type="mesh" mesh="{name}-arm_link6.stl"  class="{childclass}-visual" />
                          <body name="{name}-left_arm_left_catch" pos="0.067534 -0.091232 -0.005" quat="1.0 0.0 0.0 0.0">
                            <joint name="{name}-left_catch_joint1" type="slide" ref="0.0" class="{childclass}-motor" range="-0.0445 0.0" axis="0.087156 0.996195 0.0" />
                            <inertial pos="0.022696371000088422 0.06755851746973854 0.008381661910845134" quat="1.0 0.0 0.0 0.0" mass="0.25047156301061513" diaginertia="9.7e-05 0.000157 0.000137" />
                            <geom name="{name}-left_arm_left_catch_collision" pos="-0.2827978086885289 -0.2179220999653169 -0.13086553021673955" quat="0.5213338044737432 -0.521333804473451 -0.47771441710839885 0.47771441710812224" type="mesh" mesh="{name}-arm_left_catch.stl"  class="{childclass}-collision" />
                            <geom name="{name}-left_arm_left_catch_visual" pos="-0.2827978086885289 -0.2179220999653169 -0.13086553021673955" quat="0.5213338044737432 -0.521333804473451 -0.47771441710839885 0.47771441710812224" material="{name}-silver" type="mesh" mesh="{name}-arm_left_catch.stl"  class="{childclass}-visual" />
                          </body>
                          <body name="{name}-left_arm_right_catch" pos="0.08235 0.078122 -0.005" quat="1.0 0.0 0.0 0.0">
                            <joint name="{name}-left_catch_joint2" type="slide" ref="0.0" class="{childclass}-motor" range="0.0 0.0445" axis="0.087156 0.996195 0.0" />
                            <inertial pos="0.01062064996036352 -0.0704739510881078 0.0022902966101032707" quat="1.0 0.0 0.0 0.0" mass="0.2504715624632503" diaginertia="0.000107 0.000152 0.000137" />
                            <geom name="{name}-left_arm_right_catch_collision" pos="-0.3341410986133092 -0.4899139341993404 -0.028033322065217275" quat="0.5213338044737442 -0.5213338044734503 -0.4777144171083979 0.47771441710812296" type="mesh" mesh="{name}-arm_right_catch.stl"  class="{childclass}-collision" />
                            <geom name="{name}-left_arm_right_catch_visual" pos="-0.3341410986133092 -0.4899139341993404 -0.028033322065217275" quat="0.5213338044737442 -0.5213338044734503 -0.4777144171083979 0.47771441710812296" material="{name}-silver" type="mesh" mesh="{name}-arm_right_catch.stl"  class="{childclass}-visual" />
                          </body>
                        </body>
                      </body>
                    </body>
                  </body>
                </body>
              </body>
            </body>
            <body name="{name}-right_arm_base_link" pos="-0.193501 0.18000 0.083998" quat="2.6794896585028633e-08 0.0 0.9999999999999997 0.0">
              <inertial pos="-0.0001456050150032109 -7.271800715889125e-05 -0.03159354340734995" quat="1.0 0.0 0.0 0.0" mass="1.1276471378072246" diaginertia="0.000524 0.000527 0.000538" />
              <geom name="{name}-right_arm_base_link_collision" pos="0.007409306349121554 -0.041273942276757764 -0.09300023656190275" quat="0.5213338044737345 -0.5213338044734593 -0.47771441710840734 0.4777144171081144" type="mesh" mesh="{name}-arm_base_link.stl"  class="{childclass}-collision" />
              <geom name="{name}-right_arm_base_link_visual" pos="0.007409306349121554 -0.041273942276757764 -0.09300023656190275" quat="0.5213338044737345 -0.5213338044734593 -0.47771441710840734 0.4777144171081144" material="{name}-silver" type="mesh" mesh="{name}-arm_base_link.stl"  class="{childclass}-visual" />
              <body name="{name}-right_arm_link1" pos="0.0 0.0 -0.0565" quat="1.0 0.0 0.0 0.0">
                <joint name="{name}-right_arm_joint1" type="hinge" ref="0.0" class="{childclass}-motor" axis="-0.0 -0.0 1.0" />
                <inertial pos="0.005695029028846315 0.007271965833248688 -0.020896953872813907" quat="1.0 0.0 0.0 0.0" mass="0.2814477837021216" diaginertia="0.000303 0.000139 0.00028" />
                <geom name="{name}-right_arm_link1_collision" pos="0.003959285303010329 -0.0003463925796654088 0.026992272292183782" quat="0.5213338044737351 -0.5213338044734588 -0.47771441710840556 0.47771441710811624" type="mesh" mesh="{name}-arm_link1.stl"  class="{childclass}-collision" />
                <geom name="{name}-right_arm_link1_visual" pos="0.003959285303010329 -0.0003463925796654088 0.026992272292183782" quat="0.5213338044737351 -0.5213338044734588 -0.47771441710840556 0.47771441710811624" material="{name}-silver" type="mesh" mesh="{name}-arm_link1.stl"  class="{childclass}-visual" />
                <body name="{name}-right_arm_link2" pos="0.022299 0.025403 -0.047" quat="1.0 0.0 0.0 0.0">
                  <joint name="{name}-right_arm_joint2" type="hinge" ref="0.0" class="{childclass}-motor" axis="0.087156 0.996195 0.0" />
                  <inertial pos="-0.13152163105173825 -0.014795828980240422 3.909377899950772e-05" quat="1.0 0.0 0.0 0.0" mass="3.2738322976375356" diaginertia="0.002162 0.043867 0.044191" />
                  <geom name="{name}-right_arm_link2_collision" pos="-0.018339714696967803 -0.02574939257965983 0.07399227229217917" quat="0.5213338044737443 -0.5213338044734502 -0.47771441710839796 0.4777144171081229" type="mesh" mesh="{name}-arm_link2.stl"  class="{childclass}-collision" />
                  <geom name="{name}-right_arm_link2_visual" pos="-0.018339714696967803 -0.02574939257965983 0.07399227229217917" quat="0.5213338044737443 -0.5213338044734502 -0.47771441710839796 0.4777144171081229" material="{name}-silver" type="mesh" mesh="{name}-arm_link2.stl"  class="{childclass}-visual" />
                  <body name="{name}-right_arm_link3" pos="-0.262996 0.023009 0.0" quat="1.0 0.0 0.0 0.0">
                    <joint name="{name}-right_arm_joint3" type="hinge" ref="0.0" class="{childclass}-motor" axis="0.087156 0.996195 0.0" />
                    <inertial pos="0.1464097574775916 -0.03950335038970569 -0.055156332017432905" quat="1.0 0.0 0.0 0.0" mass="2.8273308884294726" diaginertia="0.002779 0.026162 0.025936" />
                    <geom name="{name}-right_arm_link3_collision" pos="0.24465628530304592 -0.04875839257959501 0.07399227229217889" quat="0.5213338044737441 -0.52133380447345 -0.4777144171083982 0.4777144171081231" type="mesh" mesh="{name}-arm_link3.stl"  class="{childclass}-collision" />
                    <geom name="{name}-right_arm_link3_visual" pos="0.24465628530304592 -0.04875839257959501 0.07399227229217889" quat="0.5213338044737441 -0.52133380447345 -0.4777144171083982 0.4777144171081231" material="{name}-silver" type="mesh" mesh="{name}-arm_link3.stl"  class="{childclass}-visual" />
                    <body name="{name}-right_arm_link4" pos="0.244067 -0.021403 -0.06" quat="1.0 0.0 0.0 0.0">
                      <joint name="{name}-right_arm_joint4" type="hinge" ref="0.0" class="{childclass}-motor" axis="0.087156 0.996195 0.0" />
                      <inertial pos="0.039690032456672866 -0.025382085939758787 -0.033369810917050824" quat="1.0 0.0 0.0 0.0" mass="0.3614635103426687" diaginertia="0.000648 0.000701 0.000483" />
                      <geom name="{name}-right_arm_link4_collision" pos="0.0005892853030446308 -0.027355392579593747 0.13399227229218344" quat="0.5213338044737443 -0.5213338044734501 -0.47771441710839807 0.477714417108123" type="mesh" mesh="{name}-arm_link4.stl"  class="{childclass}-collision" />
                      <geom name="{name}-right_arm_link4_visual" pos="0.0005892853030446308 -0.027355392579593747 0.13399227229218344" quat="0.5213338044737443 -0.5213338044734501 -0.47771441710839807 0.477714417108123" material="{name}-silver" type="mesh" mesh="{name}-arm_link4.stl"  class="{childclass}-visual" />
                      <body name="{name}-right_arm_link5" pos="0.067612 -0.033219 -0.0845" quat="1.0 0.0 0.0 0.0">
                        <joint name="{name}-right_arm_joint5" type="hinge" ref="0.0" class="{childclass}-motor" axis="0.0 0.0 -1.0" />
                        <inertial pos="0.0035114951739801253 -0.00032438367383951644 0.05339769316683546" quat="1.0 0.0 0.0 0.0" mass="1.682735565009155" diaginertia="0.002208 0.002158 0.000703" />
                        <geom name="{name}-right_arm_link5_collision" pos="0.030052794300312463 -0.05494208160627965 -0.057241042913650286" quat="0.7781655406314117 5.330121110899127e-14 3.1363692581466355e-13 -0.6280592260080435" type="mesh" mesh="{name}-arm_link5.stl"  class="{childclass}-collision" />
                        <geom name="{name}-right_arm_link5_visual" pos="0.030052794300312463 -0.05494208160627965 -0.057241042913650286" quat="0.7781655406314117 5.330121110899127e-14 3.1363692581466355e-13 -0.6280592260080435" material="{name}-silver" type="mesh" mesh="{name}-arm_link5.stl"  class="{childclass}-visual" />
                        <body name="{name}-right_arm_link6" pos="0.02884 -0.002523 0.0845" quat="1.0 0.0 0.0 0.0">
                          <joint name="{name}-right_arm_joint6" type="hinge" ref="0.0" class="{childclass}-motor" axis="-0.996195 0.087156 0.0" />
                          <inertial pos="0.04606151123037028 -0.00403375833742786 -0.02029844922950161" quat="1.0 0.0 0.0 0.0" mass="1.6175866280512115" diaginertia="0.002554 0.002684 0.001423" />
                          <geom name="{name}-right_arm_link6_collision" pos="0.07015096496844125 -0.0940377631493199 0.017299995001154284" quat="2.077741045466414e-13 -0.7372773368101248 -0.6755902076156596 -1.9444558750972757e-13" type="mesh" mesh="{name}-arm_link6.stl"  class="{childclass}-collision" />
                          <geom name="{name}-right_arm_link6_visual" pos="0.07015096496844125 -0.0940377631493199 0.017299995001154284" quat="2.077741045466414e-13 -0.7372773368101248 -0.6755902076156596 -1.9444558750972757e-13" material="{name}-silver" type="mesh" mesh="{name}-arm_link6.stl"  class="{childclass}-visual" />
                          <body name="{name}-right_arm_left_catch" pos="0.067534 -0.091232 -0.005" quat="1.0 0.0 0.0 0.0">
                            <joint name="{name}-right_catch_joint1" type="slide" ref="0.0" class="{childclass}-motor" range="-0.0445 0.0" axis="0.087156 0.996195 0.0" />
                            <inertial pos="0.022696371000088422 0.06755851746973854 0.008381661910845134" quat="1.0 0.0 0.0 0.0" mass="0.25047156301061513" diaginertia="9.7e-05 0.000157 0.000137" />
                            <geom name="{name}-right_arm_left_catch_collision" pos="-0.2827978086885289 -0.2179220999653169 -0.13086553021673955" quat="0.5213338044737432 -0.521333804473451 -0.47771441710839885 0.47771441710812224" type="mesh" mesh="{name}-arm_left_catch.stl"  class="{childclass}-collision" />
                            <geom name="{name}-right_arm_left_catch_visual" pos="-0.2827978086885289 -0.2179220999653169 -0.13086553021673955" quat="0.5213338044737432 -0.521333804473451 -0.47771441710839885 0.47771441710812224" material="{name}-silver" type="mesh" mesh="{name}-arm_left_catch.stl"  class="{childclass}-visual" />
                          </body>
                          <body name="{name}-right_arm_right_catch" pos="0.08235 0.078122 -0.005" quat="1.0 0.0 0.0 0.0">
                            <joint name="{name}-right_catch_joint2" type="slide" ref="0.0" class="{childclass}-motor" range="0.0 0.0445" axis="0.087156 0.996195 0.0" />
                            <inertial pos="0.01062064996036352 -0.0704739510881078 0.0022902966101032707" quat="1.0 0.0 0.0 0.0" mass="0.2504715624632503" diaginertia="0.000107 0.000152 0.000137" />
                            <geom name="{name}-right_arm_right_catch_collision" pos="-0.3341410986133092 -0.4899139341993404 -0.028033322065217275" quat="0.5213338044737442 -0.5213338044734503 -0.4777144171083979 0.47771441710812296" type="mesh" mesh="{name}-arm_right_catch.stl"  class="{childclass}-collision" />
                            <geom name="{name}-right_arm_right_catch_visual" pos="-0.3341410986133092 -0.4899139341993404 -0.028033322065217275" quat="0.5213338044737442 -0.5213338044734503 -0.4777144171083979 0.47771441710812296" material="{name}-silver" type="mesh" mesh="{name}-arm_right_catch.stl"  class="{childclass}-visual" />
                          </body>
                        </body>
                      </body>
                    </body>
                  </body>
                </body>
              </body>
            </body>
          </body>
          <site name="{name}-base_link_site" pos="0 0 0" quat="1 0 0 0" />
          <camera name="{name}-front_camera" mode="track" fovy="90.0" quat="4.329780281177467e-17 4.329780281177466e-17 0.7071067811865475 0.7071067811865476" pos="0.0 2.0 0.5" />
          <camera name="{name}-side_camera" mode="track" fovy="90.0" quat="-0.5 -0.4999999999999999 0.5 0.5000000000000001" pos="-2.0 0.0 0.5" />
        </body>
    """

    right_actuator = """
    <actuator>
        <general name="right-fingers-norm" tendon="right-fingers"
          ctrllimited="true" ctrlrange="0 1"
          gainprm="-16.2 0 0"
          biasprm="17.8 -200 -12"
          dyntype="filter" dynprm="0.02"
        />
      </actuator>
    """

    left_actuator = """
        <actuator>
            <general name="left-fingers-norm" tendon="left-fingers"
              ctrllimited="true" ctrlrange="0 1"
              gainprm="-16.2 0 0"
              biasprm="17.8 -200 -12"
              dyntype="filter" dynprm="0.02"
            />
          </actuator>
        """

    _postamble = """
      <tendon>
        <fixed name="right-fingers" range="0.005 0.089">
          <joint joint="lift-right_catch_joint1" coef="-1"/>
          <joint joint="lift-right_catch_joint2" coef="+1"/>
        </fixed>
        <fixed name="left-fingers" range="0.005 0.089">
          <joint joint="lift-left_catch_joint1" coef="-1"/>
          <joint joint="lift-left_catch_joint2" coef="+1"/>
        </fixed>
      </tendon>
      
      <contact>
        <exclude body1="{name}" body2="{name}-wheel_1" />
        <exclude body1="{name}" body2="{name}-wheel_2" />
        <exclude body1="{name}" body2="{name}-wheel_3" />
        <exclude body1="{name}" body2="{name}-lift_1" />
        <exclude body1="{name}-h_base_link" body2="{name}-h_link1_1" />
        <exclude body1="{name}-h_link1_1" body2="{name}-h_link2_1" />
        <exclude body1="{name}-lift_1" body2="{name}-h_base_link" />
        <exclude body1="{name}-left_arm_link6" body2="{name}-left_arm_left_catch" />
        <exclude body1="{name}-left_arm_link6" body2="{name}-left_arm_right_catch" />
        <exclude body1="{name}-left_arm_link5" body2="{name}-left_arm_link6" />
        <exclude body1="{name}-left_arm_link4" body2="{name}-left_arm_link5" />
        <exclude body1="{name}-left_arm_link3" body2="{name}-left_arm_link4" />
        <exclude body1="{name}-left_arm_link2" body2="{name}-left_arm_link3" />
        <exclude body1="{name}-left_arm_link1" body2="{name}-left_arm_link2" />
        <exclude body1="{name}-left_arm_base_link" body2="{name}-left_arm_link1" />
        <exclude body1="{name}-lift_1" body2="{name}-left_arm_base_link" />
        <exclude body1="{name}-right_arm_link6" body2="{name}-right_arm_left_catch" />
        <exclude body1="{name}-right_arm_link6" body2="{name}-right_arm_right_catch" />
        <exclude body1="{name}-right_arm_link5" body2="{name}-right_arm_link6" />
        <exclude body1="{name}-right_arm_link4" body2="{name}-right_arm_link5" />
        <exclude body1="{name}-right_arm_link3" body2="{name}-right_arm_link4" />
        <exclude body1="{name}-right_arm_link2" body2="{name}-right_arm_link3" />
        <exclude body1="{name}-right_arm_link1" body2="{name}-right_arm_link2" />
        <exclude body1="{name}-right_arm_base_link" body2="{name}-right_arm_link1" />
        <exclude body1="{name}-lift_1" body2="{name}-right_arm_base_link" />
      </contact>

      <sensor>
        <framepos name="{name}-base_link_site_pos" objtype="site" objname="{name}-base_link_site" />
        <framequat name="{name}-base_link_site_quat" objtype="site" objname="{name}-base_link_site" />
        <framelinvel name="{name}-base_link_site_linvel" objtype="site" objname="{name}-base_link_site" />
        <frameangvel name="{name}-base_link_site_angvel" objtype="site" objname="{name}-base_link_site" />
        <velocimeter name="{name}-base_link_site_vel" site="{name}-base_link_site" />
      </sensor>
      """

    def _add_mocaps(self, right_hand, left_hand, head):
        self.template = self.template + self._mocaps_body

        actuators = ""

        if right_hand:
            actuators += self.right_actuator
        if left_hand:
            actuators += self.left_actuator
        if head:
            pass

        self._postamble = self._postamble + actuators + self._mocaps_equality

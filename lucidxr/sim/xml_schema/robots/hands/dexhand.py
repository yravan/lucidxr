from itertools import combinations

from lucidxr.sim.xml_schema.schema import Body


class DexHand(Body):
    """Shared contact policy; distal finger links remain mutually collidable."""

    side = "r"

    @property
    def self_collision_exclusions(self):
        bodies = [self.name]
        for finger in range(1, 6):
            bodies.extend(
                f"{self.name}-{self.side}_f_link{finger}_{part}" for part in (1, 2, 3, 4, "tip", "pad")
            )
            bodies.append(f"{self.name}-ts_wrapper_{self.side}_f_link{finger}_pad")
            bodies.extend(f"{self.name}-force{finger}_f{sensor}" for sensor in range(1, 8))
        distal_links = {f"{self.name}-{self.side}_f_link{finger}_4" for finger in range(1, 6)}
        return "\n".join(
            f'<exclude body1="{first}" body2="{second}"/>'
            for first, second in combinations(bodies, 2)
            if not (first in distal_links and second in distal_links)
        )


HAND_MODEL_JOINT_KEYS = [
    "wrist",
    "thumb-metacarpal",
    "thumb-phalanx-proximal",
    "thumb-phalanx-distal",
    "thumb-tip",
    "index-finger-metacarpal",
    "index-finger-phalanx-proximal",
    "index-finger-phalanx-intermediate",
    "index-finger-phalanx-distal",
    "index-finger-tip",
    "middle-finger-metacarpal",
    "middle-finger-phalanx-proximal",
    "middle-finger-phalanx-intermediate",
    "middle-finger-phalanx-distal",
    "middle-finger-tip",
    "ring-finger-metacarpal",
    "ring-finger-phalanx-proximal",
    "ring-finger-phalanx-intermediate",
    "ring-finger-phalanx-distal",
    "ring-finger-tip",
    "pinky-finger-metacarpal",
    "pinky-finger-phalanx-proximal",
    "pinky-finger-phalanx-intermediate",
    "pinky-finger-phalanx-distal",
    "pinky-finger-tip",
]
ACTIVE_JOINTS = [
    "wrist",
    "thumb-tip",
    "index-finger-tip",
    "middle-finger-tip",
    "ring-finger-tip",
    "pinky-finger-tip",
    # 'thumb-metacarpal',
    "index-finger-metacarpal",
    "middle-finger-metacarpal",
    "ring-finger-metacarpal",
    "pinky-finger-metacarpal",
]


class DexHandLeft(DexHand):
    side = "l"
    assets: str = "robots/dexhand"
    forearm_body: bool = False
    show_mocap: bool = True
    site_alpha: float = 0.0
    default_pos = [0, 0, 0]

    _attributes = {
        "name": "left_hand_base",
        "pos": "0 0 0",
        "quat": "1 0 0 0",
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

        self.pos_wrist = self._pos + [0, 0, 0] - self.default_pos
        self.pos_index = self._pos + [0.0030, -0.0349, 0.2844] - self.default_pos
        self.quat_index = [-0.5, 0.5, 0.5, 0.5]
        self.pos_middle = self._pos + [0.0030, -0.0106, 0.2934] - self.default_pos
        self.quat_middle = [-0.5, 0.5, 0.5, 0.5]
        self.pos_ring = self._pos + [0.0030, 0.0137, 0.2844] - self.default_pos
        self.quat_ring = [0.5, -0.5, -0.5, -0.5]
        self.pos_pinky = self._pos + [0.0030, 0.0380, 0.2704] - self.default_pos
        self.quat_pinky = [0.5, -0.5, -0.5, -0.5]
        self.pos_thumb = self._pos + [0.0596, -0.1311, 0.1252] - self.default_pos
        self.quat_thumb = [0.655448, 0.441109, -0.417551, -0.448845]
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
      <default>
        <joint damping="1"/>
        <geom condim="3" solref="0.01 0.9" solimp="0.9 0.999 0.005" friction="3. 2. 2."/>
      </default>
      <size njmax="1000" nconmax="1000"/>
      <compiler angle="radian" meshdir="assets"/>
      <asset>
        <mesh name="{name}-left_hand_base" file="robots/dexhand/meshes/dexhand021_simplified/left_hand_base.STL"/>
        <mesh name="{name}-l_f_link1_1" file="robots/dexhand/meshes/dexhand021_simplified/l_f_link1_1.STL"/>
        <mesh name="{name}-l_f_link1_2" file="robots/dexhand/meshes/dexhand021_simplified/l_f_link1_2.STL"/>
        <mesh name="{name}-l_f_link1_3" file="robots/dexhand/meshes/dexhand021_simplified/l_f_link1_3.STL"/>
        <mesh name="{name}-l_f_link1_4" file="robots/dexhand/meshes/dexhand021_simplified/l_f_link1_4.STL"/>
        <mesh name="{name}-l_f_link2_1" file="robots/dexhand/meshes/dexhand021_simplified/l_f_link2_1.STL"/>
        <mesh name="{name}-l_f_link2_2" file="robots/dexhand/meshes/dexhand021_simplified/l_f_link2_2.STL"/>
        <mesh name="{name}-l_f_link2_3" file="robots/dexhand/meshes/dexhand021_simplified/l_f_link2_3.STL"/>
        <mesh name="{name}-l_f_link2_4" file="robots/dexhand/meshes/dexhand021_simplified/l_f_link2_4.STL"/>
        <mesh name="{name}-l_f_link3_1" file="robots/dexhand/meshes/dexhand021_simplified/l_f_link3_1.STL"/>
        <mesh name="{name}-l_f_link3_2" file="robots/dexhand/meshes/dexhand021_simplified/l_f_link3_2.STL"/>
        <mesh name="{name}-l_f_link3_3" file="robots/dexhand/meshes/dexhand021_simplified/l_f_link3_3.STL"/>
        <mesh name="{name}-l_f_link3_4" file="robots/dexhand/meshes/dexhand021_simplified/l_f_link3_4.STL"/>
        <mesh name="{name}-l_f_link4_1" file="robots/dexhand/meshes/dexhand021_simplified/l_f_link4_1.STL"/>
        <mesh name="{name}-l_f_link4_2" file="robots/dexhand/meshes/dexhand021_simplified/l_f_link4_2.STL"/>
        <mesh name="{name}-l_f_link4_3" file="robots/dexhand/meshes/dexhand021_simplified/l_f_link4_3.STL"/>
        <mesh name="{name}-l_f_link4_4" file="robots/dexhand/meshes/dexhand021_simplified/l_f_link4_4.STL"/>
        <mesh name="{name}-l_f_link5_1" file="robots/dexhand/meshes/dexhand021_simplified/l_f_link5_1.STL"/>
        <mesh name="{name}-l_f_link5_2" file="robots/dexhand/meshes/dexhand021_simplified/l_f_link5_2.STL"/>
        <mesh name="{name}-l_f_link5_3" file="robots/dexhand/meshes/dexhand021_simplified/l_f_link5_3.STL"/>
        <mesh name="{name}-l_f_link5_4" file="robots/dexhand/meshes/dexhand021_simplified/l_f_link5_4.STL"/>
        <mesh name="{name}-f1" file="robots/dexhand/meshes/dexhand021_simplified/F1b.stl" scale=".001 .001 .001"/>
        <mesh name="{name}-f2" file="robots/dexhand/meshes/dexhand021_simplified/F2b.stl" scale=".001 .001 .001"/>
        <mesh name="{name}-f3" file="robots/dexhand/meshes/dexhand021_simplified/F3b.stl" scale=".001 .001 .001"/>
        <mesh name="{name}-f4" file="robots/dexhand/meshes/dexhand021_simplified/F4b.stl" scale=".001 .001 .001"/>
        <mesh name="{name}-f5" file="robots/dexhand/meshes/dexhand021_simplified/F5b.stl" scale=".001 .001 .001"/>
        <mesh name="{name}-f6" file="robots/dexhand/meshes/dexhand021_simplified/F6b.stl" scale=".001 .001 .001"/>
        <mesh name="{name}-f7" file="robots/dexhand/meshes/dexhand021_simplified/F7b.stl" scale=".001 .001 .001"/>
      </asset>
    """
    wrist_mount = ""
    forearm_xml = ""

    _children_raw = """
          <freejoint name="{name}-left-floating_base"/>
          <site name="{name}" size="0.01" rgba="0 1 1 0.5"/>
          <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.75294 0.75294 0.75294 1" mesh="{name}-left_hand_base"/>
          <geom type="mesh" rgba="0.75294 0.75294 0.75294 1" mesh="{name}-left_hand_base" contype="0" conaffinity="0" group="1" density="0"/>
          <body name="{name}-l_f_link1_1" pos="0.032783 -0.023781 0.11211" quat="0.775383 -0.151562 0.0221299 -0.612635">
            <inertial pos="0.00198057 -0.000351992 -0.0134513" quat="0.716547 0.0775675 0.0530798 0.691178" mass="0.00440965" diaginertia="4.39524e-07 3.79859e-07 1.98262e-07"/>
            <joint name="{name}-l_f_joint1_1" pos="0 0 0" axis="0 0 1" range="0 2.2" actuatorfrcrange="-10 10" limited="true"/>
            <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link1_1"/>
            <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link1_1" contype="0" conaffinity="0" group="1" density="0"/>
            <body name="{name}-l_f_link1_2" pos="0.0083307 0 0" quat="0.707105 0.707108 0 0">
              <inertial pos="0.021435 0.000179938 0.0012982" quat="0.016958 0.707385 -0.0126923 0.706511" mass="0.00995163" diaginertia="1.70991e-06 1.65549e-06 6.19029e-07"/>
              <joint name="{name}-l_f_joint1_2" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
              <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link1_2"/>
              <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link1_2" contype="0" conaffinity="0" group="1" density="0"/>
              <body name="{name}-l_f_link1_3" pos="0.043 0 0">
                <inertial pos="0.0134587 -0.000699415 0.00129313" quat="0.0207134 0.706891 -0.0204889 0.706722" mass="0.00457275" diaginertia="3.79726e-07 3.56511e-07 2.03184e-07"/>
                <joint name="{name}-l_f_joint1_3" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
                <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link1_3"/>
                <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link1_3" contype="0" conaffinity="0" group="1" density="0"/>
                <body name="{name}-l_f_link1_4" pos="0.025 0 0">
                  <inertial pos="0.0197516 -0.00297416 0.00109866" quat="0.101158 0.716582 0.0177497 0.689901" mass="0.00815824" diaginertia="1.11886e-06 1.10162e-06 3.47e-07"/>
                  <joint name="{name}-l_f_joint1_4" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
                  <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link1_4"/>
                  <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link1_4" contype="0" conaffinity="0" group="1" density="0"/>
                  <geom size="0.002" pos="0.035 -0.004 0" contype="0" conaffinity="0" group="1" density="0" rgba="1 0 0 1"/>
                  <geom size="0.002" pos="0.035 -0.004 0" rgba="1 0 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  <geom size="0.006 0.0005 0.003" pos="0.026 0.0025 0.001" quat="0.974794 0 0 -0.223106" type="box" contype="0" conaffinity="0" group="1" density="0" rgba="0 1 0 1"/>
                  <geom size="0.006 0.0005 0.003" pos="0.026 0.0025 0.001" quat="0.974794 0 0 -0.223106" type="box" rgba="0 1 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  <body name="{name}-l_f_link1_tip" pos="0.035 -0.004 0" quat="1.0 0.0 0.0 0.0">
                    <geom name="{name}-geom_l_f_link1_tip" type="sphere" size="0.002" rgba="1 0 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                    <site name="{name}-site_l_f_link1_tip" size="0.0001" type="sphere" rgba="1 0 0 1"/>
                  </body>
                  <body name="{name}-l_f_link1_pad" pos="0.026 0.0025 0.001" quat="0.9747941070689433 0.0 0.0 -0.22310636213174545">
                    <geom name="{name}-geom_l_f_link1_pad" type="box" size="0.006 0.0005 0.003" rgba="0 1 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  </body>
                  <site name="{name}-site_l_f_link1_pad" pos="0.026 0.0025 0.001" quat="0.9747941070689433 0.0 0.0 -0.22310636213174545" type="box" size="0.006 0.0005 0.003" rgba="0 1 0 1"/>
                  <site name="{name}-site_l_f_link1_4" pos="0.0143 0.006 0" size="0.0001" type="sphere" rgba="1 0 0 1" zaxis="0.46 1 0"/>
                  <body name="{name}-ts_wrapper_l_f_link1_pad" pos="0.0425 -0.0188 -0.0055" quat="0.69101 -0.15003 -0.69101 -0.15003">
                    <body name="{name}-force1_f1" pos="0 0 0.02">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f1" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force1_f2" pos="0 0 0.0192">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f2" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force1_f3" pos="0.00545 0 0.02">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f3" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force1_f4" pos="0 0 0.02465">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f4" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force1_f5" pos="-0.0001 0 0.0285">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f5" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force1_f6" pos="0.0055 0 0.0285">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f6" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force1_f7" pos="0 0 0.01362">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f7" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                  </body>
                  <geom name="{name}-col_l_f_link1_4" type="capsule" contype="1" conaffinity="1" group="3" size="0.0095" fromto="0.0 0 0.001 0.027 -0.007 0.001"/>
                </body>
                <geom name="{name}-col_l_f_link1_3" type="capsule" contype="1" conaffinity="1" group="3" size="0.007" fromto="0.0125 0.003 -0.002 0.0125 0.003 0.0042"/>
              </body>
              <geom name="{name}-col_l_f_link1_2" type="capsule" contype="1" conaffinity="1" group="3" size="0.0095" fromto="0.0 0 0 0.03 0 0.002"/>
            </body>
          </body>
          <body name="{name}-l_f_link2_1" pos="0.006966 -0.034912 0.1644" quat="-2.59734e-06 0.707105 2.59735e-06 0.707108">
            <inertial pos="0.00700212 1.08537e-07 -0.00096856" quat="0.370763 0.602117 0.602108 0.370749" mass="0.00409701" diaginertia="3.18122e-07 2.71723e-07 2.04204e-07"/>
            <joint name="{name}-l_f_joint2_1" pos="0 0 0" axis="0 0 1" range="0 0.3" actuatorfrcrange="-10 10" limited="true"/>
            <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.792157 0.819608 0.933333 1" mesh="{name}-l_f_link2_1"/>
            <geom type="mesh" rgba="0.792157 0.819608 0.933333 1" mesh="{name}-l_f_link2_1" contype="0" conaffinity="0" group="1" density="0"/>
            <body name="{name}-l_f_link2_2" pos="0.017 0 0" quat="0.707105 0.707108 0 0">
              <inertial pos="0.0211622 -0.000590378 2.72622e-06" quat="0.502474 0.508577 0.49194 0.496854" mass="0.0094283" diaginertia="1.65781e-06 1.64333e-06 5.5432e-07"/>
              <joint name="{name}-l_f_joint2_2" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
              <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link2_2"/>
              <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link2_2" contype="0" conaffinity="0" group="1" density="0"/>
              <body name="{name}-l_f_link2_3" pos="0.043 0 0">
                <inertial pos="0.0134587 -0.000699415 7.12893e-07" quat="0.0207134 0.706891 -0.0204889 0.706722" mass="0.00457275" diaginertia="3.79726e-07 3.56511e-07 2.03184e-07"/>
                <joint name="{name}-l_f_joint2_3" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
                <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link2_3"/>
                <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link2_3" contype="0" conaffinity="0" group="1" density="0"/>
                <body name="{name}-l_f_link2_4" pos="0.025 0 0">
                  <inertial pos="0.0197516 -0.00297416 5.40083e-07" quat="0.0429662 0.705803 -0.0424926 0.705826" mass="0.00815824" diaginertia="1.11778e-06 1.10066e-06 3.46138e-07"/>
                  <joint name="{name}-l_f_joint2_4" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
                  <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link2_4"/>
                  <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link2_4" contype="0" conaffinity="0" group="1" density="0"/>
                  <geom size="0.002" pos="0.035 -0.004 0" contype="0" conaffinity="0" group="1" density="0" rgba="1 0 0 1"/>
                  <geom size="0.002" pos="0.035 -0.004 0" rgba="1 0 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  <geom size="0.006 0.0005 0.003" pos="0.026 0.0025 0" quat="0.974794 0 0 -0.223106" type="box" contype="0" conaffinity="0" group="1" density="0" rgba="0 1 0 1"/>
                  <geom size="0.006 0.0005 0.003" pos="0.026 0.0025 0" quat="0.974794 0 0 -0.223106" type="box" rgba="0 1 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  <body name="{name}-l_f_link2_tip" pos="0.035 -0.004 0" quat="1.0 0.0 0.0 0.0">
                    <geom name="{name}-geom_l_f_link2_tip" type="sphere" size="0.002" rgba="1 0 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                    <site name="{name}-site_l_f_link2_tip" size="0.002" type="sphere" rgba="1 0 0 1"/>
                  </body>
                  <body name="{name}-l_f_link2_pad" pos="0.026 0.0025 0.000" quat="0.9747941070689433 0.0 0.0 -0.22310636213174545">
                    <geom name="{name}-geom_l_f_link2_pad" type="box" size="0.006 0.0005 0.003" rgba="0 1 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  </body>
                  <site name="{name}-site_l_f_link2_pad" pos="0.026 0.0025 0.000" quat="0.9747941070689433 0.0 0.0 -0.22310636213174545" type="box" size="0.006 0.0005 0.003" rgba="0 1 0 1"/>
                  <site name="{name}-site_l_f_link2_4" pos="0.0143 0.006 0" size="0.0001" type="sphere" rgba="1 0 0 1" zaxis="0.46 1 0"/>
                  <body name="{name}-ts_wrapper_l_f_link2_pad" pos="0.0425 -0.0188 -0.0055" quat="0.69101 -0.15003 -0.69101 -0.15003">
                    <body name="{name}-force2_f1" pos="0 0 0.02">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f1" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force2_f2" pos="0 0 0.0192">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f2" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force2_f3" pos="0.00545 0 0.02">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f3" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force2_f4" pos="0 0 0.02465">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f4" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force2_f5" pos="-0.0001 0 0.0285">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f5" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force2_f6" pos="0.0055 0 0.0285">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f6" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force2_f7" pos="0 0 0.01362">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f7" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                  </body>
                  <geom name="{name}-col_l_f_link2_4" type="capsule" contype="1" conaffinity="1" group="3" size="0.0095" fromto="0.0 0 0 0.026 -0.007 0"/>
                </body>
                <geom name="{name}-col_l_f_link2_3" type="capsule" contype="1" conaffinity="1" group="3" size="0.007" fromto="0.012 0.003 -0.0035 0.012 0.003 0.0035"/>
              </body>
              <geom name="{name}-col_l_f_link2_2" type="capsule" contype="1" conaffinity="1" group="3" size="0.0095" fromto="0.005 0 0 0.03 0 0"/>
            </body>
          </body>
          <body name="{name}-l_f_link3_1" pos="0.006966 -0.010612 0.1734" quat="-2.59734e-06 0.707105 2.59735e-06 0.707108">
            <inertial pos="0.00700212 1.07469e-07 -0.000968557" quat="0.370763 0.602117 0.602109 0.370749" mass="0.00409701" diaginertia="3.18122e-07 2.71723e-07 2.04204e-07"/>
            <joint name="{name}-l_f_joint3_1" pos="0 0 0" axis="0 0 1" range="-0.001 0.001" actuatorfrcrange="-10 10" limited="true"/>
            <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.792157 0.819608 0.933333 1" mesh="{name}-l_f_link3_1"/>
            <geom type="mesh" rgba="0.792157 0.819608 0.933333 1" mesh="{name}-l_f_link3_1" contype="0" conaffinity="0" group="1" density="0"/>
            <body name="{name}-l_f_link3_2" pos="0.017 0 0" quat="0.707105 0.707108 0 0">
              <inertial pos="0.0211622 -0.000590378 2.72622e-06" quat="0.502474 0.508577 0.49194 0.496854" mass="0.0094283" diaginertia="1.65781e-06 1.64333e-06 5.5432e-07"/>
              <joint name="{name}-l_f_joint3_2" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
              <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link3_2"/>
              <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link3_2" contype="0" conaffinity="0" group="1" density="0"/>
              <body name="{name}-l_f_link3_3" pos="0.043 0 0">
                <inertial pos="0.0134587 -0.000699415 7.12894e-07" quat="0.0207134 0.706891 -0.0204889 0.706722" mass="0.00457275" diaginertia="3.79726e-07 3.56511e-07 2.03184e-07"/>
                <joint name="{name}-l_f_joint3_3" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
                <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link3_3"/>
                <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link3_3" contype="0" conaffinity="0" group="1" density="0"/>
                <body name="{name}-l_f_link3_4" pos="0.025 0 0">
                  <inertial pos="0.0197516 -0.00297416 5.40083e-07" quat="0.0429662 0.705803 -0.0424926 0.705826" mass="0.00815824" diaginertia="1.11778e-06 1.10066e-06 3.46138e-07"/>
                  <joint name="{name}-l_f_joint3_4" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
                  <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link3_4"/>
                  <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link3_4" contype="0" conaffinity="0" group="1" density="0"/>
                  <geom size="0.002" pos="0.035 -0.004 0" contype="0" conaffinity="0" group="1" density="0" rgba="1 0 0 1"/>
                  <geom size="0.002" pos="0.035 -0.004 0" rgba="1 0 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  <geom size="0.006 0.0005 0.003" pos="0.026 0.0025 0" quat="0.974794 0 0 -0.223106" type="box" contype="0" conaffinity="0" group="1" density="0" rgba="0 1 0 1"/>
                  <geom size="0.006 0.0005 0.003" pos="0.026 0.0025 0" quat="0.974794 0 0 -0.223106" type="box" rgba="0 1 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  <body name="{name}-l_f_link3_tip" pos="0.035 -0.004 0" quat="1.0 0.0 0.0 0.0">
                    <geom name="{name}-geom_l_f_link3_tip" type="sphere" size="0.002" rgba="1 0 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                    <site name="{name}-site_l_f_link3_tip" size="0.002" type="sphere" rgba="1 0 0 1"/>
                  </body>
                  <body name="{name}-l_f_link3_pad" pos="0.026 0.0025 0.000" quat="0.9747941070689433 0.0 0.0 -0.22310636213174545">
                    <geom name="{name}-geom_l_f_link3_pad" type="box" size="0.006 0.0005 0.003" rgba="0 1 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  </body>
                  <site name="{name}-site_l_f_link3_pad" pos="0.026 0.0025 0.000" quat="0.9747941070689433 0.0 0.0 -0.22310636213174545" type="box" size="0.006 0.0005 0.003" rgba="0 1 0 1"/>
                  <site name="{name}-site_l_f_link3_4" pos="0.0143 0.006 0" size="0.0001" type="sphere" rgba="1 0 0 1" zaxis="0.46 1 0"/>
                  <body name="{name}-ts_wrapper_l_f_link3_pad" pos="0.0425 -0.0188 -0.0055" quat="0.69101 -0.15003 -0.69101 -0.15003">
                    <body name="{name}-force3_f1" pos="0 0 0.02">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f1" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force3_f2" pos="0 0 0.0192">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f2" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force3_f3" pos="0.00545 0 0.02">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f3" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force3_f4" pos="0 0 0.02465">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f4" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force3_f5" pos="-0.0001 0 0.0285">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f5" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force3_f6" pos="0.0055 0 0.0285">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f6" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force3_f7" pos="0 0 0.01362">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f7" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                  </body>
                  <geom name="{name}-col_l_f_link3_4" type="capsule" contype="1" conaffinity="1" group="3" size="0.0095" fromto="0.0 0 0 0.026 -0.007 0"/>
                </body>
                <geom name="{name}-col_l_f_link3_3" type="capsule" contype="1" conaffinity="1" group="3" size="0.007" fromto="0.012 0.003 -0.0035 0.012 0.003 0.0035"/>
              </body>
              <geom name="{name}-col_l_f_link3_2" type="capsule" contype="1" conaffinity="1" group="3" size="0.0095" fromto="0.005 0 0 0.03 0 0"/>
            </body>
          </body>
          <body name="{name}-l_f_link4_1" pos="0.006966 0.013688 0.1644" quat="0.707105 0 -0.707108 0">
            <inertial pos="0.00700212 -1.07487e-07 0.000968558" quat="0.602109 0.370749 0.370763 0.602117" mass="0.00409701" diaginertia="3.18122e-07 2.71723e-07 2.04204e-07"/>
            <joint name="{name}-l_f_joint4_1" pos="0 0 0" axis="0 0 1" range="0 0.3" actuatorfrcrange="-10 10" limited="true"/>
            <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.792157 0.819608 0.933333 1" mesh="{name}-l_f_link4_1"/>
            <geom type="mesh" rgba="0.792157 0.819608 0.933333 1" mesh="{name}-l_f_link4_1" contype="0" conaffinity="0" group="1" density="0"/>
            <body name="{name}-l_f_link4_2" pos="0.017 0 0" quat="0.707105 -0.707108 0 0">
              <inertial pos="0.0211622 -0.000590378 2.72622e-06" quat="0.502474 0.508577 0.49194 0.496854" mass="0.0094283" diaginertia="1.65781e-06 1.64333e-06 5.5432e-07"/>
              <joint name="{name}-l_f_joint4_2" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
              <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link4_2"/>
              <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link4_2" contype="0" conaffinity="0" group="1" density="0"/>
              <body name="{name}-l_f_link4_3" pos="0.043 0 0">
                <inertial pos="0.0134587 -0.000699415 7.12894e-07" quat="0.0207134 0.706891 -0.0204889 0.706722" mass="0.00457275" diaginertia="3.79726e-07 3.56511e-07 2.03184e-07"/>
                <joint name="{name}-l_f_joint4_3" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
                <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link4_3"/>
                <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link4_3" contype="0" conaffinity="0" group="1" density="0"/>
                <body name="{name}-l_f_link4_4" pos="0.025 0 0">
                  <inertial pos="0.0197516 -0.00297416 5.40083e-07" quat="0.0429662 0.705803 -0.0424926 0.705826" mass="0.00815824" diaginertia="1.11778e-06 1.10066e-06 3.46138e-07"/>
                  <joint name="{name}-l_f_joint4_4" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
                  <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link4_4"/>
                  <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link4_4" contype="0" conaffinity="0" group="1" density="0"/>
                  <geom size="0.002" pos="0.035 -0.004 0" contype="0" conaffinity="0" group="1" density="0" rgba="1 0 0 1"/>
                  <geom size="0.002" pos="0.035 -0.004 0" rgba="1 0 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  <geom size="0.006 0.0005 0.003" pos="0.026 0.0025 0" quat="0.974794 0 0 -0.223106" type="box" contype="0" conaffinity="0" group="1" density="0" rgba="0 1 0 1"/>
                  <geom size="0.006 0.0005 0.003" pos="0.026 0.0025 0" quat="0.974794 0 0 -0.223106" type="box" rgba="0 1 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  <body name="{name}-l_f_link4_tip" pos="0.035 -0.004 0" quat="1.0 0.0 0.0 0.0">
                    <geom name="{name}-geom_l_f_link4_tip" type="sphere" size="0.002" rgba="1 0 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                    <site name="{name}-site_l_f_link4_tip" size="0.002" type="sphere" rgba="1 0 0 1"/>
                  </body>
                  <body name="{name}-l_f_link4_pad" pos="0.026 0.0025 0.000" quat="0.9747941070689433 0.0 0.0 -0.22310636213174545">
                    <geom name="{name}-geom_l_f_link4_pad" type="box" size="0.006 0.0005 0.003" rgba="0 1 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  </body>
                  <site name="{name}-site_l_f_link4_pad" pos="0.026 0.0025 0.000" quat="0.9747941070689433 0.0 0.0 -0.22310636213174545" type="box" size="0.006 0.0005 0.003" rgba="0 1 0 1"/>
                  <site name="{name}-site_l_f_link4_4" pos="0.0143 0.006 0" size="0.0001" type="sphere" rgba="1 0 0 1" zaxis="0.46 1 0"/>
                  <body name="{name}-ts_wrapper_l_f_link4_pad" pos="0.0425 -0.0188 -0.0055" quat="0.69101 -0.15003 -0.69101 -0.15003">
                    <body name="{name}-force4_f1" pos="0 0 0.02">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f1" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force4_f2" pos="0 0 0.0192">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f2" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force4_f3" pos="0.00545 0 0.02">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f3" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force4_f4" pos="0 0 0.02465">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f4" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force4_f5" pos="-0.0001 0 0.0285">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f5" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force4_f6" pos="0.0055 0 0.0285">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f6" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force4_f7" pos="0 0 0.01362">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f7" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                  </body>
                  <geom name="{name}-col_l_f_link4_4" type="capsule" contype="1" conaffinity="1" group="3" size="0.0095" fromto="0.0 0 0 0.026 -0.007 0"/>
                </body>
                <geom name="{name}-col_l_f_link4_3" type="capsule" contype="1" conaffinity="1" group="3" size="0.007" fromto="0.012 0.003 -0.0035 0.012 0.003 0.0035"/>
              </body>
              <geom name="{name}-col_l_f_link4_2" type="capsule" contype="1" conaffinity="1" group="3" size="0.0095" fromto="0.005 0 0 0.03 0 0"/>
            </body>
          </body>
          <body name="{name}-l_f_link5_1" pos="0.006966 0.037988 0.1504" quat="0.707105 0 -0.707108 0">
            <inertial pos="0.00700212 -1.08915e-07 0.000968551" quat="0.602109 0.370749 0.370763 0.602117" mass="0.00409701" diaginertia="3.18122e-07 2.71723e-07 2.04203e-07"/>
            <joint name="{name}-l_f_joint5_1" pos="0 0 0" axis="0 0 1" range="0 0.6" actuatorfrcrange="-10 10" limited="true"/>
            <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.792157 0.819608 0.933333 1" mesh="{name}-l_f_link5_1"/>
            <geom type="mesh" rgba="0.792157 0.819608 0.933333 1" mesh="{name}-l_f_link5_1" contype="0" conaffinity="0" group="1" density="0"/>
            <body name="{name}-l_f_link5_2" pos="0.017 0 0" quat="0.707105 -0.707108 0 0">
              <inertial pos="0.0211622 -0.000590378 2.72622e-06" quat="0.502474 0.508577 0.49194 0.496854" mass="0.0094283" diaginertia="1.65781e-06 1.64333e-06 5.5432e-07"/>
              <joint name="{name}-l_f_joint5_2" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
              <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link5_2"/>
              <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link5_2" contype="0" conaffinity="0" group="1" density="0"/>
              <body name="{name}-l_f_link5_3" pos="0.043 0 0">
                <inertial pos="0.0134587 -0.000699415 7.12894e-07" quat="0.0207134 0.706891 -0.0204889 0.706722" mass="0.00457275" diaginertia="3.79726e-07 3.56511e-07 2.03184e-07"/>
                <joint name="{name}-l_f_joint5_3" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
                <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link5_3"/>
                <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link5_3" contype="0" conaffinity="0" group="1" density="0"/>
                <body name="{name}-l_f_link5_4" pos="0.025 0 0">
                  <inertial pos="0.0197516 -0.00297416 5.40083e-07" quat="0.0429662 0.705803 -0.0424926 0.705826" mass="0.00815824" diaginertia="1.11778e-06 1.10066e-06 3.46138e-07"/>
                  <joint name="{name}-l_f_joint5_4" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
                  <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link5_4"/>
                  <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-l_f_link5_4" contype="0" conaffinity="0" group="1" density="0"/>
                  <geom size="0.002" pos="0.035 -0.004 0" contype="0" conaffinity="0" group="1" density="0" rgba="1 0 0 1"/>
                  <geom size="0.002" pos="0.035 -0.004 0" rgba="1 0 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  <geom size="0.006 0.0005 0.003" pos="0.026 0.0025 0" quat="0.974794 0 0 -0.223106" type="box" contype="0" conaffinity="0" group="1" density="0" rgba="0 1 0 1"/>
                  <geom size="0.006 0.0005 0.003" pos="0.026 0.0025 0" quat="0.974794 0 0 -0.223106" type="box" rgba="0 1 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  <body name="{name}-l_f_link5_tip" pos="0.035 -0.004 0" quat="1.0 0.0 0.0 0.0">
                    <geom name="{name}-geom_l_f_link5_tip" type="sphere" size="0.002" rgba="1 0 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                    <site name="{name}-site_l_f_link5_tip" size="0.002" type="sphere" rgba="1 0 0 1"/>
                  </body>
                  <body name="{name}-l_f_link5_pad" pos="0.026 0.0025 0.000" quat="0.9747941070689433 0.0 0.0 -0.22310636213174545">
                    <geom name="{name}-geom_l_f_link5_pad" type="box" size="0.006 0.0005 0.003" rgba="0 1 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  </body>
                  <site name="{name}-site_l_f_link5_pad" pos="0.026 0.0025 0.000" quat="0.9747941070689433 0.0 0.0 -0.22310636213174545" type="box" size="0.006 0.0005 0.003" rgba="0 1 0 1"/>
                  <site name="{name}-site_l_f_link5_4" pos="0.0143 0.006 0" size="0.0001" type="sphere" rgba="1 0 0 1" zaxis="0.46 1 0"/>
                  <body name="{name}-ts_wrapper_l_f_link5_pad" pos="0.0425 -0.0188 -0.0055" quat="0.69101 -0.15003 -0.69101 -0.15003">
                    <body name="{name}-force5_f1" pos="0 0 0.02">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f1" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force5_f2" pos="0 0 0.0192">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f2" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force5_f3" pos="0.00545 0 0.02">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f3" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force5_f4" pos="0 0 0.02465">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f4" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force5_f5" pos="-0.0001 0 0.0285">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f5" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force5_f6" pos="0.0055 0 0.0285">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f6" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force5_f7" pos="0 0 0.01362">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f7" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                  </body>
                  <geom name="{name}-col_l_f_link5_4" type="capsule" contype="1" conaffinity="1" group="3" size="0.0095" fromto="0.0 0 0 0.026 -0.007 0"/>
                </body>
                <geom name="{name}-col_l_f_link5_3" type="capsule" contype="1" conaffinity="1" group="3" size="0.007" fromto="0.012 0.003 -0.0035 0.012 0.003 0.0035"/>
              </body>
              <geom name="{name}-col_l_f_link5_2" type="capsule" contype="1" conaffinity="1" group="3" size="0.0095" fromto="0.005 0 0 0.03 0 0"/>
            </body>
          </body>
          <geom name="{name}-col_left_hand_base" type="box" contype="1" conaffinity="1" group="3" size="0.0273 0.05 0.05" pos="-0.0022 0 0.11"/>
        """

    _postamble = """
      <actuator>
        <position name="{name}-act_l_f_joint1_2" joint="{name}-l_f_joint1_2" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>
        <position name="{name}-act_l_f_joint1_3" joint="{name}-l_f_joint1_3" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>
        <position name="{name}-act_l_f_joint1_4" joint="{name}-l_f_joint1_4" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>
        <position name="{name}-act_l_f_joint2_2" joint="{name}-l_f_joint2_2" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>
        <position name="{name}-act_l_f_joint2_3" joint="{name}-l_f_joint2_3" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>
        <position name="{name}-act_l_f_joint2_4" joint="{name}-l_f_joint2_4" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>
        <position name="{name}-act_l_f_joint3_2" joint="{name}-l_f_joint3_2" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>
        <position name="{name}-act_l_f_joint3_3" joint="{name}-l_f_joint3_3" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>
        <position name="{name}-act_l_f_joint3_4" joint="{name}-l_f_joint3_4" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>
        <position name="{name}-act_l_f_joint4_2" joint="{name}-l_f_joint4_2" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>
        <position name="{name}-act_l_f_joint4_3" joint="{name}-l_f_joint4_3" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>
        <position name="{name}-act_l_f_joint4_4" joint="{name}-l_f_joint4_4" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>
        <position name="{name}-act_l_f_joint5_2" joint="{name}-l_f_joint5_2" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>
        <position name="{name}-act_l_f_joint5_3" joint="{name}-l_f_joint5_3" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>
        <position name="{name}-act_l_f_joint5_4" joint="{name}-l_f_joint5_4" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>
        <position name="{name}-act_l_f_joint1_1" joint="{name}-l_f_joint1_1" kp="1000" kv="50" ctrlrange="0 2.2" forcerange="-200 200" forcelimited="true"/>
        <position name="{name}-act_l_f_joint2_1" joint="{name}-l_f_joint2_1" kp="1000" kv="50" ctrlrange="0 0.3" forcerange="-200 200" forcelimited="true"/>
        <position name="{name}-act_l_f_joint3_1" joint="{name}-l_f_joint3_1" kp="1000" kv="50" ctrlrange="-0.0001 0.0001" forcerange="-200 200" forcelimited="true"/>
        <position name="{name}-act_l_f_joint4_1" joint="{name}-l_f_joint4_1" kp="1000" kv="50" ctrlrange="0 0.3" forcerange="-200 200" forcelimited="true"/>
        <position name="{name}-act_l_f_joint5_1" joint="{name}-l_f_joint5_1" kp="1000" kv="50" ctrlrange="0 0.6" forcerange="-200 200" forcelimited="true"/>
      </actuator>
      <sensor>
        <touch name="{name}-touch_l_f_link1_pad" site="{name}-site_l_f_link1_pad"/>
        <touch name="{name}-touch_l_f_link2_pad" site="{name}-site_l_f_link2_pad"/>
        <touch name="{name}-touch_l_f_link3_pad" site="{name}-site_l_f_link3_pad"/>
        <touch name="{name}-touch_l_f_link4_pad" site="{name}-site_l_f_link4_pad"/>
        <touch name="{name}-touch_l_f_link5_pad" site="{name}-site_l_f_link5_pad"/>
        <rangefinder name="{name}-rf1" site="{name}-site_l_f_link1_4" cutoff="0.1"/>
        <rangefinder name="{name}-rf2" site="{name}-site_l_f_link2_4" cutoff="0.1"/>
        <rangefinder name="{name}-rf3" site="{name}-site_l_f_link3_4" cutoff="0.1"/>
        <rangefinder name="{name}-rf4" site="{name}-site_l_f_link4_4" cutoff="0.1"/>
        <rangefinder name="{name}-rf5" site="{name}-site_l_f_link5_4" cutoff="0.1"/>
        <user name="{name}-TS-F-A-1" dim="11" noise="0.0"/>
        <user name="{name}-TS-F-A-2" dim="11" noise="0.0"/>
        <user name="{name}-TS-F-A-3" dim="11" noise="0.0"/>
        <user name="{name}-TS-F-A-4" dim="11" noise="0.0"/>
        <user name="{name}-TS-F-A-5" dim="11" noise="0.0"/>
      </sensor>
      <contact>
{self_collision_exclusions}
      </contact>
      <equality>
        <weld site1="{name}" site2="left-wrist-mocap-site"/>
        <weld site1="{name}-site_l_f_link2_tip" site2="left-index-finger-tip-mocap-site"/>
        <weld site1="{name}-site_l_f_link3_tip" site2="left-middle-finger-tip-mocap-site"/>
        <weld site1="{name}-site_l_f_link4_tip" site2="left-ring-finger-tip-mocap-site"/>
        <weld site1="{name}-site_l_f_link5_tip" site2="left-pinky-finger-tip-mocap-site"/>
        <weld site1="{name}-site_l_f_link1_tip" site2="left-thumb-tip-mocap-site"/>
      </equality>
    """


class DexHandRight(DexHand):
    assets: str = "robots/dexhand"
    forearm_body: bool = False
    show_mocap: bool = True
    site_alpha: float = 0.0
    default_pos = [0, 0, 0]

    _attributes = {
        "name": "right_hand_base",
        "pos": "0 0 0",
        "quat": "1 0 0 0",
    }

    JOINT_TO_SITE = {
        "wrist": "{name}",
        # Thumb (link1 chain)
        "thumb-metacarpal": "{name}-site_r_f_link1_1",
        "thumb-phalanx-proximal": "{name}-site_r_f_link1_2",
        "thumb-phalanx-intermediate": "{name}-site_r_f_link1_3",
        "thumb-phalanx-distal": "{name}-site_r_f_link1_4",
        "thumb-tip": "{name}-site_r_f_link1_tip",
        # Index finger (link2 chain)
        "index-finger-metacarpal": "{name}-site_r_f_link2_1",
        "index-finger-phalanx-proximal": "{name}-site_r_f_link2_2",
        "index-finger-phalanx-intermediate": "{name}-site_r_f_link2_3",
        "index-finger-phalanx-distal": "{name}-site_r_f_link2_4",
        "index-finger-tip": "{name}-site_r_f_link2_tip",
        # Middle finger (link3 chain)
        "middle-finger-metacarpal": "{name}-site_r_f_link3_1",
        "middle-finger-phalanx-proximal": "{name}-site_r_f_link3_2",
        "middle-finger-phalanx-intermediate": "{name}-site_r_f_link3_3",
        "middle-finger-phalanx-distal": "{name}-site_r_f_link3_4",
        "middle-finger-tip": "{name}-site_r_f_link3_tip",
        # Ring finger (link4 chain)
        "ring-finger-metacarpal": "{name}-site_r_f_link4_1",
        "ring-finger-phalanx-proximal": "{name}-site_r_f_link4_2",
        "ring-finger-phalanx-intermediate": "{name}-site_r_f_link4_3",
        "ring-finger-phalanx-distal": "{name}-site_r_f_link4_4",
        "ring-finger-tip": "{name}-site_r_f_link4_tip",
        # Pinky finger (link5 chain)
        "pinky-finger-metacarpal": "{name}-site_r_f_link5_1",
        "pinky-finger-phalanx-proximal": "{name}-site_r_f_link5_2",
        "pinky-finger-phalanx-intermediate": "{name}-site_r_f_link5_3",
        "pinky-finger-phalanx-distal": "{name}-site_r_f_link5_4",
        "pinky-finger-tip": "{name}-site_r_f_link5_tip",
    }
    _mocaps_raw = ""
    welds = ""

    def __init__(self, *_children, **kwargs):
        super().__init__(*_children, **kwargs)

        DEFAULT_JOINT_POS = {
            "wrist": [0.0, 0.0, 0.0],
            "thumb-metacarpal": [-0.023781, 0.112110, -0.032783],
            "thumb-phalanx-proximal": [-0.031751, 0.113371, -0.034852],
            "thumb-phalanx-intermediate": [-0.072892, 0.119881, -0.045532],
            "thumb-phalanx-distal": [-0.096811, 0.123665, -0.051742],
            "thumb-tip": [-0.131100, 0.125200, -0.059600],
            "index-finger-metacarpal": [-0.034912, 0.164400, -0.006966],
            "index-finger-phalanx-proximal": [-0.034912, 0.181400, -0.006966],
            "index-finger-phalanx-intermediate": [-0.034912, 0.224400, -0.006966],
            "index-finger-phalanx-distal": [-0.034912, 0.249400, -0.006966],
            "index-finger-tip": [-0.034900, 0.284400, -0.003000],
            "middle-finger-metacarpal": [-0.010612, 0.173400, -0.006966],
            "middle-finger-phalanx-proximal": [-0.010612, 0.190400, -0.006966],
            "middle-finger-phalanx-intermediate": [-0.010612, 0.233400, -0.006966],
            "middle-finger-phalanx-distal": [-0.010612, 0.258400, -0.006966],
            "middle-finger-tip": [-0.010600, 0.293400, -0.003000],
            "ring-finger-metacarpal": [0.013688, 0.164400, -0.006966],
            "ring-finger-phalanx-proximal": [0.013688, 0.181400, -0.006966],
            "ring-finger-phalanx-intermediate": [0.013688, 0.224400, -0.006966],
            "ring-finger-phalanx-distal": [0.013688, 0.249400, -0.006966],
            "ring-finger-tip": [0.013700, 0.284400, -0.003000],
            "pinky-finger-metacarpal": [0.037988, 0.150400, -0.006966],
            "pinky-finger-phalanx-proximal": [0.037988, 0.167400, -0.006966],
            "pinky-finger-phalanx-intermediate": [0.037988, 0.210400, -0.006966],
            "pinky-finger-phalanx-distal": [0.037988, 0.235400, -0.006966],
            "pinky-finger-tip": [0.038000, 0.270400, -0.003000],
        }

        DEFAULT_JOINT_QUAT = {
            "wrist": [-0.5, 0.5, -0.5, -0.5],
            "thumb-metacarpal": [0.5, -0.5, -0.5, 0.5],
            # "thumb-phalanx-proximal": [0.5, -0.5, -0.5, 0.5],
            # "thumb-phalanx-intermediate": [0.5, -0.5, -0.5, 0.5],
            # "thumb-phalanx-distal": [0.5, -0.5, -0.5, 0.5],
            "thumb-tip": [0, -0.7071, 0.7071, 0],
            "index-finger-metacarpal": [0.707, 0, 0, 0.707],
            # "index-finger-phalanx-proximal": [-0.5, 0.5, -0.5, -0.5],
            # "index-finger-phalanx-intermediate": [-0.5, 0.5, -0.5, -0.5],
            # "index-finger-phalanx-distal": [-0.5, 0.5, -0.5, -0.5],
            "index-finger-tip": [-0.5, 0.5, -0.5, -0.5],
            "middle-finger-metacarpal": [0.707, 0, 0, 0.707],
            # "middle-finger-phalanx-proximal": [-0.5, 0.5, -0.5, -0.5],
            # "middle-finger-phalanx-intermediate": [-0.5, 0.5, -0.5, -0.5],
            # "middle-finger-phalanx-distal": [-0.5, 0.5, -0.5, -0.5],
            "middle-finger-tip": [-0.5, 0.5, -0.5, -0.5],
            "ring-finger-metacarpal": [0, 0.707, 0.707, 0],
            # "ring-finger-phalanx-proximal": [-0.5, 0.5, -0.5, -0.5],
            # "ring-finger-phalanx-intermediate": [-0.5, 0.5, -0.5, -0.5],
            # "ring-finger-phalanx-distal": [-0.5, 0.5, -0.5, -0.5],
            "ring-finger-tip": [-0.5, 0.5, -0.5, -0.5],
            "pinky-finger-metacarpal": [0, 0.707, 0.707, 0],
            # "pinky-finger-phalanx-proximal": [-0.5, 0.5, -0.5, -0.5],
            # "pinky-finger-phalanx-intermediate": [-0.5, 0.5, -0.5, -0.5],
            # "pinky-finger-phalanx-distal": [-0.5, 0.5, -0.5, -0.5],
            "pinky-finger-tip": [-0.5, 0.5, -0.5, -0.5],
        }

        for joint in ACTIVE_JOINTS:
            pos = DEFAULT_JOINT_POS[joint]
            pos = self._pos + pos - self.default_pos
            pos_str = " ".join(f"{x:.2f}" for x in pos)
            quat = DEFAULT_JOINT_QUAT[joint]
            quat_str = " ".join(f"{x:.6f}" for x in quat)
            self._mocaps_raw += f"""
                <body mocap="true" name="right-{joint}" pos="{pos_str}">
                    <site name="right-{joint}-mocap-site" rgba="0 0 1 {{site_alpha}}" quat="{quat_str}"  size=".01"/> <!-- Blue -->
                </body>
            """
            self.welds += f'<weld site1="{self.JOINT_TO_SITE[joint]}" site2="right-{joint}-mocap-site" solref="0.003 1.5"/>\n'

        if self.show_mocap:
            self.site_alpha = 1.0
        else:
            self.site_alpha = 0

        if self.forearm_body:
            raise NotImplementedError("forearm_body is not implemented yet.")

        values = self._format_dict()
        self.welds = self.welds.format(**values)
        self._mocaps = self._mocaps_raw.format(**values)
        self._children_raw = self._children_raw.format(**values)

    _preamble = """
      <default>
        <joint damping="1"/>
        <geom condim="3" solref="0.01 0.9" solimp="0.9 0.999 0.005" friction="3. 2. 2."/>
      </default>
      <asset>
        <mesh name="{name}-right_hand_base" file="robots/dexhand/meshes/dexhand021_simplified/right_hand_base.STL"/>
        <mesh name="{name}-r_f_link1_1" file="robots/dexhand/meshes/dexhand021_simplified/r_f_link1_1.STL"/>
        <mesh name="{name}-r_f_link1_2" file="robots/dexhand/meshes/dexhand021_simplified/r_f_link1_2.STL"/>
        <mesh name="{name}-r_f_link1_3" file="robots/dexhand/meshes/dexhand021_simplified/r_f_link1_3.STL"/>
        <mesh name="{name}-r_f_link1_4" file="robots/dexhand/meshes/dexhand021_simplified/r_f_link1_4.STL"/>
        <mesh name="{name}-r_f_link2_1" file="robots/dexhand/meshes/dexhand021_simplified/r_f_link2_1.STL"/>
        <mesh name="{name}-r_f_link2_2" file="robots/dexhand/meshes/dexhand021_simplified/r_f_link2_2.STL"/>
        <mesh name="{name}-r_f_link2_3" file="robots/dexhand/meshes/dexhand021_simplified/r_f_link2_3.STL"/>
        <mesh name="{name}-r_f_link2_4" file="robots/dexhand/meshes/dexhand021_simplified/r_f_link2_4.STL"/>
        <mesh name="{name}-r_f_link3_1" file="robots/dexhand/meshes/dexhand021_simplified/r_f_link3_1.STL"/>
        <mesh name="{name}-r_f_link3_2" file="robots/dexhand/meshes/dexhand021_simplified/r_f_link3_2.STL"/>
        <mesh name="{name}-r_f_link3_3" file="robots/dexhand/meshes/dexhand021_simplified/r_f_link3_3.STL"/>
        <mesh name="{name}-r_f_link3_4" file="robots/dexhand/meshes/dexhand021_simplified/r_f_link3_4.STL"/>
        <mesh name="{name}-r_f_link4_1" file="robots/dexhand/meshes/dexhand021_simplified/r_f_link4_1.STL"/>
        <mesh name="{name}-r_f_link4_2" file="robots/dexhand/meshes/dexhand021_simplified/r_f_link4_2.STL"/>
        <mesh name="{name}-r_f_link4_3" file="robots/dexhand/meshes/dexhand021_simplified/r_f_link4_3.STL"/>
        <mesh name="{name}-r_f_link4_4" file="robots/dexhand/meshes/dexhand021_simplified/r_f_link4_4.STL"/>
        <mesh name="{name}-r_f_link5_1" file="robots/dexhand/meshes/dexhand021_simplified/r_f_link5_1.STL"/>
        <mesh name="{name}-r_f_link5_2" file="robots/dexhand/meshes/dexhand021_simplified/r_f_link5_2.STL"/>
        <mesh name="{name}-r_f_link5_3" file="robots/dexhand/meshes/dexhand021_simplified/r_f_link5_3.STL"/>
        <mesh name="{name}-r_f_link5_4" file="robots/dexhand/meshes/dexhand021_simplified/r_f_link5_4.STL"/>
        <mesh name="{name}-f1" file="robots/dexhand/meshes/dexhand021_simplified/F1b.stl" scale=".001 .001 .001"/>
        <mesh name="{name}-f2" file="robots/dexhand/meshes/dexhand021_simplified/F2b.stl" scale=".001 .001 .001"/>
        <mesh name="{name}-f3" file="robots/dexhand/meshes/dexhand021_simplified/F3b.stl" scale=".001 .001 .001"/>
        <mesh name="{name}-f4" file="robots/dexhand/meshes/dexhand021_simplified/F4b.stl" scale=".001 .001 .001"/>
        <mesh name="{name}-f5" file="robots/dexhand/meshes/dexhand021_simplified/F5b.stl" scale=".001 .001 .001"/>
        <mesh name="{name}-f6" file="robots/dexhand/meshes/dexhand021_simplified/F6b.stl" scale=".001 .001 .001"/>
        <mesh name="{name}-f7" file="robots/dexhand/meshes/dexhand021_simplified/F7b.stl" scale=".001 .001 .001"/>
      </asset>
    """
    wrist_mount = ""
    forearm_xml = ""

    _children_raw = """
          <freejoint name="{name}-{name}-left-floating_base"/>
          <site name="{name}" size="0.01" rgba="0 1 1 0.5"/>
          <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.75294 0.75294 0.75294 1" mesh="{name}-right_hand_base"/>
          <geom type="mesh" rgba="0.75294 0.75294 0.75294 1" mesh="{name}-right_hand_base" contype="0" conaffinity="0" group="1" density="0"/>
          <body name="{name}-r_f_link1_1" pos="0.032783 0.023781 0.11211" quat="0.151551 -0.775385 -0.612635 0.0221215">
            <inertial pos="0.00197785 -0.000351482 0.0134505" quat="0.716208 -0.0775695 -0.0529929 0.691535" mass="0.00440996" diaginertia="4.39581e-07 3.79862e-07 1.98309e-07"/>
            <joint name="{name}-r_f_joint1_1" pos="0 0 0" axis="0 0 1" range="0 2.2" actuatorfrcrange="-10 10" limited="true"/>
            <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link1_1"/>
            <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link1_1" contype="0" conaffinity="0" group="1" density="0"/>
            <site name="{name}-site_r_f_link1_1" size="0.005" rgba="1 0 0 1"/> <!-- Red -->
            <body name="{name}-r_f_link1_2" pos="0.0083307 0 0" quat="0.707105 -0.707108 0 0">
              <inertial pos="0.0214331 0.000179495 -0.00129805" quat="0.0128566 0.706495 -0.0167187 0.707404" mass="0.00995222" diaginertia="1.71013e-06 1.65574e-06 6.19077e-07"/>
              <joint name="{name}-r_f_joint1_2" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
              <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link1_2"/>
              <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link1_2" contype="0" conaffinity="0" group="1" density="0"/>
              <body name="{name}-r_f_link1_3" pos="0.043 0 0">
                <inertial pos="0.0134587 -0.000699996 -0.00129335" quat="0.0204189 0.706708 -0.0207895 0.706905" mass="0.00457333" diaginertia="3.7975e-07 3.56572e-07 2.03242e-07"/>
                <joint name="{name}-r_f_joint1_3" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
                <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link1_3"/>
                <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link1_3" contype="0" conaffinity="0" group="1" density="0"/>
                <body name="{name}-r_f_link1_4" pos="0.025 0 0">
                  <inertial pos="0.0197512 -0.0029745 -0.00109785" quat="-0.0170159 0.689951 -0.100438 0.716652" mass="0.00815928" diaginertia="1.11902e-06 1.10174e-06 3.47089e-07"/>
                  <joint name="{name}-r_f_joint1_4" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
                  <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link1_4"/>
                  <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link1_4" contype="0" conaffinity="0" group="1" density="0"/>
                  <geom size="0.002" pos="0.035 -0.004 0" contype="0" conaffinity="0" group="1" density="0" rgba="1 0 0 1"/>
                  <geom size="0.002" pos="0.035 -0.004 0" rgba="1 0 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  <geom size="0.006 0.0005 0.003" pos="0.026 0.0025 -0.001" quat="0.974794 0 0 -0.223106" type="box" contype="0" conaffinity="0" group="1" density="0" rgba="0 1 0 1"/>
                  <geom size="0.006 0.0005 0.003" pos="0.026 0.0025 -0.001" quat="0.974794 0 0 -0.223106" type="box" rgba="0 1 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  <body name="{name}-r_f_link1_tip" pos="0.035 -0.004 0" quat="1.0 0.0 0.0 0.0">
                    <geom name="{name}-geom_r_f_link1_tip" type="sphere" size="0.002" rgba="1 0 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                    <site name="{name}-site_r_f_link1_tip" size="0.002" type="sphere" rgba="1 0 0 1"/>
                  </body>
                  <body name="{name}-r_f_link1_pad" pos="0.026 0.0025 -0.001" quat="0.9747941070689433 0.0 0.0 -0.22310636213174545">
                    <geom name="{name}-geom_r_f_link1_pad" type="box" size="0.006 0.0005 0.003" rgba="0 1 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  </body>
                  <site name="{name}-site_r_f_link1_pad" pos="0.026 0.0025 -0.001" quat="0.9747941070689433 0.0 0.0 -0.22310636213174545" type="box" size="0.006 0.0005 0.003" rgba="0 1 0 1"/>
                  <site name="{name}-site_r_f_link1_4" pos="0.0143 0.006 0" size="0.0001" type="sphere" rgba="1 0 0 1" zaxis="0.46 1 0"/>
                  <body name="{name}-ts_wrapper_r_f_link1_pad" pos="0.0425 -0.0188 -0.0055" quat="0.69101 -0.15003 -0.69101 -0.15003">
                    <body name="{name}-force1_f1" pos="0 0 0.02">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f1" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force1_f2" pos="0 0 0.0192">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f2" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force1_f3" pos="0.00545 0 0.02">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f3" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force1_f4" pos="0 0 0.02465">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f4" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force1_f5" pos="-0.0001 0 0.0285">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f5" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force1_f6" pos="0.0055 0 0.0285">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f6" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force1_f7" pos="0 0 0.01362">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f7" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                  </body>
                  <geom name="{name}-col_r_f_link1_4" type="capsule" contype="1" conaffinity="1" group="3" size="0.0095" fromto="0.0 0 -0.001 0.027 -0.007 -0.001"/>
                </body>
                <geom name="{name}-col_r_f_link1_3" type="capsule" contype="1" conaffinity="1" group="3" size="0.007" fromto="0.0125 0.003 -0.0045 0.0125 0.003 0.0023"/>
              </body>
              <geom name="{name}-col_r_f_link1_2" type="capsule" contype="1" conaffinity="1" group="3" size="0.0095" fromto="0.0 0 0 0.03 0 -0.002"/>
            </body>
          </body>
          <body name="{name}-r_f_link2_1" pos="0.006966 0.034912 0.1644" quat="0.707105 0 -0.707108 0">
            <inertial pos="0.00700207 9.3578e-08 0.000968546" quat="0.602139 0.37074 0.370772 0.602087" mass="0.00409704" diaginertia="3.18125e-07 2.71726e-07 2.04208e-07"/>
            <joint name="{name}-r_f_joint2_1" pos="0 0 0" axis="0 0 1" range="0 0.3" actuatorfrcrange="-10 10" limited="true"/>
            <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.79216 0.81961 0.93333 1" mesh="{name}-r_f_link2_1"/>
            <geom type="mesh" rgba="0.79216 0.81961 0.93333 1" mesh="{name}-r_f_link2_1" contype="0" conaffinity="0" group="1" density="0"/>
            <site name="{name}-site_r_f_link2_1" size="0.005" rgba="1 0 0 1"/> <!-- Red -->
            <body name="{name}-r_f_link2_2" pos="0.017 0 0" quat="0.707105 -0.707108 0 0">
              <inertial pos="0.0211623 -0.000590509 -2.03591e-06" quat="0.507059 0.504013 0.495283 0.493514" mass="0.0094284" diaginertia="1.65775e-06 1.64329e-06 5.54341e-07"/>
              <joint name="{name}-r_f_joint2_2" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
              <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link2_2"/>
              <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link2_2" contype="0" conaffinity="0" group="1" density="0"/>
              <body name="{name}-r_f_link2_3" pos="0.043 0 0">
                <inertial pos="0.0134587 -0.000699996 -9.33093e-07" quat="0.0204189 0.706708 -0.0207895 0.706905" mass="0.00457333" diaginertia="3.7975e-07 3.56572e-07 2.03242e-07"/>
                <joint name="{name}-r_f_joint2_3" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
                <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link2_3"/>
                <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link2_3" contype="0" conaffinity="0" group="1" density="0"/>
                <body name="{name}-r_f_link2_4" pos="0.025 0 0">
                  <inertial pos="0.0197512 -0.0029745 2.99885e-07" quat="0.043096 0.705808 -0.0423577 0.705821" mass="0.00815928" diaginertia="1.11794e-06 1.10078e-06 3.46237e-07"/>
                  <joint name="{name}-r_f_joint2_4" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
                  <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link2_4"/>
                  <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link2_4" contype="0" conaffinity="0" group="1" density="0"/>
                  <geom size="0.002" pos="0.035 -0.004 0" contype="0" conaffinity="0" group="1" density="0" rgba="1 0 0 1"/>
                  <geom size="0.002" pos="0.035 -0.004 0" rgba="1 0 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  <geom size="0.006 0.0005 0.003" pos="0.026 0.0025 0" quat="0.974794 0 0 -0.223106" type="box" contype="0" conaffinity="0" group="1" density="0" rgba="0 1 0 1"/>
                  <geom size="0.006 0.0005 0.003" pos="0.026 0.0025 0" quat="0.974794 0 0 -0.223106" type="box" rgba="0 1 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  <body name="{name}-r_f_link2_tip" pos="0.035 -0.004 0" quat="1.0 0.0 0.0 0.0">
                    <geom name="{name}-geom_r_f_link2_tip" type="sphere" size="0.002" rgba="1 0 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                    <site name="{name}-site_r_f_link2_tip" size="0.002" type="sphere" rgba="1 0 0 1"/>
                  </body>
                  <body name="{name}-r_f_link2_pad" pos="0.026 0.0025 0.000" quat="0.9747941070689433 0.0 0.0 -0.22310636213174545">
                    <geom name="{name}-geom_r_f_link2_pad" type="box" size="0.006 0.0005 0.003" rgba="0 1 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  </body>
                  <site name="{name}-site_r_f_link2_pad" pos="0.026 0.0025 0.000" quat="0.9747941070689433 0.0 0.0 -0.22310636213174545" type="box" size="0.006 0.0005 0.003" rgba="0 1 0 1"/>
                  <site name="{name}-site_r_f_link2_4" pos="0.0143 0.006 0" size="0.0001" type="sphere" rgba="1 0 0 1" zaxis="0.46 1 0"/>
                  <body name="{name}-ts_wrapper_r_f_link2_pad" pos="0.0425 -0.0188 -0.0055" quat="0.69101 -0.15003 -0.69101 -0.15003">
                    <body name="{name}-force2_f1" pos="0 0 0.02">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f1" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force2_f2" pos="0 0 0.0192">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f2" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force2_f3" pos="0.00545 0 0.02">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f3" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force2_f4" pos="0 0 0.02465">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f4" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force2_f5" pos="-0.0001 0 0.0285">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f5" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force2_f6" pos="0.0055 0 0.0285">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f6" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force2_f7" pos="0 0 0.01362">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f7" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                  </body>
                  <geom name="{name}-col_r_f_link2_4" type="capsule" contype="1" conaffinity="1" group="3" size="0.0095" fromto="0.0 0 0 0.026 -0.007 0"/>
                </body>
                <geom name="{name}-col_r_f_link2_3" type="capsule" contype="1" conaffinity="1" group="3" size="0.007" fromto="0.012 0.003 -0.0035 0.012 0.003 0.0035"/>
              </body>
              <geom name="{name}-col_r_f_link2_2" type="capsule" contype="1" conaffinity="1" group="3" size="0.0095" fromto="0.005 0 0 0.03 0 0"/>
            </body>
          </body>
          <body name="{name}-r_f_link3_1" pos="0.006966 0.010612 0.1734" quat="0.707105 0 -0.707108 0">
            <inertial pos="0.00700207 9.45418e-08 0.000968552" quat="0.602139 0.37074 0.370772 0.602087" mass="0.00409704" diaginertia="3.18126e-07 2.71726e-07 2.04209e-07"/>
            <joint name="{name}-r_f_joint3_1" pos="0 0 0" axis="0 0 1" range="-0.001 0.001" limited="true"/>
            <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.79216 0.81961 0.93333 1" mesh="{name}-r_f_link3_1"/>
            <geom type="mesh" rgba="0.79216 0.81961 0.93333 1" mesh="{name}-r_f_link3_1" contype="0" conaffinity="0" group="1" density="0"/>
            <site name="{name}-site_r_f_link3_1" size="0.005" rgba="1 0 0 1"/> <!-- Red -->
            <body name="{name}-r_f_link3_2" pos="0.017 0 0" quat="0.707105 -0.707108 0 0">
              <inertial pos="0.0211623 -0.000590509 -2.03591e-06" quat="0.507059 0.504013 0.495283 0.493514" mass="0.0094284" diaginertia="1.65775e-06 1.64329e-06 5.54341e-07"/>
              <joint name="{name}-r_f_joint3_2" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
              <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link3_2"/>
              <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link3_2" contype="0" conaffinity="0" group="1" density="0"/>
              <body name="{name}-r_f_link3_3" pos="0.043 0 0">
                <inertial pos="0.0134587 -0.000699996 -9.33093e-07" quat="0.0204189 0.706708 -0.0207895 0.706905" mass="0.00457333" diaginertia="3.7975e-07 3.56572e-07 2.03242e-07"/>
                <joint name="{name}-r_f_joint3_3" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
                <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link3_3"/>
                <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link3_3" contype="0" conaffinity="0" group="1" density="0"/>
                <body name="{name}-r_f_link3_4" pos="0.025 0 0">
                  <inertial pos="0.0197512 -0.0029745 2.99885e-07" quat="0.043096 0.705808 -0.0423577 0.705821" mass="0.00815928" diaginertia="1.11794e-06 1.10078e-06 3.46237e-07"/>
                  <joint name="{name}-r_f_joint3_4" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
                  <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link3_4"/>
                  <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link3_4" contype="0" conaffinity="0" group="1" density="0"/>
                  <geom size="0.002" pos="0.035 -0.004 0" contype="0" conaffinity="0" group="1" density="0" rgba="1 0 0 1"/>
                  <geom size="0.002" pos="0.035 -0.004 0" rgba="1 0 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  <geom size="0.006 0.0005 0.003" pos="0.026 0.0025 0" quat="0.974794 0 0 -0.223106" type="box" contype="0" conaffinity="0" group="1" density="0" rgba="0 1 0 1"/>
                  <geom size="0.006 0.0005 0.003" pos="0.026 0.0025 0" quat="0.974794 0 0 -0.223106" type="box" rgba="0 1 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  <body name="{name}-r_f_link3_tip" pos="0.035 -0.004 0" quat="1.0 0.0 0.0 0.0">
                    <geom name="{name}-geom_r_f_link3_tip" type="sphere" size="0.002" rgba="1 0 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                    <site name="{name}-site_r_f_link3_tip" size="0.002" type="sphere" rgba="1 0 0 1"/>
                  </body>
                  <body name="{name}-r_f_link3_pad" pos="0.026 0.0025 0.000" quat="0.9747941070689433 0.0 0.0 -0.22310636213174545">
                    <geom name="{name}-geom_r_f_link3_pad" type="box" size="0.006 0.0005 0.003" rgba="0 1 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  </body>
                  <site name="{name}-site_r_f_link3_pad" pos="0.026 0.0025 0.000" quat="0.9747941070689433 0.0 0.0 -0.22310636213174545" type="box" size="0.006 0.0005 0.003" rgba="0 1 0 1"/>
                  <site name="{name}-site_r_f_link3_4" pos="0.0143 0.006 0" size="0.0001" type="sphere" rgba="1 0 0 1" zaxis="0.46 1 0"/>
                  <body name="{name}-ts_wrapper_r_f_link3_pad" pos="0.0425 -0.0188 -0.0055" quat="0.69101 -0.15003 -0.69101 -0.15003">
                    <body name="{name}-force3_f1" pos="0 0 0.02">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f1" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force3_f2" pos="0 0 0.0192">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f2" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force3_f3" pos="0.00545 0 0.02">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f3" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force3_f4" pos="0 0 0.02465">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f4" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force3_f5" pos="-0.0001 0 0.0285">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f5" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force3_f6" pos="0.0055 0 0.0285">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f6" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force3_f7" pos="0 0 0.01362">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f7" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                  </body>
                  <geom name="{name}-col_r_f_link3_4" type="capsule" contype="1" conaffinity="1" group="3" size="0.0095" fromto="0.0 0 0 0.026 -0.007 0"/>
                </body>
                <geom name="{name}-col_r_f_link3_3" type="capsule" contype="1" conaffinity="1" group="3" size="0.007" fromto="0.012 0.003 -0.0035 0.012 0.003 0.0035"/>
              </body>
              <geom name="{name}-col_r_f_link3_2" type="capsule" contype="1" conaffinity="1" group="3" size="0.0095" fromto="0.005 0 0 0.03 0 0"/>
            </body>
          </body>
          <body name="{name}-r_f_link4_1" pos="0.006966 -0.013688 0.1644" quat="-2.59734e-06 0.707105 2.59735e-06 0.707108">
            <inertial pos="0.00700206 -9.456e-08 -0.000968554" quat="0.370772 0.602087 0.602139 0.37074" mass="0.00409704" diaginertia="3.18126e-07 2.71726e-07 2.04209e-07"/>
            <joint name="{name}-r_f_joint4_1" pos="0 0 0" axis="0 0 1" range="0 0.3" actuatorfrcrange="-10 10" limited="true"/>
            <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.79216 0.81961 0.93333 1" mesh="{name}-r_f_link4_1"/>
            <geom type="mesh" rgba="0.79216 0.81961 0.93333 1" mesh="{name}-r_f_link4_1" contype="0" conaffinity="0" group="1" density="0"/>
            <site name="{name}-site_r_f_link4_1" size="0.005" rgba="1 0 0 1"/> <!-- Red -->
            <body name="{name}-r_f_link4_2" pos="0.017 0 0" quat="0.707105 0.707108 0 0">
              <inertial pos="0.0211623 -0.000590509 -2.03591e-06" quat="0.507059 0.504013 0.495283 0.493514" mass="0.0094284" diaginertia="1.65775e-06 1.64329e-06 5.54341e-07"/>
              <joint name="{name}-r_f_joint4_2" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
              <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link4_2"/>
              <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link4_2" contype="0" conaffinity="0" group="1" density="0"/>
              <body name="{name}-r_f_link4_3" pos="0.043 0 0">
                <inertial pos="0.0134587 -0.000699996 -9.33093e-07" quat="0.0204189 0.706708 -0.0207895 0.706905" mass="0.00457333" diaginertia="3.7975e-07 3.56572e-07 2.03242e-07"/>
                <joint name="{name}-r_f_joint4_3" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
                <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link4_3"/>
                <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link4_3" contype="0" conaffinity="0" group="1" density="0"/>
                <body name="{name}-r_f_link4_4" pos="0.025 0 0">
                  <inertial pos="0.0197512 -0.0029745 2.99885e-07" quat="0.043096 0.705808 -0.0423577 0.705821" mass="0.00815928" diaginertia="1.11794e-06 1.10078e-06 3.46237e-07"/>
                  <joint name="{name}-r_f_joint4_4" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
                  <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link4_4"/>
                  <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link4_4" contype="0" conaffinity="0" group="1" density="0"/>
                  <geom size="0.002" pos="0.035 -0.004 0" contype="0" conaffinity="0" group="1" density="0" rgba="1 0 0 1"/>
                  <geom size="0.002" pos="0.035 -0.004 0" rgba="1 0 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  <geom size="0.006 0.0005 0.003" pos="0.026 0.0025 0" quat="0.974794 0 0 -0.223106" type="box" contype="0" conaffinity="0" group="1" density="0" rgba="0 1 0 1"/>
                  <geom size="0.006 0.0005 0.003" pos="0.026 0.0025 0" quat="0.974794 0 0 -0.223106" type="box" rgba="0 1 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  <body name="{name}-r_f_link4_tip" pos="0.035 -0.004 0" quat="1.0 0.0 0.0 0.0">
                    <geom name="{name}-geom_r_f_link4_tip" type="sphere" size="0.002" rgba="1 0 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                    <site name="{name}-site_r_f_link4_tip" size="0.002" type="sphere" rgba="1 0 0 1"/>
                  </body>
                  <body name="{name}-r_f_link4_pad" pos="0.026 0.0025 0.000" quat="0.9747941070689433 0.0 0.0 -0.22310636213174545">
                    <geom name="{name}-geom_r_f_link4_pad" type="box" size="0.006 0.0005 0.003" rgba="0 1 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  </body>
                  <site name="{name}-site_r_f_link4_pad" pos="0.026 0.0025 0.000" quat="0.9747941070689433 0.0 0.0 -0.22310636213174545" type="box" size="0.006 0.0005 0.003" rgba="0 1 0 1"/>
                  <site name="{name}-site_r_f_link4_4" pos="0.0143 0.006 0" size="0.0001" type="sphere" rgba="1 0 0 1" zaxis="0.46 1 0"/>
                  <body name="{name}-ts_wrapper_r_f_link4_pad" pos="0.0425 -0.0188 -0.0055" quat="0.69101 -0.15003 -0.69101 -0.15003">
                    <body name="{name}-force4_f1" pos="0 0 0.02">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f1" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force4_f2" pos="0 0 0.0192">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f2" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force4_f3" pos="0.00545 0 0.02">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f3" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force4_f4" pos="0 0 0.02465">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f4" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force4_f5" pos="-0.0001 0 0.0285">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f5" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force4_f6" pos="0.0055 0 0.0285">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f6" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force4_f7" pos="0 0 0.01362">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f7" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                  </body>
                  <geom name="{name}-col_r_f_link4_4" type="capsule" contype="1" conaffinity="1" group="3" size="0.0095" fromto="0.0 0 0 0.026 -0.007 0"/>
                </body>
                <geom name="{name}-col_r_f_link4_3" type="capsule" contype="1" conaffinity="1" group="3" size="0.007" fromto="0.012 0.003 -0.0035 0.012 0.003 0.0035"/>
              </body>
              <geom name="{name}-col_r_f_link4_2" type="capsule" contype="1" conaffinity="1" group="3" size="0.0095" fromto="0.005 0 0 0.03 0 0"/>
            </body>
          </body>
          <body name="{name}-r_f_link5_1" pos="0.006966 -0.037988 0.1504" quat="-2.59734e-06 0.707105 2.59735e-06 0.707108">
            <inertial pos="0.00700207 -9.35677e-08 -0.000968542" quat="0.370771 0.602088 0.602139 0.37074" mass="0.00409703" diaginertia="3.18125e-07 2.71726e-07 2.04208e-07"/>
            <joint name="{name}-r_f_joint5_1" pos="0 0 0" axis="0 0 1" range="0 0.6" actuatorfrcrange="-10 10" limited="true"/>
            <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.792157 0.819608 0.933333 1" mesh="{name}-r_f_link5_1"/>
            <geom type="mesh" rgba="0.792157 0.819608 0.933333 1" mesh="{name}-r_f_link5_1" contype="0" conaffinity="0" group="1" density="0"/>
            <site name="{name}-site_r_f_link5_1" size="0.005" rgba="1 0 0 1"/> <!-- Red -->
            <body name="{name}-r_f_link5_2" pos="0.017 0 0" quat="0.707105 0.707108 0 0">
              <inertial pos="0.0211623 -0.000590509 -2.03591e-06" quat="0.507059 0.504013 0.495283 0.493514" mass="0.0094284" diaginertia="1.65775e-06 1.64329e-06 5.54341e-07"/>
              <joint name="{name}-r_f_joint5_2" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
              <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link5_2"/>
              <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link5_2" contype="0" conaffinity="0" group="1" density="0"/>
              <body name="{name}-r_f_link5_3" pos="0.043 0 0">
                <inertial pos="0.0134587 -0.000699996 -9.33093e-07" quat="0.0204189 0.706708 -0.0207895 0.706905" mass="0.00457333" diaginertia="3.7975e-07 3.56572e-07 2.03242e-07"/>
                <joint name="{name}-r_f_joint5_3" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
                <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link5_3"/>
                <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link5_3" contype="0" conaffinity="0" group="1" density="0"/>
                <body name="{name}-r_f_link5_4" pos="0.025 0 0">
                  <inertial pos="0.0197512 -0.0029745 2.99885e-07" quat="0.043096 0.705808 -0.0423577 0.705821" mass="0.00815928" diaginertia="1.11794e-06 1.10078e-06 3.46237e-07"/>
                  <joint name="{name}-r_f_joint5_4" pos="0 0 0" axis="0 0 1" range="0 1.3" actuatorfrcrange="-10 10" limited="true"/>
                  <geom type="mesh" contype="0" conaffinity="0" group="1" density="0" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link5_4"/>
                  <geom type="mesh" rgba="0.6 0.6 0.6 1" mesh="{name}-r_f_link5_4" contype="0" conaffinity="0" group="1" density="0"/>
                  <geom size="0.002" pos="0.035 -0.004 0" contype="0" conaffinity="0" group="1" density="0" rgba="1 0 0 1"/>
                  <geom size="0.002" pos="0.035 -0.004 0" rgba="1 0 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  <geom size="0.006 0.0005 0.003" pos="0.026 0.0025 0" quat="0.974794 0 0 -0.223106" type="box" contype="0" conaffinity="0" group="1" density="0" rgba="0 1 0 1"/>
                  <geom size="0.006 0.0005 0.003" pos="0.026 0.0025 0" quat="0.974794 0 0 -0.223106" type="box" rgba="0 1 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  <body name="{name}-r_f_link5_tip" pos="0.035 -0.004 0" quat="1.0 0.0 0.0 0.0">
                    <geom name="{name}-geom_r_f_link5_tip" type="sphere" size="0.002" rgba="1 0 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                    <site name="{name}-site_r_f_link5_tip" size="0.0001" type="sphere" rgba="1 0 0 1"/>
                  </body>
                  <body name="{name}-r_f_link5_pad" pos="0.026 0.0025 0.000" quat="0.9747941070689433 0.0 0.0 -0.22310636213174545">
                    <geom name="{name}-geom_r_f_link5_pad" type="box" size="0.006 0.0005 0.003" rgba="0 1 0 1" contype="0" conaffinity="0" group="1" density="0"/>
                  </body>
                  <site name="{name}-site_r_f_link5_pad" pos="0.026 0.0025 0.000" quat="0.9747941070689433 0.0 0.0 -0.22310636213174545" type="box" size="0.006 0.0005 0.003" rgba="0 1 0 1"/>
                  <site name="{name}-site_r_f_link5_4" pos="0.0143 0.006 0" size="0.0001" type="sphere" rgba="1 0 0 1" zaxis="0.46 1 0"/>
                  <body name="{name}-ts_wrapper_r_f_link5_pad" pos="0.0425 -0.0188 -0.0055" quat="0.69101 -0.15003 -0.69101 -0.15003">
                    <body name="{name}-force5_f1" pos="0 0 0.02">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f1" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force5_f2" pos="0 0 0.0192">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f2" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force5_f3" pos="0.00545 0 0.02">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f3" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force5_f4" pos="0 0 0.02465">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f4" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force5_f5" pos="-0.0001 0 0.0285">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f5" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force5_f6" pos="0.0055 0 0.0285">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f6" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                    <body name="{name}-force5_f7" pos="0 0 0.01362">
                      <geom type="mesh" rgba="1 0.3 0.3 1" mesh="{name}-f7" contype="0" conaffinity="0" group="1" density="0"/>
                    </body>
                  </body>
                  <geom name="{name}-col_r_f_link5_4" type="capsule" contype="1" conaffinity="1" group="3" size="0.0095" fromto="0.0 0 0 0.026 -0.007 0"/>
                </body>
                <geom name="{name}-col_r_f_link5_3" type="capsule" contype="1" conaffinity="1" group="3" size="0.007" fromto="0.012 0.003 -0.0035 0.012 0.003 0.0035"/>
              </body>
              <geom name="{name}-col_r_f_link5_2" type="capsule" contype="1" conaffinity="1" group="3" size="0.0095" fromto="0.005 0 0 0.03 0 0"/>
            </body>
          </body>
          <geom name="{name}-col_right_hand_base" type="box" contype="1" conaffinity="1" group="3" size="0.0273 0.05 0.05" pos="-0.0022 0 0.11"/>
        """

    _postamble = """
<!--  <actuator>-->
<!--    <position name="dex_hand_right-act_r_f_joint1_2" joint="dex_hand_right-r_f_joint1_2" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>-->
<!--    <position name="dex_hand_right-act_r_f_joint1_3" joint="dex_hand_right-r_f_joint1_3" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>-->
<!--    <position name="dex_hand_right-act_r_f_joint1_4" joint="dex_hand_right-r_f_joint1_4" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>-->
<!--    <position name="dex_hand_right-act_r_f_joint2_2" joint="dex_hand_right-r_f_joint2_2" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>-->
<!--    <position name="dex_hand_right-act_r_f_joint2_3" joint="dex_hand_right-r_f_joint2_3" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>-->
<!--    <position name="dex_hand_right-act_r_f_joint2_4" joint="dex_hand_right-r_f_joint2_4" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>-->
<!--    <position name="dex_hand_right-act_r_f_joint3_2" joint="dex_hand_right-r_f_joint3_2" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>-->
<!--    <position name="dex_hand_right-act_r_f_joint3_3" joint="dex_hand_right-r_f_joint3_3" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>-->
<!--    <position name="dex_hand_right-act_r_f_joint3_4" joint="dex_hand_right-r_f_joint3_4" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>-->
<!--    <position name="dex_hand_right-act_r_f_joint4_2" joint="dex_hand_right-r_f_joint4_2" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>-->
<!--    <position name="dex_hand_right-act_r_f_joint4_3" joint="dex_hand_right-r_f_joint4_3" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>-->
<!--    <position name="dex_hand_right-act_r_f_joint4_4" joint="dex_hand_right-r_f_joint4_4" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>-->
<!--    <position name="dex_hand_right-act_r_f_joint5_2" joint="dex_hand_right-r_f_joint5_2" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>-->
<!--    <position name="dex_hand_right-act_r_f_joint5_3" joint="dex_hand_right-r_f_joint5_3" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>-->
<!--    <position name="dex_hand_right-act_r_f_joint5_4" joint="dex_hand_right-r_f_joint5_4" kp="1000" kv="50" ctrlrange="0 1.3" forcerange="-200 200" forcelimited="true"/>-->
<!--    <position name="dex_hand_right-act_r_f_joint1_1" joint="dex_hand_right-r_f_joint1_1" kp="1000" kv="50" ctrlrange="0 2.2" forcerange="-200 200" forcelimited="true"/>-->
<!--    <position name="dex_hand_right-act_r_f_joint2_1" joint="dex_hand_right-r_f_joint2_1" kp="1000" kv="50" ctrlrange="0 0.3" forcerange="-200 200" forcelimited="true"/>-->
<!--    <position name="dex_hand_right-act_r_f_joint3_1" joint="dex_hand_right-r_f_joint3_1" kp="1000" kv="50" ctrlrange="-0.0001 0.0001" forcerange="-200 200" forcelimited="true"/>-->
<!--    <position name="dex_hand_right-act_r_f_joint4_1" joint="dex_hand_right-r_f_joint4_1" kp="1000" kv="50" ctrlrange="0 0.3" forcerange="-200 200" forcelimited="true"/>-->
<!--    <position name="dex_hand_right-act_r_f_joint5_1" joint="dex_hand_right-r_f_joint5_1" kp="1000" kv="50" ctrlrange="0 0.6" forcerange="-200 200" forcelimited="true"/>-->
<!--  </actuator> -->
      <sensor>
        <touch name="{name}-touch_r_f_link1_pad" site="{name}-site_r_f_link1_pad"/>
        <touch name="{name}-touch_r_f_link2_pad" site="{name}-site_r_f_link2_pad"/>
        <touch name="{name}-touch_r_f_link3_pad" site="{name}-site_r_f_link3_pad"/>
        <touch name="{name}-touch_r_f_link4_pad" site="{name}-site_r_f_link4_pad"/>
        <touch name="{name}-touch_r_f_link5_pad" site="{name}-site_r_f_link5_pad"/>
        <rangefinder name="{name}-rf1" site="{name}-site_r_f_link1_4" cutoff="0.1"/>
        <rangefinder name="{name}-rf2" site="{name}-site_r_f_link2_4" cutoff="0.1"/>
        <rangefinder name="{name}-rf3" site="{name}-site_r_f_link3_4" cutoff="0.1"/>
        <rangefinder name="{name}-rf4" site="{name}-site_r_f_link4_4" cutoff="0.1"/>
        <rangefinder name="{name}-rf5" site="{name}-site_r_f_link5_4" cutoff="0.1"/>
        <user name="{name}-TS-F-A-1" dim="11" noise="0.0"/>
        <user name="{name}-TS-F-A-2" dim="11" noise="0.0"/>
        <user name="{name}-TS-F-A-3" dim="11" noise="0.0"/>
        <user name="{name}-TS-F-A-4" dim="11" noise="0.0"/>
        <user name="{name}-TS-F-A-5" dim="11" noise="0.0"/>
      </sensor>
      <contact>
{self_collision_exclusions}
      </contact>
      <equality>
        {welds}
      </equality>
    """

    # print(right_hand._xml | Prettify())

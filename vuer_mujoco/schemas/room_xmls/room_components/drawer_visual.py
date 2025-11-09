from vuer_mujoco.schemas.schema import Body


class KitchenDrawerVisual(Body):
    """
    Pull-out kitchen drawer whose **total width = 2·width**.

    • Outer frame is fixed; inner box slides −Y on a prismatic joint.
    • Visual geoms → group 1, collision geoms → group 3.
    """

    # ───────── class-level defaults you may change ─────────
    assets       = "drawer"
    prefix       = "drawer"
    body_pos     = "2.05 -0.3 0.365"
    body_quat    = "1 0 0 0"
    slide_range  = "-0.5 0"          # drawer travel (m)
    # handle / pin sizes stay constant
    sz_handle    = "0.013 0.0635"
    sz_pin       = "0.008 0.025"
    side_gap = 0.001
    # vertical trim is constant in X (only thickness matters)
    sz_trim_v    = "0.04 0.1035 0.01"

    # ───────── constructor lets caller set the width ─────────
    def __init__(self, *, width: float = 0.50, **kwargs):
        """
        Parameters
        ----------
        width : float
            **Half-width** of carcass in metres (default 0.50 ➜ 1 m total).  
            All horizontal dimensions & offsets are derived from this.
        """
        self.w = float(width)
        super().__init__(**kwargs)

    # ───────── handy string helper ─────────
    _box = staticmethod(lambda x, y, z: f"{x:.4f} {y:.4f} {z:.4f}")

    # ───────── derived sizes / offsets (depend on self.w) ─────────
    # outer frame
    @property
    def sz_frame_tb(self):   return self._box(self.w,         0.285, 0.015)
    @property
    def sz_frame_back(self): return self._box(self.w - 0.030, 0.015, 0.075)
    @property
    def sz_frame_side(self): return self._box(0.015,          0.285, 0.075)
    @property
    def off_outer(self):     return f"{self.w - 0.015:.4f}"

    # inner sliding box
    @property
    def sz_inner_bot(self):   return self._box(self.w - 0.031, 0.270, 0.015)
    @property
    def sz_inner_back(self):  return self._box(self.w - 0.061, 0.015, 0.044)
    @property
    def sz_inner_side(self):  return self._box(0.015,          0.270, 0.044)
    @property
    def off_inner(self):      return f"{self.w - 0.031 * 1.5:.4f}"

    # face panel / horizontal trims
    @property
    def sz_face(self):    return self._box(self.w - 0.0815, 0.0235, 0.005)
    @property
    def sz_trim_h(self):  return self._box(self.w - 0.0815, 0.0400, 0.010)
    @property
    def off_face(self):   return f"{self.w - 0.0415:.4f}"

    # ───────── attributes on the root <body> tag ─────────
    _attributes = {
        "name": prefix,
        "pos":  body_pos,
        "quat": body_quat,
    }

    # ───────── <asset> block ─────────
    _preamble = """
    <asset>
        <texture type="2d" name="{prefix}_tex_lam"   file="{assets}/laminate.png"/>
        <texture type="2d" name="{prefix}_tex_metal" file="{assets}/metal.png"/>

        <material name="{prefix}_lam_mat"    texture="{prefix}_tex_lam"   shininess="0.1" reflectance="0.1"/>
        <material name="{prefix}_face_mat"   texture="{prefix}_tex_lam"   shininess="0.1" reflectance="0.1"/>
        <material name="{prefix}_handle_mat" texture="{prefix}_tex_metal" shininess="0.8" reflectance="0.8"/>
    </asset>
    """

    # ───────── body tree ─────────
    _children_raw = """
    <!-- ========== OUTER FRAME ========== -->
    <body name="{name}_frame">
        <!-- ========== SLIDING BOX ========== -->
        <body name="{name}_box">
            <!-- ========== FACE PANEL ========== -->
            <body name="{name}_face" pos="0 -0.285 0">
                <geom name="{name}_face_col" size="{sz_face}" pos="0 0.005 0"
                      quat="0.707105 0.707108 0 0" type="box" group="3" density="10"/>
                <geom name="{name}_face_v"   size="{sz_face}" pos="0 0.005 0"
                      quat="0.707105 0.707108 0 0" type="box" contype="0" conaffinity="0"
                      group="0" mass="0" material="{prefix}_face_mat"/>

                <!-- horizontal trims -->
                <geom name="{name}_trim_t_v" size="{sz_trim_h}" pos="0 -0.0025 0.0635"
                      quat="0.707105 0.707108 0 0" type="box" contype="0" conaffinity="0"
                      group="0" mass="0" material="{prefix}_face_mat"/>
                <geom name="{name}_trim_b_v" size="{sz_trim_h}" pos="0 -0.0025 -0.0635"
                      quat="0.707105 0.707108 0 0" type="box" contype="0" conaffinity="0"
                      group="0" mass="0" material="{prefix}_face_mat"/>

                <!-- vertical trims -->
                <geom name="{name}_trim_l_v" size="{sz_trim_v}" pos="-{off_face} -0.0025 0"
                      quat="0.707105 0.707108 0 0" type="box" contype="0" conaffinity="0"
                      group="0" mass="0" material="{prefix}_face_mat"/>
                <geom name="{name}_trim_r_v" size="{sz_trim_v}" pos="{off_face} -0.0025 0"
                      quat="0.707105 0.707108 0 0" type="box" contype="0" conaffinity="0"
                      group="0" mass="0" material="{prefix}_face_mat"/>

                <!-- handle -->
                <body name="{name}_handle">
                    <geom name="{name}_bar_col" type="cylinder" size="{sz_handle}"
                          pos="0 -0.05 0" quat="0.707105 0 0.707108 0"
                          group="3" density="10"/>
                    <geom name="{name}_bar_v"   type="cylinder" size="{sz_handle}"
                          pos="0 -0.05 0" quat="0.707105 0 0.707108 0"
                          contype="0" conaffinity="0" group="0" mass="0"
                          material="{prefix}_handle_mat"/>

                    <geom name="{name}_pin_t_v" type="cylinder" size="{sz_pin}"
                          pos="0.0381 -0.025 0" quat="0.707107 0.707107 0 0"
                          contype="0" conaffinity="0" group="0" mass="0"
                          material="{prefix}_handle_mat"/>
                    <geom name="{name}_pin_b_v" type="cylinder" size="{sz_pin}"
                          pos="-0.0381 -0.025 0" quat="0.707107 0.707107 0 0"
                          contype="0" conaffinity="0" group="0" mass="0"
                          material="{prefix}_handle_mat"/>
                </body>
            </body>
        </body>
    </body>
    """

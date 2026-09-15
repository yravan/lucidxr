from .drawer import KitchenDrawer


class KitchenDrawerVisual(KitchenDrawer):
    """Fixed drawer face for layouts without an interactive sliding box."""

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

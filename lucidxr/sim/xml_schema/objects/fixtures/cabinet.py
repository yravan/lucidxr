from lucidxr.sim.xml_schema.schema import Body


class KitchenCabinet(Body):
    """
    Two–door base cabinet with shelves and working hinges.
    ─────────────────────────────────────────────────────────
    • All *visual* geoms have group="0", mass="0",
      and `contype="0" conaffinity="0"` so they never collide.

    • All *collision* geoms go in group="3" and use the same sizes.

    • Door hinges are revolute joints with ±3 rad range
      (approx ±172°) – tune as you like.
    """

    show_texture = True  # whether to include texture/material preamble

    assets = "rooms/cabinet"  # folder that holds textures / meshes
    prefix = "cab"  # unique prefix for every generated tag
    body_pos = "2.05 -0.20 1.85"  # placement of whole cabinet
    body_quat = "1 0 0 0"  # rotation of whole cabinet

    # primitive sizes reused a lot
    sz_top_bot = "0.5 0.185 0.015"
    sz_back = "0.47 0.015 0.43"
    sz_side = "0.015 0.185 0.43"
    sz_shelf = "0.47 0.15 0.015"
    sz_door = "0.1685 0.3785 0.005"
    sz_trim_long = "0.1685 0.04 0.01"
    sz_trim_vert = "0.04 0.4585 0.01"
    sz_handle = "0.013 0.12"
    sz_handle_pin = "0.008 0.025"

    _attributes = {
        "name": prefix,
        "pos": body_pos,
        "quat": body_quat,
    }

    _preamble = """
    <asset>
        <!-- flat-coloured laminate & bright metal -->
        <texture type="2d" name="{prefix}_tex_body"  file="{assets}/laminate.png"/>
        <texture type="2d" name="{prefix}_tex_metal" file="{assets}/metal.png"/>

        <material name="{prefix}_body_mat"  texture="{prefix}_tex_body"  shininess="0.1" reflectance="0.1"/>
        <material name="{prefix}_door_mat"  texture="{prefix}_tex_body"  shininess="0.1" reflectance="0.1"/>
        <material name="{prefix}_handle_mat" texture="{prefix}_tex_metal" shininess="0.8" reflectance="0.8"/>
    </asset>
    """

    _children_raw = """
    <body name="{name}_main">
        <!-- ========= cabinet carcass – collisions (group 3) ========= -->
        <geom name="{name}_top"     size="{sz_top_bot}"  pos="0 0.015 0.445"  type="box" group="3" density="10"/>
        <geom name="{name}_bottom"  size="{sz_top_bot}"  pos="0 0.015 -0.445" type="box" group="3" density="10"/>
        <geom name="{name}_back"    size="{sz_back}"     pos="0 0.185 0"      type="box" group="3" density="10"/>
        <geom name="{name}_right"   size="{sz_side}"     pos="0.485 0.015 0"  type="box" group="3" density="10"/>
        <geom name="{name}_left"    size="{sz_side}"     pos="-0.485 0.015 0" type="box" group="3" density="10"/>
        <geom name="{name}_shelf"   size="{sz_shelf}"    pos="0 0.035 0"      type="box" group="3" density="10"/>

        <!-- ========= cabinet carcass – visuals (group 0) ============ -->
        <geom name="{name}_top_v"     size="{sz_top_bot}" pos="0 0.015 0.445"  type="box"
              contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_body_mat"/>
        <geom name="{name}_bottom_v"  size="{sz_top_bot}" pos="0 0.015 -0.445" type="box"
              contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_body_mat"/>
        <geom name="{name}_back_v"    size="{sz_back}"    pos="0 0.185 0"      type="box"
              contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_body_mat"/>
        <geom name="{name}_right_v"   size="{sz_side}"    pos="0.485 0.015 0"  type="box"
              contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_body_mat"/>
        <geom name="{name}_left_v"    size="{sz_side}"    pos="-0.485 0.015 0" type="box"
              contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_body_mat"/>
        <geom name="{name}_shelf_v"   size="{sz_shelf}"   pos="0 0.035 0"      type="box"
              contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_body_mat"/>

        <!-- =========================================================== -->
        <!--                     LEFT  DOOR                              -->
        <!-- =========================================================== -->
        <body name="{name}_left_hinge">
            <joint name="{name}_leftdoor_hinge" pos="-0.485 -0.2 0"
                   axis="0 0 1" limited="true" range="-3 0" damping="2"/>

            <body name="{name}_left_door" pos="-0.25 -0.185 0">
                <!-- door slab – collision & visual  -->
                <geom name="{name}_left_door_col"  size="{sz_door}" pos="0 0.005 0"
                      quat="0.707105 0.707108 0 0" type="box" group="3" density="10"/>
                <geom name="{name}_left_door_vis"  size="{sz_door}" pos="0 0.005 0"
                      quat="0.707105 0.707108 0 0" type="box"
                      contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_door_mat"/>

                <!-- decorative trims (visual only) -->
                <geom name="{name}_lt_trim_top"    size="{sz_trim_long}" pos="0 -0.0025  0.4185"
                      quat="0.707105 0.707108 0 0" type="box"
                      contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_door_mat"/>
                <geom name="{name}_lt_trim_bottom" size="{sz_trim_long}" pos="0 -0.0025 -0.4185"
                      quat="0.707105 0.707108 0 0" type="box"
                      contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_door_mat"/>
                <geom name="{name}_lt_trim_left"   size="{sz_trim_vert}" pos="-0.2085 -0.0025 0"
                      quat="0.707105 0.707108 0 0" type="box"
                      contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_door_mat"/>
                <geom name="{name}_lt_trim_right"  size="{sz_trim_vert}" pos="0.2085 -0.0025 0"
                      quat="0.707105 0.707108 0 0" type="box"
                      contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_door_mat"/>

                <!-- handle -->
                <body name="{name}_left_handle" pos="0.1985 0 -0.2585">
                    <geom name="{name}_lh_bar"    type="cylinder" size="{sz_handle}"     pos="0 -0.05 0"
                          group="3" density="10"/>
                    <geom name="{name}_lh_bar_v"  type="cylinder" size="{sz_handle}"     pos="0 -0.05 0"
                          contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_handle_mat"/>
                    <geom name="{name}_lh_pin_t"  type="cylinder" size="{sz_handle_pin}" pos="0 -0.025 0.072"
                          quat="0.707107 0.707107 0 0" group="3" density="10"/>
                    <geom name="{name}_lh_pin_t_v" type="cylinder" size="{sz_handle_pin}" pos="0 -0.025 0.072"
                          quat="0.707107 0.707107 0 0" contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_handle_mat"/>
                    <geom name="{name}_lh_pin_b"  type="cylinder" size="{sz_handle_pin}" pos="0 -0.025 -0.072"
                          quat="0.707107 0.707107 0 0" group="3" density="10"/>
                    <geom name="{name}_lh_pin_b_v" type="cylinder" size="{sz_handle_pin}" pos="0 -0.025 -0.072"
                          quat="0.707107 0.707107 0 0" contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_handle_mat"/>
                </body>
            </body>
        </body>

        <!-- =========================================================== -->
        <!--                     RIGHT DOOR                              -->
        <!-- =========================================================== -->
        <body name="{name}_right_hinge">
            <joint name="{name}_rightdoor_hinge" pos="0.485 -0.2 0"
                   axis="0 0 1" limited="true" range="0 3" damping="2"/>

            <body name="{name}_right_door" pos="0.25 -0.185 0">
                <!-- collision & visual for slab -->
                <geom name="{name}_right_door_col" size="{sz_door}" pos="0 0.005 0"
                      quat="0.707105 0.707108 0 0" type="box" group="3" density="10"/>
                <geom name="{name}_right_door_vis" size="{sz_door}" pos="0 0.005 0"
                      quat="0.707105 0.707108 0 0" type="box"
                      contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_door_mat"/>

                <!-- same trims as left door -->
                <geom name="{name}_rt_trim_top"    size="{sz_trim_long}" pos="0 -0.0025 0.4185"
                      quat="0.707105 0.707108 0 0" type="box"
                      contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_door_mat"/>
                <geom name="{name}_rt_trim_bottom" size="{sz_trim_long}" pos="0 -0.0025 -0.4185"
                      quat="0.707105 0.707108 0 0" type="box"
                      contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_door_mat"/>
                <geom name="{name}_rt_trim_left"   size="{sz_trim_vert}" pos="-0.2085 -0.0025 0"
                      quat="0.707105 0.707108 0 0" type="box"
                      contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_door_mat"/>
                <geom name="{name}_rt_trim_right"  size="{sz_trim_vert}" pos="0.2085 -0.0025 0"
                      quat="0.707105 0.707108 0 0" type="box"
                      contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_door_mat"/>

                <!-- handle mirrored across X -->
                <body name="{name}_right_handle" pos="-0.1985 0 -0.2585">
                    <geom name="{name}_rh_bar"   type="cylinder" size="{sz_handle}"     pos="0 -0.05 0"
                          group="3" density="10"/>
                    <geom name="{name}_rh_bar_v" type="cylinder" size="{sz_handle}"     pos="0 -0.05 0"
                          contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_handle_mat"/>
                    <geom name="{name}_rh_pin_t" type="cylinder" size="{sz_handle_pin}" pos="0 -0.025 0.072"
                          quat="0.707107 0.707107 0 0" group="3" density="10"/>
                    <geom name="{name}_rh_pin_t_v" type="cylinder" size="{sz_handle_pin}" pos="0 -0.025 0.072"
                          quat="0.707107 0.707107 0 0" contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_handle_mat"/>
                    <geom name="{name}_rh_pin_b" type="cylinder" size="{sz_handle_pin}" pos="0 -0.025 -0.072"
                          quat="0.707107 0.707107 0 0" group="3" density="10"/>
                    <geom name="{name}_rh_pin_b_v" type="cylinder" size="{sz_handle_pin}" pos="0 -0.025 -0.072"
                          quat="0.707107 0.707107 0 0" contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_handle_mat"/>
                </body>
            </body>
        </body>
    </body>
    """

    def __init__(self, **kwargs):
        self.show_texture = kwargs.get("keep_texture", self.show_texture)
        if not self.show_texture:
            self._preamble = """
            <asset>
                <!-- flat-coloured laminate & bright metal -->
                <material name="{prefix}_body_mat" rgba="0.7 0.7 0.7 1" shininess="0.1" reflectance="0.1"/>
                <material name="{prefix}_door_mat"  rgba="0.7 0.7 0.7 1"  shininess="0.1" reflectance="0.1"/>
                <material name="{prefix}_handle_mat" rgba="0.7 0.7 0.7 1" shininess="0.8" reflectance="0.8"/>
            </asset>
            """  # disable texture/material preamble
        super().__init__(**kwargs)

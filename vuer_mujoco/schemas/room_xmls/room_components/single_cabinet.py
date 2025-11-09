from vuer_mujoco.schemas.schema import Body


class KitchenSingleCabinet(Body):
    """
    Single-door single-cabinet module (≈ 0.5 m wide) that mounts in a base-cabinet stack.
    ─────────────────────────────────────────────────────────────────────────────
    • Collision geoms → group 3 • Visual geoms → group 1 (mass 0, contype/affinity 0)
    • Door swings out around +Z (hinge on the right edge).
    """

    # ── quick knobs you’ll typically change ──────────────────────────
    assets   = "single-cabinet"                       # path to meshes / textures
    prefix   = "single-cabinet"                       # tag prefix for uniqueness
    body_pos = "4.9 -0.9 0.365"               # placement in the scene
    body_quat = "0.707105 0 0 -0.707108"

    # primitive block-sizes
    sz_top_bot  = "0.25 0.285 0.015"
    sz_back     = "0.22 0.015 0.285"
    sz_side     = "0.015 0.285 0.285"
    sz_shelf    = "0.22 0.25 0.015"
    sz_door     = "0.1685 0.2335 0.005"
    sz_trim_h   = "0.1685 0.04 0.01"
    sz_trim_v   = "0.04 0.3135 0.01"
    sz_handle   = "0.013 0.12"
    sz_pin      = "0.008 0.025"

    # ── attributes on the root <body> tag ────────────────────────────
    _attributes = {
        "name": prefix,
        "pos":  body_pos,
        "quat": body_quat,
    }

    # ── <asset> section: textures, materials, meshes ─────────────────
    _preamble = """
    <asset>
        <texture type="2d" name="{prefix}_tex_body" file="{assets}/laminate.png"/>
        <texture type="2d" name="{prefix}_tex_metal"  file="{assets}/metal.png"/>

        <material name="{prefix}_body_mat"  texture="{prefix}_tex_body"  shininess="0.1" reflectance="0.1"/>
        <material name="{prefix}_door_mat"  texture="{prefix}_tex_body"  shininess="0.1" reflectance="0.1"/>
        <material name="{prefix}_handle_mat" texture="{prefix}_tex_metal" shininess="0.8" reflectance="0.8"/>
    </asset>
    """

    # ── body tree ────────────────────────────────────────────────────
    _children_raw = """
    <body name="{name}_main">
        <!-- carcass collisions (group 3) -->
        <geom name="{name}_top_col"    size="{sz_top_bot}" pos="0 0.015 0.3"   type="box" group="3" mass="0.2"/>
        <geom name="{name}_bottom_col" size="{sz_top_bot}" pos="0 0.015 -0.3"  type="box" group="3" mass="0.2"/>
        <geom name="{name}_back_col"   size="{sz_back}"    pos="0 0.285 0"     type="box" group="3" mass="0.2"/>
        <geom name="{name}_right_col"  size="{sz_side}"    pos="0.235 0.015 0" type="box" group="3" mass="0.2"/>
        <geom name="{name}_left_col"   size="{sz_side}"    pos="-0.235 0.015 0" type="box" group="3" mass="0.2"/>
        <geom name="{name}_shelf_col"  size="{sz_shelf}"   pos="0 0.035 0"     type="box" group="3" density="10"/>

        <!-- carcass visuals (group 0) -->
        <geom name="{name}_top_v"    size="{sz_top_bot}" pos="0 0.015 0.3"  type="box"
              contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_body_mat"/>
        <geom name="{name}_bottom_v" size="{sz_top_bot}" pos="0 0.015 -0.3" type="box"
              contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_body_mat"/>
        <geom name="{name}_back_v"   size="{sz_back}"    pos="0 0.285 0"    type="box"
              contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_body_mat"/>
        <geom name="{name}_right_v"  size="{sz_side}"    pos="0.235 0.015 0" type="box"
              contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_body_mat"/>
        <geom name="{name}_left_v"   size="{sz_side}"    pos="-0.235 0.015 0" type="box"
              contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_body_mat"/>
        <geom name="{name}_shelf_v"  size="{sz_shelf}"   pos="0 0.035 0"    type="box"
              contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_body_mat"/>

        <body name="{name}_hinge">
            <joint name="{name}_door_hinge" pos="0.235 -0.3 0" axis="0 0 1"
                   limited="true" range="0 3" damping="2"/>

            <body name="{name}_door" pos="0 -0.285 0">
                <!-- door slab -->
                <geom name="{name}_door_col" size="{sz_door}" pos="0 0.005 0"
                      quat="0.707105 0.707108 0 0" type="box" group="3" density="10"/>
                <geom name="{name}_door_v"  size="{sz_door}" pos="0 0.005 0"
                      quat="0.707105 0.707108 0 0" type="box"
                      contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_door_mat"/>

                <!-- decorative trims (visual only) -->
                <geom name="{name}_trim_top_v"    size="{sz_trim_h}" pos="0 -0.0025 0.2735"
                      quat="0.707105 0.707108 0 0" type="box"
                      contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_door_mat"/>
                <geom name="{name}_trim_bottom_v" size="{sz_trim_h}" pos="0 -0.0025 -0.2735"
                      quat="0.707105 0.707108 0 0" type="box"
                      contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_door_mat"/>
                <geom name="{name}_trim_left_v"   size="{sz_trim_v}" pos="-0.2085 -0.0025 0"
                      quat="0.707105 0.707108 0 0" type="box"
                      contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_door_mat"/>
                <geom name="{name}_trim_right_v"  size="{sz_trim_v}" pos="0.2085 -0.0025 0"
                      quat="0.707105 0.707108 0 0" type="box"
                      contype="0" conaffinity="0" group="0" mass="0" material="{prefix}_door_mat"/>

                <!-- handle -->
                <body name="{name}_handle" pos="-0.1985 0 0.1135">
                    <geom name="{name}_handle_bar_col" type="cylinder" size="{sz_handle}"
                          pos="0 -0.05 0" group="3" density="10"/>
                    <geom name="{name}_handle_bar_v"  type="cylinder" size="{sz_handle}"
                          pos="0 -0.05 0" contype="0" conaffinity="0" group="0"
                          mass="0" material="{prefix}_handle_mat"/>

                    <geom name="{name}_pin_t_col" type="cylinder" size="{sz_pin}"
                          pos="0 -0.025 0.072" quat="0.707107 0.707107 0 0"
                          group="3" density="10"/>
                    <geom name="{name}_pin_t_v"   type="cylinder" size="{sz_pin}"
                          pos="0 -0.025 0.072" quat="0.707107 0.707107 0 0"
                          contype="0" conaffinity="0" group="0"
                          mass="0" material="{prefix}_handle_mat"/>

                    <geom name="{name}_pin_b_col" type="cylinder" size="{sz_pin}"
                          pos="0 -0.025 -0.072" quat="0.707107 0.707107 0 0"
                          group="3" density="10"/>
                    <geom name="{name}_pin_b_v"   type="cylinder" size="{sz_pin}"
                          pos="0 -0.025 -0.072" quat="0.707107 0.707107 0 0"
                          contype="0" conaffinity="0" group="0"
                          mass="0" material="{prefix}_handle_mat"/>
                </body>
            </body>
        </body>
    </body>
    """

from lucidxr.sim.xml_schema.schema import Body


class KitchenOven(Body):
    """
    Glass-top electric stove with 5 rotating burner knobs.
    ══════════════════════════════════════════════════════
    * Visual meshes live in group 1, non-colliding.
    * Simplified collision hulls live in group 3.
    * All names are auto-prefixed, so multiple ovens can be spawned.
    """

    # ---------- quick knobs ----------
    assets = "electric-range"  # folder holding all meshes / textures
    prefix = "oven"  # tag prefix for uniqueness
    body_pos = "4.846 -1.534 0.6404"  # placement
    body_quat = "0.707105 0 0 -0.707108"

    # collision block sizes
    sz_core = "0.384 0.33 0.432"
    sz_lip = "0.384 0.036 0.18"
    sz_lip2 = "0.384 0.012 0.03"
    sz_plate = "0.156 0.012 0.036"
    sz_knob = "0.012 0.018 0.0264"

    # ---------- attributes ----------
    _attributes = {
        "name": prefix,
        "pos": body_pos,
        "quat": body_quat,
    }

    # ---------- <asset> ----------
    _preamble = """
    <asset>
        <texture type="2d" name="{prefix}_tex_body"  file="{assets}/paint.png"/>

        <material name="{prefix}_glass_mat" shininess="1" rgba="0.103704 0.103704 0.103704 0.25"/>
        <material name="{prefix}_body_mat"  texture="{prefix}_tex_body"  shininess="0.25"/>

        <!-- main chassis and knob meshes -->
        <mesh name="{prefix}_body_vis0"  file="{assets}/model_0.obj" scale="1.2 1.2 1.2"/>
        <mesh name="{prefix}_body_vis1"  file="{assets}/model_1.obj" scale="1.2 1.2 1.2"/>
        <mesh name="{prefix}_knob_rc_vis" file="{assets}/knob_rear_center.obj" scale="1.2 1.2 1.2"/>
        <mesh name="{prefix}_knob_rr_vis" file="{assets}/knob_rear_right.obj"  scale="1.2 1.2 1.2"/>
        <mesh name="{prefix}_knob_fl_vis" file="{assets}/knob_front_left.obj"  scale="1.2 1.2 1.2"/>
        <mesh name="{prefix}_knob_fr_vis" file="{assets}/knob_front_right.obj" scale="1.2 1.2 1.2"/>
        <mesh name="{prefix}_knob_rl_vis" file="{assets}/knob_rear_left.obj"   scale="1.2 1.2 1.2"/>
    </asset>
    """

    _children_raw = """
    <body name="{prefix}_main">
        <!-- visual shell -->
        <geom name="{prefix}_vis0" type="mesh" mesh="{prefix}_body_vis0"
              material="{prefix}_glass_mat" contype="0" conaffinity="0" group="0"/>
        <geom name="{prefix}_vis1" type="mesh" mesh="{prefix}_body_vis1"
              material="{prefix}_body_mat"  contype="0" conaffinity="0" group="0"/>

        <!-- collision hulls -->
        <geom name="{prefix}_core_col"  size="{sz_core}"  pos="0 0.024 -0.156"
              type="box" group="3" rgba="0.5 0 0 0.5"/>
        <geom name="{prefix}_lip_col"   size="{sz_lip}"   pos="0 0.324 0.42"
              type="box" group="3" rgba="0.5 0 0 0.5"/>
        <geom name="{prefix}_lip2_col"  size="{sz_lip2}"  pos="0 0.276 0.444"
              type="box" group="3" rgba="0.5 0 0 0.5"/>
        <geom name="{prefix}_plate_col" size="{sz_plate}" pos="-0.03 0.288 0.516"
              type="box" group="3" rgba="0.5 0 0 0.5"/>

        <!-- burner sites -->
        <site name="{prefix}_burner_fl" pos="-0.1824 -0.12 0.2676"
              size="0.12 0.00012" type="cylinder" rgba="0.5 0 0 0"/>
        <site name="{prefix}_burner_fr" pos="0.1824 -0.12 0.2676"
              size="0.12 0.00012" type="cylinder" rgba="0.5 0 0 0"/>
        <site name="{prefix}_burner_rl" pos="-0.2304 0.138 0.2676"
              size="0.084 0.00012" type="cylinder" rgba="0.5 0 0 0"/>
        <site name="{prefix}_burner_rr" pos="0.228 0.138 0.2676"
              size="0.084 0.00012" type="cylinder" rgba="0.5 0 0 0"/>
        <site name="{prefix}_burner_rc" pos="0 0.1284 0.2676"
              size="0.078 0.00012" type="cylinder" rgba="0.5 0 0 0"/>

        <!-- ============ five knobs (explicit, no helper) ============ -->
        <body name="{prefix}_knob_rc">
            <joint name="{prefix}_knob_rc_joint" pos="0.168 0.264 0.5124"
                   axis="0 1 0" damping="1"/>
            <geom name="{prefix}_knob_rc_vis" type="mesh" mesh="{prefix}_knob_rc_vis"
                  material="{prefix}_body_mat" contype="0" conaffinity="0" group="0"/>
            <geom name="{prefix}_knob_rc_col" type="box" size="{sz_knob}"
                  pos="0.168 0.264 0.5124" group="3" rgba="0.5 0 0 0.5"/>
        </body>

        <body name="{prefix}_knob_rr">
            <joint name="{prefix}_knob_rr_joint" pos="0.24 0.264 0.5124"
                   axis="0 1 0" damping="1"/>
            <geom name="{prefix}_knob_rr_vis" type="mesh" mesh="{prefix}_knob_rr_vis"
                  material="{prefix}_body_mat" contype="0" conaffinity="0" group="0"/>
            <geom name="{prefix}_knob_rr_col" type="box" size="{sz_knob}"
                  pos="0.24 0.264 0.5124" group="3" rgba="0.5 0 0 0.5"/>
        </body>

        <body name="{prefix}_knob_fl">
            <joint name="{prefix}_knob_fl_joint" pos="-0.312 0.264 0.5124"
                   axis="0 1 0" damping="1"/>
            <geom name="{prefix}_knob_fl_vis" type="mesh" mesh="{prefix}_knob_fl_vis"
                  material="{prefix}_body_mat" contype="0" conaffinity="0" group="0"/>
            <geom name="{prefix}_knob_fl_col" type="box" size="{sz_knob}"
                  pos="-0.312 0.264 0.5124" group="3" rgba="0.5 0 0 0.5"/>
        </body>

        <body name="{prefix}_knob_fr">
            <joint name="{prefix}_knob_fr_joint" pos="0.318 0.264 0.5124"
                   axis="0 1 0" damping="1"/>
            <geom name="{prefix}_knob_fr_vis" type="mesh" mesh="{prefix}_knob_fr_vis"
                  material="{prefix}_body_mat" contype="0" conaffinity="0" group="0"/>
            <geom name="{prefix}_knob_fr_col" type="box" size="{sz_knob}"
                  pos="0.318 0.264 0.5124" group="3" rgba="0.5 0 0 0.5"/>
        </body>

        <body name="{prefix}_knob_rl">
            <joint name="{prefix}_knob_rl_joint" pos="-0.24 0.264 0.5124"
                   axis="0 1 0" damping="1"/>
            <geom name="{prefix}_knob_rl_vis" type="mesh" mesh="{prefix}_knob_rl_vis"
                  material="{prefix}_body_mat" contype="0" conaffinity="0" group="0"/>
            <geom name="{prefix}_knob_rl_col" type="box" size="{sz_knob}"
                  pos="-0.24 0.264 0.5124" group="3" rgba="0.5 0 0 0.5"/>
        </body>
    </body>
    """

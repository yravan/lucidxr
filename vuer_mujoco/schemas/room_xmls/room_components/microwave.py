from vuer_mujoco.schemas.schema import Body


class KitchenMicrowave(Body):
    """
    Over-range microwave with a hinged glass panel door.

    VISUALS   (group 1): detailed OBJ meshes + grey plastic control panel
    COLLISIONS(group 3): five simple boxes that approximate the hull
    Door joint         : revolute about +Z (hinge at the left edge)
    """

    # ------------------------------------------------------------------
    # quick knobs
    # ------------------------------------------------------------------
    assets    = "microwave"                   # folder with png / obj files
    prefix    = "mw"                          # name prefix
    body_pos  = "4.96031 -1.534 1.59586"
    body_quat = "0.707105 0 0 -0.707108"

    # simplified hull blocks
    sz_top    = "0.384 0.0463918 0.239109"
    sz_back   = "0.384 0.172165 0.0435464"
    sz_left   = "0.0197938 0.172165 0.239109"
    sz_right  = "0.117179 0.172165 0.239109"
    sz_face   = "0.384 0.172165 0.0229608"

    # door handle
    sz_handle = "0.0174186 0.0927835"

    _attributes = {"name": prefix, "pos": body_pos, "quat": body_quat}

    # ------------------------------------------------------------------
    # <asset>
    # ------------------------------------------------------------------
    _preamble = """
    <asset>
        <texture type="2d" name="{prefix}_tex_0" file="{assets}/tex_2.png"/>
        <texture type="2d" name="{prefix}_tex_1" file="{assets}/tex_0.png"/>
        <texture type="2d" name="{prefix}_tex_2" file="{assets}/tex_1.png"/>

        <material name="{prefix}_mat_0" texture="{prefix}_tex_0" shininess="0.25"/>
        <material name="{prefix}_mat_1" texture="{prefix}_tex_1" shininess="0.25"/>
        <material name="{prefix}_mat_2" texture="{prefix}_tex_2" shininess="0.25"/>

        <!-- chassis meshes -->
        <mesh name="{prefix}_vis0" file="{assets}/model_0.obj" scale="0.791753 0.515464 0.791753"/>
        <mesh name="{prefix}_vis1" file="{assets}/model_1.obj" scale="0.791753 0.515464 0.791753"/>
        <mesh name="{prefix}_vis2" file="{assets}/model_2.obj" scale="0.791753 0.515464 0.791753"/>

        <!-- door meshes -->
        <mesh name="{prefix}_door0" file="{assets}/door_0.obj" scale="0.791753 0.515464 0.791753"/>
        <mesh name="{prefix}_door1" file="{assets}/door_1.obj" scale="0.791753 0.515464 0.791753"/>
        <mesh name="{prefix}_door2" file="{assets}/door_2.obj" scale="0.791753 0.515464 0.791753"/>
    </asset>
    """

    # ------------------------------------------------------------------
    # body tree
    # ------------------------------------------------------------------
    _children_raw = """
    <body name="{prefix}_main">
        <!-- detailed visual shell -->
        <geom name="{prefix}_g0" type="mesh" mesh="{prefix}_vis0" material="{prefix}_mat_1"
              contype="0" conaffinity="0" group="0"/>
        <geom name="{prefix}_g1" type="mesh" mesh="{prefix}_vis1" material="{prefix}_mat_2"
              contype="0" conaffinity="0" group="0"/>
        <geom name="{prefix}_g2" type="mesh" mesh="{prefix}_vis2" material="{prefix}_mat_0"
              contype="0" conaffinity="0" group="0"/>

        <!-- grey plastic control-panel frame -->
        <geom name="{prefix}_panel_top"  size="0.0752165 0.0170103 0.197938" pos="0.285031 -0.190206 0.0229608"
              type="box" contype="0" conaffinity="0" group="0" rgba="0.4 0.4 0.4 1"/>
        <geom name="{prefix}_panel_cap"  size="0.0752165 0.0154639 0.00870928" pos="0.285031 -0.186598 0.229608"
              type="box" contype="0" conaffinity="0" group="0" rgba="0.4 0.4 0.4 1"/>
        <geom name="{prefix}_panel_base" size="0.0752165 0.0154639 0.0134598" pos="0.285031 -0.187113 -0.188437"
              type="box" contype="0" conaffinity="0" group="0" rgba="0.4 0.4 0.4 1"/>

        <!-- simplified collision hull -->
        <geom name="{prefix}_col_top"   size="{sz_top}"   pos="0 0.216495 0"      type="box" group="3" rgba="0.5 0 0 0.5"/>
        <geom name="{prefix}_col_back"  size="{sz_back}"  pos="0 0 -0.196355"     type="box" group="3" rgba="0.5 0 0 0.5"/>
        <geom name="{prefix}_col_left"  size="{sz_left}"  pos="-0.364206 0 0"     type="box" group="3" rgba="0.5 0 0 0.5"/>
        <geom name="{prefix}_col_right" size="{sz_right}" pos="0.265237 0 0"      type="box" group="3" rgba="0.5 0 0 0.5"/>
        <geom name="{prefix}_col_face"  size="{sz_face}"  pos="0 0 0.216148"      type="box" group="3" rgba="0.5 0 0 0.5"/>

        <!-- green buttons -->
        <geom name="{prefix}_btn_start" size="0.0237526 0.011134 0.0197938"
              pos="0.336495 -0.198454 -0.102928" type="box" contype="0" conaffinity="0"
              group="0" rgba="0 0.5 0 0.5"/>
        <geom name="{prefix}_btn_stop"  size="0.0237526 0.011134 0.0197938"
              pos="0.237526 -0.198454 -0.102928" type="box" contype="0" conaffinity="0"
              group="0" rgba="0 0.5 0 0.5"/>

        <!-- interior tray (visual only) -->
        <geom name="{prefix}_tray" type="cylinder" size="0.143794 0.00395876"
              pos="-0.0950103 -0.0103093 -0.154392" contype="0" conaffinity="0"
              group="0" rgba="0 1 0 0.5"/>

        <body name="{prefix}_door">
            <joint name="{prefix}_hinge" pos="-0.384 -0.172165 0"
                   axis="0 0 1" limited="true" range="-1.57 0" damping="2"
                   frictionloss="2"/>

            <!-- door visuals -->
            <geom name="{prefix}_d0" type="mesh" mesh="{prefix}_door0" material="{prefix}_mat_1"
                  contype="0" conaffinity="0" group="0"/>
            <geom name="{prefix}_d1" type="mesh" mesh="{prefix}_door1" material="{prefix}_mat_2"
                  contype="0" conaffinity="0" group="0"/>
            <geom name="{prefix}_d2" type="mesh" mesh="{prefix}_door2" material="{prefix}_mat_0"
                  contype="0" conaffinity="0" group="0"/>

            <!-- collision slab + handle -->
            <geom name="{prefix}_door_col" size="0.278618 0.0190722 0.220899"
                  pos="-0.0712577 -0.191237 0.0182103" type="box" group="3"
                  rgba="0.5 0 0 0.5"/>
            <geom name="{prefix}_handle" type="cylinder" size="{sz_handle}"
                  pos="0.161518 -0.24433 0.0308784" group="3" rgba="0.5 0 0 0.5"/>

            <!-- mounting pins (visual) -->
            <geom name="{prefix}_pin_top_v" size="0.0213773 0.0242268 0.0166268"
                  pos="0.161518 -0.233505 0.186854" type="box"
                  contype="0" conaffinity="0" group="0" rgba="0.5 0 0 0.5"/>
            <geom name="{prefix}_pin_bot_v" size="0.0213773 0.0242268 0.0166268"
                  pos="0.161518 -0.233505 -0.125889" type="box"
                  contype="0" conaffinity="0" group="0" rgba="0.5 0 0 0.5"/>
        </body>
    </body>
    """

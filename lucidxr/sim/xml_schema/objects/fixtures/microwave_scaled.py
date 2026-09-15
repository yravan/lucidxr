from lucidxr.sim.xml_schema.schema import Body


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
    assets = "objects/microwave"  # folder with png / obj files
    prefix = "mw"  # name prefix
    body_pos = "4.96031 -1.534 1.59586"
    body_quat = "0.707105 0 0 -0.707108"

    # simplified hull blocks
    sz_top = "0.2688 0.03247426 0.16737629999999998"
    sz_back = "0.2688 0.1205155 0.030482479999999996"
    sz_left = "0.013855659999999999 0.1205155 0.16737629999999998"
    sz_right = "0.0820253 0.1205155 0.16737629999999998"
    sz_face = "0.2688 0.1205155 0.01607256"

    # door handle
    sz_handle = "0.012193019999999999 0.06494845"

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
        <mesh name="{prefix}_vis0" file="{assets}/model_0.obj" scale="0.5542271 0.3608248 0.5542271"/>
        <mesh name="{prefix}_vis1" file="{assets}/model_1.obj" scale="0.5542271 0.3608248 0.5542271"/>
        <mesh name="{prefix}_vis2" file="{assets}/model_2.obj" scale="0.5542271 0.3608248 0.5542271"/>

        <!-- door meshes -->
        <mesh name="{prefix}_door0" file="{assets}/door_0.obj" scale="0.5542271 0.3608248 0.5542271"/>
        <mesh name="{prefix}_door1" file="{assets}/door_1.obj" scale="0.5542271 0.3608248 0.5542271"/>
        <mesh name="{prefix}_door2" file="{assets}/door_2.obj" scale="0.5542271 0.3608248 0.5542271"/>
    </asset>
    """

    # ------------------------------------------------------------------
    # body tree
    # ------------------------------------------------------------------
    _children_raw = """
    <body name="{prefix}_main">
        <site name="{prefix}_site" pos="0 0 0" size="0.02"/>
        <!-- detailed visual shell -->
        <geom name="{prefix}_g0" type="mesh" mesh="{prefix}_vis0" material="{prefix}_mat_1"
              contype="0" conaffinity="0" group="0"/>
        <geom name="{prefix}_g1" type="mesh" mesh="{prefix}_vis1" material="{prefix}_mat_2"
              contype="0" conaffinity="0" group="0"/>
        <geom name="{prefix}_g2" type="mesh" mesh="{prefix}_vis2" material="{prefix}_mat_0"
              contype="0" conaffinity="0" group="0"/>

        <!-- grey plastic control-panel frame -->
        <geom name="{prefix}_panel_top"  size="0.05265155 0.011907209999999998 0.1385566" pos="0.19952169999999997 -0.1331442 0.01607256"
              type="box" contype="0" conaffinity="0" group="0" rgba="0.4 0.4 0.4 1"/>
        <geom name="{prefix}_panel_cap"  size="0.05265155 0.01082473 0.006096496" pos="0.19952169999999997 -0.1306186 0.1607256"
              type="box" contype="0" conaffinity="0" group="0" rgba="0.4 0.4 0.4 1"/>
        <geom name="{prefix}_panel_base" size="0.05265155 0.01082473 0.009421859999999999" pos="0.19952169999999997 -0.1309791 -0.1319059"
              type="box" contype="0" conaffinity="0" group="0" rgba="0.4 0.4 0.4 1"/>

        <!-- simplified collision hull -->
        <geom name="{prefix}_col_top"   size="{sz_top}"   pos="0.0 0.15154649999999997 0.0"      type="box" group="3" rgba="0.5 0 0 0.5"/>
        <geom name="{prefix}_col_back"  size="{sz_back}"  pos="0.0 0.0 -0.1374485"     type="box" group="3" rgba="0.5 0 0 0.5"/>
        <geom name="{prefix}_col_left"  size="{sz_left}"  pos="-0.25494419999999995 0.0 0.0"     type="box" group="3" rgba="0.5 0 0 0.5"/>
        <geom name="{prefix}_col_right" size="{sz_right}" pos="0.1856659 0.0 0.0"      type="box" group="3" rgba="0.5 0 0 0.5"/>
        <geom name="{prefix}_col_face"  size="{sz_face}"  pos="0.0 0.0 0.15130359999999998"      type="box" group="3" rgba="0.5 0 0 0.5"/>

        <!-- green buttons -->
        <geom name="{prefix}_btn_start" size="0.016626819999999997 0.007793799999999999 0.013855659999999999"
              pos="0.23554649999999996 -0.13891779999999998 -0.0720496" type="box" contype="0" conaffinity="0"
              group="0" rgba="0 0.5 0 0.5"/>
        <geom name="{prefix}_btn_stop"  size="0.016626819999999997 0.007793799999999999 0.013855659999999999"
              pos="0.16626819999999998 -0.13891779999999998 -0.0720496" type="box" contype="0" conaffinity="0"
              group="0" rgba="0 0.5 0 0.5"/>

        <!-- interior tray (visual only) -->
        <geom name="{prefix}_tray" type="cylinder" size="0.1006558 0.002771132"
              pos="-0.06650721 -0.00721651 -0.1080744" contype="0" conaffinity="0"
              group="0" rgba="0 1 0 0.5"/>

        <body name="{prefix}_door">
            <joint name="{prefix}_hinge" pos="-0.2688 -0.1205155 0.0"
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
            <geom name="{prefix}_door_col" size="0.19503259999999997 0.01335054 0.1546293"
                  pos="-0.04988038999999999 -0.13386589999999998 0.012747209999999998" type="box" group="3"
                  rgba="0.5 0 0 0.5"/>
            <geom name="{prefix}_handle" type="cylinder" size="{sz_handle}"
                  pos="0.11306259999999999 -0.171031 0.02161488" group="3" rgba="0.5 0 0 0.5"/>

            <!-- mounting pins (visual) -->
            <geom name="{prefix}_pin_top_v" size="0.014964109999999997 0.01695876 0.01163876"
                  pos="0.11306259999999999 -0.16345349999999997 0.1307978" type="box"
                  contype="0" conaffinity="0" group="0" rgba="0.5 0 0 0.5"/>
            <geom name="{prefix}_pin_bot_v" size="0.014964109999999997 0.01695876 0.01163876"
                  pos="0.11306259999999999 -0.16345349999999997 -0.0881223" type="box"
                  contype="0" conaffinity="0" group="0" rgba="0.5 0 0 0.5"/>
        </body>
    </body>
    """

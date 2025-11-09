from vuer_mujoco.schemas.schema import Body


class KitchenSinkWide(Body):
    # folder that holds texture / mesh files
    assets = "sink_wide"
    # short prefix used to generate unique MJCF names
    prefix = "sink-wide"
    # convenient geometry sizes (taken from your MJCF snippet)
    size_bottom = "0.2717647 0.2070588 0.0097059"      # bowl floor
    size_wall   = "0.2976471 0.2070588 0.0776471"      # tapered side-walls
    size_lip    = "0.3235294 0.0440000 0.0045294"      # thin surface rim
    size_spout  = "0.0220000"                          # radius of spout / valve
    size_handle = "0.0148824 0.0841176 0.0042059"      # rectangular handle bar

    # where to drop the sink in the world
    _attributes = {
        "name": f"{prefix}",
        "pos":  "0.295 -1.7303 0.9381",   # same as in the MJCF you showed
    }

    # ---------------------------------------------------------------------- #
    # 1) <asset> section: textures, materials, visual meshes
    # ---------------------------------------------------------------------- #
    _preamble = """
    <asset>
        <texture type="2d" name="{prefix}_tex_model"  file="{assets}/image0.png"/>
        <texture type="2d" name="{prefix}_tex_sink"   file="{assets}/image0.png"/>

        <material name="{prefix}_model_mat" texture="{prefix}_tex_model" reflectance="0.5"/>
        <material name="{prefix}_sink_mat"  texture="{prefix}_tex_sink"  shininess="0.25"/>

        <mesh name="{prefix}_bowl_vis"    file="{assets}/model_0.obj"  scale="0.647059 0.647059 0.647059"/>
        <mesh name="{prefix}_spout_vis"   file="{assets}/spout_0.obj"  scale="0.647059 0.647059 0.647059"/>
        <mesh name="{prefix}_handle_vis"  file="{assets}/handle_0.obj" scale="0.647059 0.647059 0.647059"/>
    </asset>
    """

    # ---------------------------------------------------------------------- #
    # 2) <body> hierarchy: collision boxes, joints, etc.
    # ---------------------------------------------------------------------- #
    _children_raw = """
    <body name="{prefix}_main">
        <geom name="{prefix}_bowl_vis"
              type="mesh"      mesh="{prefix}_bowl_vis"
              material="{prefix}_sink_mat"
              density="100"    friction="0.95 0.3 0.1"
              contype="0"      conaffinity="0"
              solref="0.001"   solimp="0.998 0.998"/>

<geom name="{prefix}_bottom"  type="box"
              pos="0.0 -0.02588235294117647 -0.16823529411764707"   size="0.27176470588235296 0.20705882352941177 0.009705882352941177"
              group="3" rgba="0 0 1 .15"/>

        <!-- left / right walls (thin plates) -->
        <geom name="{prefix}_wall_left"  type="box"
              pos="-0.2911764705882353 -0.02588235294117647 -0.09382352941176471" size="0.009705882352941177 0.20705882352941177 0.07764705882352942"
              axisangle="0 1 0 -0.17"
              group="3" rgba="0 0 1 .15"/>

        <geom name="{prefix}_wall_right" type="box"
              pos="0.2911764705882353 -0.02588235294117647 -0.09382352941176471" size="0.009705882352941179 0.20705882352941177 0.07764705882352943"
              axisangle="0 1 0  0.17"
              group="3" rgba="0 0 1 .15"/>

        <!-- front / rear walls (thin plates) -->
        <geom name="{prefix}_wall_front" type="box"
              pos="0.0 -0.24264705882352944 -0.09382352941176471" size="0.29764705882352943 0.00970588235294118 0.07764705882352942"
              axisangle="1 0 0  0.10"
              group="3" rgba="0 0 1 .15"/>

        <geom name="{prefix}_wall_back"  type="box"
              pos="0.0 0.18764705882352942 -0.09382352941176471" size="0.29764705882352943 0.00970588235294118 0.07764705882352942"
              axisangle="1 0 0 -0.10"
              group="3" rgba="0 0 1 .15"/>

        <!-- thin lip (just for small contact on the countertop) -->
        <geom name="{prefix}_lip_front" type="box"
              pos="0.0 -0.24264705882352944 -0.09382352941176471"    size="0.300 0.010 0.0045"
              group="3" rgba="0 0 1 .15"/>

        <geom name="{prefix}_lip_back"  type="box"
              pos="0.0 0.2303529411764706 -0.022647058823529416"    size="0.300 0.040 0.0045"
              group="3" rgba="0 0 1 .15"/>

        <geom name="{prefix}_lip_left"  type="box"
              pos="-0.31058823529411766 0.0 -0.022647058823529416"    size="0.010 0.235 0.0045"
              group="3" rgba="0 0 1 .15"/>

        <geom name="{prefix}_lip_right" type="box"
              pos="0.31058823529411766 0.0 -0.022647058823529416"    size="0.010 0.235 0.0045"
              group="3" rgba="0 0 1 .15"/>

        <body name="{prefix}_spout">
            <joint name="{prefix}_spout_joint" type="hinge"
                   pos="0 0.2381176 0.0291176" axis="0 0 1"
                   range="-1.57 1.57" damping="10"/>
            <geom name="{prefix}_spout_vis" type="mesh" mesh="{prefix}_spout_vis"
                  material="{prefix}_sink_mat" density="100"
                  solref="0.001" solimp="0.998 0.998"/>
            <geom name="{prefix}_spout_col" type="cylinder"
                  pos="0 0.2381176 0.0291176" size="{size_spout} {size_spout}"
                  group="3" rgba="0 1 0 0.15"/>
        </body>

        <body name="{prefix}_handle">
            <joint name="{prefix}_handle_joint" type="hinge"
                   pos="0 0.2381176 0.0711765" axis="-1 0 0"
                   range="0 0.52" damping="10"/>
            <joint name="{prefix}_temp_joint"   type="hinge"
                   pos="0 0.2381176 0.0753824" axis="0 0 1"
                   range="-0.79 0.79" damping="50"/>

            <geom name="{prefix}_handle_vis" type="mesh" mesh="{prefix}_handle_vis"
                  material="{prefix}_sink_mat"
                  contype="0" conaffinity="0" density="100"
                  friction="0.95 0.3 0.1" solref="0.001" solimp="0.998 0.998"/>
            <geom name="{prefix}_handle_bar" type="box"
                  pos="0 0.1895882 0.134588" size="{size_handle}"
                  axisangle="1 0 0 -0.63"
                  group="3" rgba="0 1 0 0.15"/>
            <geom name="{prefix}_handle_pivot" type="cylinder"
                  pos="0 0.2381176 0.0753824" size="{size_spout} 0.0106765"
                  axisangle="1 0 0 0.17"
                  group="3" rgba="0 1 0 0.15"/>
        </body>
        <!-- Sites for 8 corners -->
        <site name="{prefix}_corner_1" pos="-0.3106 -0.235 -0.178" size="0.05" rgba="1 0 0 0"/>
        <site name="{prefix}_corner_2" pos=" 0.3106 -0.235 -0.178" size="0.05" rgba="1 0 0 0"/>
        <site name="{prefix}_corner_3" pos="-0.3106  0.235 -0.178" size="0.05" rgba="1 0 0 0"/>
        <site name="{prefix}_corner_4" pos=" 0.3106  0.235 -0.178" size="0.05" rgba="1 0 0 0"/>
        <site name="{prefix}_corner_5" pos="-0.3106 -0.235 -0.0181" size="0.05" rgba="0 1 0 0"/>
        <site name="{prefix}_corner_6" pos=" 0.3106 -0.235 -0.0181" size="0.05" rgba="0 1 0 0"/>
        <site name="{prefix}_corner_7" pos="-0.3106  0.235 -0.0181" size="0.05" rgba="0 1 0 0"/>
        <site name="{prefix}_corner_8" pos=" 0.3106  0.235 -0.0181" size="0.05" rgba="0 1 0 0"/>
    </body>
    """


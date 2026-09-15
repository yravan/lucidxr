from lucidxr.sim.xml_schema.schema import Body


class KitchenSink(Body):
    assets = "concrete-sink"
    prefix = "sink"
    size_bottom = "0.183333 0.22 0.0114583"
    size_wall = "0.238333 0.275 0.099"
    size_spout = "0.0183333 0.0733333"
    size_handle = "0.01375 0.0275 0.0275"

    _attributes = {
        "name": "sink",
        "pos": "3.05 -0.30 0.96125",
    }

    _preamble = """
    <asset>
        <texture type="2d" name="{prefix}_tex_model" file="{assets}/material_0.png"/>
        <texture type="2d" name="{prefix}_tex_image0" file="{assets}/image0.png"/>

        <material name="{prefix}_model_mat" texture="{prefix}_tex_model" reflectance="0.5"/>
        <material name="{prefix}_sink_mat"  texture="{prefix}_tex_image0" shininess="0.25"/>

        <mesh name="{prefix}_model_0_vis"   file="{assets}/model_0.obj"   scale="0.916667 0.916667 0.916667"/>
        <mesh name="{prefix}_spout_0_vis"   file="{assets}/spout_0.obj"   scale="0.916667 0.916667 0.916667"/>
        <mesh name="{prefix}_handle_0_vis"  file="{assets}/handle_0.obj"  scale="0.916667 0.916667 0.916667"/>
    </asset>
    """

    _children_raw = """
    <body name="{prefix}_group">
        <geom name="{prefix}_bowl_vis" type="mesh" mesh="{prefix}_model_0_vis" material="{prefix}_sink_mat" contype="0" conaffinity="0" friction="0.95 0.3 0.1" density="100" solref="0.001" solimp="0.998 0.998"/>

        <geom name="{prefix}_bottom" size="{size_bottom}" pos="0.22 0 -0.238333" type="box" group="3" rgba="0.5 0 0 0.5"/>
        <geom name="{prefix}_rear_wall" size="{size_wall}"  pos="-0.210833 0 -0.1375" type="box" group="3" rgba="0.5 0 0 0.5"/>

        <geom name="{prefix}_drain" size="0.0320833 0.055" pos="-0.00916667 0.224583 0.00916667" type="cylinder" group="3" rgba="0.5 0 0 0.5"/>

        <body name="{prefix}_spout">
            <joint name="{prefix}_spout_joint" pos="-0.00825 0.2255 0.146667" axis="0 0 1" damping="10"/>
            <geom name="{prefix}_spout_vis" type="mesh" mesh="{prefix}_spout_0_vis" material="{prefix}_sink_mat" contype="0" conaffinity="0" friction="0.95 0.3 0.1" density="100" solref="0.001" solimp="0.998 0.998"/>
            <geom name="{prefix}_spout_col" type="cylinder" size="{size_spout}" pos="-0.00825 0.2255 0.146667" group="3" rgba="0.5 0 0 0.5"/>
        </body>

        <body name="{prefix}_handle">
            <joint name="{prefix}_handle_joint"
                   pos="0.055 0.2255 0.0366667" axis="0 1 0" range="0 0.52" damping="10"/>
            <joint name="{prefix}_handle_temp_joint"
                   pos="0.055 0.2255 0.0155833" axis="1 0 0" range="-0.785 0.785" damping="50"/>

            <geom name="{prefix}_handle_vis"
                  type="mesh" mesh="{prefix}_handle_0_vis" material="{prefix}_sink_mat"
                  contype="0" conaffinity="0"
                  friction="0.95 0.3 0.1" density="100" solref="0.001" solimp="0.998 0.998"/>
            <geom name="{prefix}_handle_base"
                  type="box" size="{size_handle}" pos="0.06875 0.2255 0.0155833" group="3"
                  rgba="0.5 0 0 0.5"/>
            <geom name="{prefix}_handle_main" type="cylinder" size="0.00916667 0.0275" pos="0.0733333 0.2255 0.0733333" group="3" rgba="0.5 0 0 0.5"/>
        </body>
    </body>
    """

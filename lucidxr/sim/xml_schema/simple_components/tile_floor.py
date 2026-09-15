from lucidxr.sim.xml_schema.schema import Body


class TileFloor(Body):
    _attributes = {
        "name": "tile_floor",
    }
    _preamble = """
    <asset>
        <texture builtin="gradient" height="256" rgb1=".9 .9 1." rgb2=".2 .3 .4" type="skybox" width="256"/>
        <texture file="textures/light-gray-floor-tile.png" type="2d" name="texplane"/>
        <material name="floorplane" reflectance="0.01" shininess="0.0" specular="0.0" texrepeat="2 2" texture="texplane" texuniform="true"/>
      </asset>
    """
    _children_raw = """
    <body name="floor">
        <geom condim="3" group="1" material="floorplane" name="floor" pos="0 0 0" size="10 10 .125" type="plane"/>
    </body>
    """

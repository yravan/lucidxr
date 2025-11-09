from vuer_mujoco.schemas.schema import Body

class PlainRoom(Body):
    _attributes = {
        "name": "plain_room"
    }

    # This sets up a single material for the floor and the walls.
    _preamble = """
        <asset>
        <material name="{name}-wall" rgba="0.5 0.5 0.5 1" shininess="0.1"/>
        <material name="{name}-floor" rgba="0.1 0.2 0.3 1" shininess="0.1"/>
        </asset>
    """

    _children_raw = """
        <!-- Floor -->
        <geom name="{name}-floor" type="plane" material="{name}-floor" 
            size="2 2 0.1" pos="0 0 0"/>
        
        <!-- North Wall -->
        <geom name="{name}-wall-north" type="box" material="{name}-wall"
            size="2 0.1 1.5" pos="0 2 1"/>
        <!-- South Wall -->
        <geom name="{name}-wall-south" type="box" material="{name}-wall"
            size="2 0.1 1.5" pos="0 -2 1"/>
        <!-- West Wall -->
        <geom name="{name}-wall-west" type="box" material="{name}-wall"
            size="0.1 2 1.5" pos="-2 0 1"/>
    """
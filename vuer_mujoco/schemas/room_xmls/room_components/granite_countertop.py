from vuer_mujoco.schemas.schema import Body


class GraniteCountertop(Body):
    assets = "granite-countertop"
    size = "0.5 0.5 0.05"
    prefix = "gr-countertop"

    _attributes = {
        "name": "granite-countertop",
    }
    _preamble = """
    <asset>
        <texture type="2d" name="{prefix}-marble" file="{assets}/marble.png"/>
        <material name="{prefix}-granite" texture="{prefix}-marble" texuniform="true" texrepeat="3 3" shininess="0.1" reflectance="0.1"/>
    </asset>
    """
    _children_raw = """
        <geom name="{name}_main_main_group_top_left_visual" size="{size}" type="box" contype="0" conaffinity="0" mass="0" material="{prefix}-granite"/>
        <geom name="{name}_main_main_group_top_left_0" size="{size}" type="box" density="10" group="3" rgba="0.5 0 0 1"/>
    """

from vuer_mujoco.schemas.schema import Body


class Ball(Body):
    size = 0.03
    rgba = "1 0 0 0.1"

    _attributes = {
        "name": "ball",
    }
    _children_raw = """
    <joint type="free" name="{name}"/>
    <geom name="{name}-sphere" type="sphere" size="{size}" rgba="{rgba}" mass="0.01" condim="4" solimp="0.998 0.998 0.001" solref="0.001 1" friction="10 0.3 0.1" density="50"/>
    <site name="{name}" pos="0 0 0" size="0.01" rgba="1 0 0 0" type="sphere"/>
    """

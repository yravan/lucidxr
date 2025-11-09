from ..schema import Body


class Placeholder(Body):
    """A zero-sized object with no collision detection used as a placeholder.

    This class represents a minimal geometric object with negligible dimensions (0.0001)
    and disabled collision detection (contype=0, conaffinity=0). It is used when a
    physical presence is needed without affecting dynamics or collisions, ensuring
    qpos and qvel states remain unchanged.

    **Note**: can NOT use singleton b/c geom name.
    """

    rgba = "0.8 0.8 0.8 0"
    group = "5"
    width = 0.1
    height = 0.1
    thickness = 0.1

    _attributes = dict(name="placeholder")

    # use {childclass} when you want to use defaults. Just {name}- if no
    # defaults are involved.
    # todo: how do I make sure it has collision? what about friction?
    _children_raw = """
    <geom name="{name}-placeholder" type="box" group="{group}" size="{width} {height} {thickness}" pos="{pos}"
        contype="0" conaffinity="0"
    />
    """

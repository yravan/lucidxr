import random

from vuer_mujoco.schemas.schema import Body


class ObjaverseMujocoBowl(Body):
    """
    Generic MJCF wrapper for an Objaverse bowl.

    Parameters
    ----------
    name : str
        Prefix used inside MJCF for mesh / geom names.
    assets : str
        Folder that contains the `visual` and `collision` sub-folders.
    collision_count : int
        How many collision OBJ files to include.
    visual_count : int
        How many visual OBJ files (usually 1).
    scale : float
        Uniform scale applied to every mesh (default 0.13 = 13 cm diameter bowl).
    randomize_colors : bool
        If True, each collision geom gets a random RGBA so you can
        see them in the viewer.
    """

    def __init__(
        self,
        name: str = "bowl",
        assets: str = "objects",
        collision_count: int = 32,
        visual_count: int = 1,
        scale: float = 0.13,
        randomize_colors: bool = True,
        # Body-level kwargs ---------------------------------------------------
        pos=None,
        quat=None,
        attributes=None,
        **kwargs,
    ):
        # call Body.__init__ --------------------------------------------------
        super().__init__(pos=pos, quat=quat, attributes=attributes or {}, **kwargs)
        self.collision_count = collision_count

        # store for string-formatting later
        self._attributes["name"] = name
        self.assets = assets
        self.visual_count = visual_count
        self.collision_count = collision_count
        self.randomize_colors = randomize_colors

        # ------------------------------------------------------------------ #
        # 1) <asset> section  (visual + collision meshes + materials)
        # ------------------------------------------------------------------ #
        visual_meshes = "\n".join(
            f'<mesh name="{name}_vis_{i}" '
            f'file="{assets}/visual/model_normalized_{i}.obj" '
            f'scale="{scale} {scale} {scale}"/>'
            for i in range(visual_count)
        )

        collision_meshes = "\n".join(
            f'<mesh name="{name}_coll_{i}" '
            f'file="{assets}/collision/model_normalized_collision_{i}.obj" '
            f'scale="{scale} {scale} {scale}"/>'
            for i in range(collision_count)
        )

        self._preamble = f"""
        <default>
            <default class="{name}_visual">
                <geom type="mesh" contype="0" conaffinity="0"
                      friction="0.95 0.3 0.1" density="100"
                      solimp="0.998 0.998 0.001" solref="0.001 1"/>
            </default>
            <default class="{name}_collision">
                <geom type="mesh" group="3"
                      friction="0.95 0.3 0.1" density="100"
                      solimp="0.998 0.998 0.001" solref="0.001 1"/>
            </default>
        </default>

        <asset>
            {visual_meshes}
            {collision_meshes}
            <texture type="2d" name="{name}_tex" file="{assets}/visual/image0.png"/>
            <material name="{name}_mat" texture="{name}_tex" shininess="0.25"/>
        </asset>
        """.strip()

        # ------------------------------------------------------------------ #
        # 2) <body> section  (free joint + geoms)
        # ------------------------------------------------------------------ #
        # visual geoms
        visual_geoms = "\n".join(
            f'    <geom mesh="{name}_vis_{i}" material="{name}_mat" class="{name}_visual"/>'
            for i in range(visual_count)
        )

        # collision geoms
        collision_geoms = ""
        for i in range(collision_count):
            rgba = (
                f"{random.random()} {random.random()} {random.random()} 1"
                if randomize_colors
                else "0.8 0.8 0.8 1"
            )
            collision_geoms += (
                f'    <geom name="{name}_coll_{i}_mesh" mesh="{name}_coll_{i}" rgba="{rgba}" class="{name}_collision"/>\n'
            )

        self._children_raw = f"""
        <joint name="{name}_joint" type="free"/>
        {visual_geoms}
        {collision_geoms.rstrip()}
        <site name="{name}" pos="0 0 0" size="0.01" rgba="1 1 1 0"/>
        """.strip()
        super().__init__(pos=pos, quat=quat, attributes=attributes or {}, **kwargs)


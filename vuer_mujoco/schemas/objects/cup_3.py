import random

from vuer_mujoco.schemas.schema import Body


class ObjaverseMujocoCup(Body):
    """
    Generic Objaverse cup -- one visual mesh + many collision meshes.

    Parameters
    ----------
    name : str
        Prefix used for every MJCF name (geom / mesh / joint / class, …).
    assets : str
        Folder that contains the `visual/` + `collision/` sub-directories.
    collision_count : int
        How many collision OBJ files are present in `collision/`.
    visual_count : int
        How many visual OBJ files are present in `visual/` (usually 1).
    randomize_colors : bool
        If True each collision geom gets a random debug color (handy!).
    scale : float
        OBJ scale factor (taken straight from the XML: 0.105 m).
    """

    def __init__(
        self,
        name: str = "cup",
        assets: str = "cup_assets",
        collision_count: int = 32,
        visual_count: int = 1,
        randomize_colors: bool = True,
        scale: float = 0.105,
        # forward anything else to Body.__init__
        pos=None,
        quat=None,
        attributes=None,
        **kwargs,
    ):
        super().__init__(pos=pos, quat=quat, attributes=attributes or {}, **kwargs)
        self._attributes["name"] = name
        self.collision_count = collision_count

        # ------------------------------------------------------------------ #
        # 1) <asset> section – meshes, textures, materials
        # ------------------------------------------------------------------ #
        visual_meshes = ""
        for i in range(visual_count):
            visual_meshes += (
                f'<mesh name="{name}_vis_{i}" '
                f'file="{assets}/visual/model_normalized_{i}.obj" '
                f'scale="{scale} {scale} {scale}"/>\n'
            )

        collision_meshes = ""
        for i in range(collision_count):
            collision_meshes += (
                f'<mesh name="{name}_coll_{i}" '
                f'file="{assets}/collision/model_normalized_collision_{i}.obj" '
                f'scale="{scale} {scale} {scale}"/>\n'
            )

        # simple matte material (tweak as you like)
        material = (
            f'<material name="{name}_mat" specular="0.5" shininess="0.0" '
            f'rgba="0.1 0.5 0.03 1"/>'
        )

        self._preamble = f"""
        <default>
            <default class="{name}_visual">
                <geom type="mesh" contype="0" conaffinity="0"
                      density="100" friction="2.0 0.3 0.1"
                      solref="0.001 1" solimp="0.998 0.998 0.001"/>
            </default>
            <default class="{name}_collision">
                <geom type="mesh" group="3"
                      density="100" friction="2.0 0.3 0.1"
                      solref="0.001 1" solimp="0.998 0.998 0.001"/>
            </default>
        </default>
        <asset>
        {visual_meshes}
        {collision_meshes}
            <material name="{name}_mat" specular="0.5" shininess="0.0"
                      rgba="0.1 0.3 0.2 1.0"/>
        </asset>
        """.strip()


        # ------------------------------------------------------------------ #
        # 2) <body> – joint + geoms
        # ------------------------------------------------------------------ #
        # visual geoms
        visual_geoms = ""
        for i in range(visual_count):
            visual_geoms += (
                f'    <geom name="{name}_vis_{i}_mesh" mesh="{name}_vis_{i}" material="{name}_mat" '
                f'class="{name}_visual"/>\n'
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
                f'    <geom name="{name}_coll_{i}_mesh" mesh="{name}_coll_{i}" rgba="{rgba}" '
                f'class="{name}_collision"/>\n'
            )

        self._children_raw = (
            f"""
        <joint name="{name}_joint" type="free"/>
        {visual_geoms}
        {collision_geoms.rstrip()}
        <site name="{name}" pos="0 0 0" size="0.01" rgba="1 1 1 0"/>
        """.strip()
        )

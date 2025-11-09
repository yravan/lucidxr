import random
from vuer_mujoco.schemas.schema import Body


class ObjaverseMujocoSpoon(Body):
    """
    Generic MJCF wrapper for an Objaverse spoon.

    Parameters
    ----------
    name : str
        Prefix used for every MJCF asset (default ``spoon``).
    assets : str
        Directory that contains the `visual/` and `collision/` sub–folders.
    visual_count : int
        Number of visual OBJ files (this spoon has 2).
    collision_count : int
        Number of collision OBJ files (32 for the dump you pasted).
    scale : float
        Uniform mesh scale (default 0.18 ≈ 18 cm spoon).
    randomize_colors : bool
        Whether to give each collision geom a random transparent color
        so you can see them in the viewer.
    """

    def __init__(
        self,
        name: str = "spoon",
        assets: str = "objects",
        visual_count: int = 2,
        collision_count: int = 32,
        scale: float = 0.18,
        randomize_colors: bool = True,
        # ---- Body-level kwargs --------------------------------------------
        pos=None,
        quat=None,
        attributes=None,
        **kwargs,
    ):
        super().__init__(pos=pos, quat=quat, attributes=attributes or {}, **kwargs)

        # Stash a few values for str.format
        self._attributes["name"] = name
        self.assets = assets
        self.visual_count = visual_count
        self.collision_count = collision_count
        self.randomize_colors = randomize_colors

        # ------------------------------------------------------------------ #
        # 1) <asset>  (all meshes, textures, materials)
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

        # two textures / materials (handle & bowl)
        self._preamble = f"""
        <default>
            <default class="{name}_visual">
                <geom type="mesh" contype="0" conaffinity="0"
                      density="100" friction="0.95 0.3 0.1"
                      solimp="0.998 0.998 0.001" solref="0.001 1"/>
            </default>
            <default class="{name}_collision">
                <geom type="mesh" group="3"
                      density="100" friction="0.95 0.3 0.1"
                      solimp="0.998 0.998 0.001" solref="0.001 1"/>
            </default>
        </default>

        <asset>
            {visual_meshes}
            {collision_meshes}

            <!-- textures pulled straight from your MJCF -->
            <texture type="2d" name="{name}_tex0" file="{assets}/visual/image1.png"/>
            <texture type="2d" name="{name}_tex1" file="{assets}/visual/image3.png"/>

            <material name="{name}_mat_bowl"   texture="{name}_tex0" shininess="0.25"/>
            <material name="{name}_mat_handle" texture="{name}_tex1" shininess="0.25"/>
        </asset>
        """.strip()

        # ------------------------------------------------------------------ #
        # 2) <body>  (free-joint + geoms)
        # ------------------------------------------------------------------ #
        # visual geoms: first mesh is the handle, second is the bowl
        visual_geoms = [
            f'<geom mesh="{name}_vis_0" material="{name}_mat_handle" class="{name}_visual"/>',
            f'<geom mesh="{name}_vis_1" material="{name}_mat_bowl"   class="{name}_visual"/>',
        ]

        # collision geoms
        collision_geoms = ""
        for i in range(collision_count):
            rgba = (
                f"{random.random()} {random.random()} {random.random()} 0.3"
                if randomize_colors
                else "0.8 0.8 0.8 1"
            )
            collision_geoms += (
                f'<geom mesh="{name}_coll_{i}" rgba="{rgba}" class="{name}_collision"/>'
            )

        # glue everything together
        self._children_raw = f"""
        <site name="{name}_site" pos="0 0 0" size="0.02"/>
        <joint name="{name}_joint" type="free"/>
        {visual_geoms}
        {collision_geoms.rstrip()}
        """.strip()

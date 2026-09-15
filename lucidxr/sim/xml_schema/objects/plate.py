import random

from lucidxr.sim.xml_schema.schema import Body


class ObjaverseMujoco(Body):
    def __init__(
        self,
        name="object",
        assets="objects",
        collision_count=0,
        visual_count=1,
        randomize_colors=True,
        seed=0,
        scale=0.185,
        # Add these to match Body's signature
        pos=None,
        quat=None,
        attributes=None,
        **kwargs,
    ):
        # Forward pos, quat, attributes, and any other leftover kwargs to Body.__init__
        rng = random.Random(seed)
        super().__init__(pos=pos, quat=quat, attributes=attributes or {}, **kwargs)

        # Now do your custom logic
        self._attributes["name"] = name
        self.assets = assets
        self.visual_count = visual_count
        self.collision_count = collision_count
        self.randomize_colors = randomize_colors

        # Build the <asset> lines for the visual meshes
        visual_meshes_str = ""
        for i in range(visual_count):
            visual_meshes_str += f'<mesh name="{name}-model_visual_{i}" file="{assets}/visual/model_normalized_{i}.obj" scale="{scale} {scale} {scale}"/>\n'

        # Build the <mesh> lines for the collision meshes
        collision_meshes_str = ""
        for i in range(collision_count):
            collision_meshes_str += f'<mesh name="{name}-model_collision_{i}" file="{assets}/collision/model_normalized_collision_{i}.obj" scale="{scale} {scale} {scale}"/>\n'

        # Save that snippet in our preamble along with texture/material lines
        self._preamble = f"""
            <default>
                <default class="{name}-obj-visual">
                    <geom solimp="0.998 0.998 0.001" solref="0.001 1" density="100" friction="0.95 0.3 0.1" group="0" type="mesh" contype="0" conaffinity="0"/>
                </default>
                <default class="{name}-obj-collision">
                    <geom solimp="0.998 0.998 0.001" solref="0.001 1" friction="0.95 0.3 0.1" density="100" group="3" type="mesh"/>
                </default>
            </default>
            <asset>
                {visual_meshes_str}
                <material name="{name}-material" specular="0.5" shininess="0.359999993" rgba="0.800000 0.800000 0.800000 1.0"/>
                {collision_meshes_str}
            </asset>
        """.strip("\n")

        # Build <geom> lines for collision geometries, with random colors
        collision_geoms_str = ""
        for i in range(collision_count):
            if randomize_colors:
                r = rng.random()
                g = rng.random()
                b = rng.random()
                rgba_str = f"{r} {g} {b} 1"
            else:
                rgba_str = "0.8 0.8 0.8 1"
            collision_geoms_str += f'    <geom mesh="{name}-model_collision_{i}" rgba="{rgba_str}" class="{name}-obj-collision"/>\n'

        visual_geoms = "".join(
            f'<geom material="{name}-material" mesh="{name}-model_visual_{i}" class="{name}-obj-visual"/>'
            for i in range(visual_count)
        )
        self._children_raw = f"""
            <freejoint/>

            <!-- Visual Mesh -->
            {visual_geoms}    
            {collision_geoms_str}
        """.strip("\n")

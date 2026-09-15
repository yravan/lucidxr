"""Shared construction for objects with separate visual and convex collision meshes."""

import random

from lucidxr.sim.xml_schema.base import Xml
from lucidxr.sim.xml_schema.schema import Body


class MeshObject(Body):
    """Normalized Objaverse mesh layout with per-object appearance and contact settings."""

    default_name = "object"
    default_assets = "objects"
    default_scale = 1.0
    friction = "0.95 0.3 0.1"
    texture = None
    material_attributes = {"shininess": 0.25}
    name_visual_geoms = False

    def __init__(
        self,
        name=None,
        assets=None,
        collision_count=32,
        visual_count=1,
        scale=None,
        randomize_colors=True,
        seed=0,
        remove_joints=False,
        **kwargs,
    ):
        if any(
            isinstance(n, bool) or not isinstance(n, int) or n < 0 for n in (visual_count, collision_count)
        ):
            raise ValueError("Mesh counts must be nonnegative integers")
        if visual_count == 0:
            raise ValueError("At least one visual mesh is required")
        name = self.default_name if name is None else name
        assets = self.default_assets if assets is None else assets
        scale = self.default_scale if scale is None else scale
        if scale <= 0:
            raise ValueError("Mesh scale must be positive")
        super().__init__(name=name, **kwargs)
        self.assets = assets
        self.visual_count = visual_count
        self.collision_count = collision_count
        self.randomize_colors = randomize_colors
        contact = dict(
            type="mesh", density=100, friction=self.friction, solref="0.001 1", solimp="0.998 0.998 0.001"
        )
        self._preamble = str(
            Xml(
                Xml(
                    Xml(tag="geom", contype=0, conaffinity=0, **contact),
                    tag="default",
                    **{"class": f"{name}_visual"},
                ),
                Xml(Xml(tag="geom", group=3, **contact), tag="default", **{"class": f"{name}_collision"}),
                tag="default",
            )
        )
        meshes = []
        for kind, count, directory, filename in (
            ("vis", visual_count, "visual", "model_normalized"),
            ("coll", collision_count, "collision", "model_normalized_collision"),
        ):
            meshes.extend(
                Xml(
                    tag="mesh",
                    name=f"{name}_{kind}_{i}",
                    file=f"{assets}/{directory}/{filename}_{i}.obj",
                    scale=(scale,) * 3,
                )
                for i in range(count)
            )
        material = dict(self.material_attributes)
        if self.texture:
            meshes.append(Xml(tag="texture", type="2d", name=f"{name}_tex", file=f"{assets}/{self.texture}"))
            material["texture"] = f"{name}_tex"
        meshes.append(Xml(tag="material", name=f"{name}_mat", **material))
        self._preamble += str(Xml(*meshes, tag="asset"))
        children = [] if remove_joints else [Xml(tag="joint", name=f"{name}_joint", type="free")]
        for i in range(visual_count):
            attributes = {"name": f"{name}_vis_{i}_mesh"} if self.name_visual_geoms else {}
            children.append(
                Xml(
                    tag="geom",
                    mesh=f"{name}_vis_{i}",
                    material=f"{name}_mat",
                    **{"class": f"{name}_visual"},
                    **attributes,
                )
            )
        rng = random.Random(seed)
        for i in range(collision_count):
            rgba = (*[rng.random() for _ in range(3)], 1) if randomize_colors else (0.8, 0.8, 0.8, 1)
            children.append(
                Xml(
                    tag="geom",
                    name=f"{name}_coll_{i}_mesh",
                    mesh=f"{name}_coll_{i}",
                    rgba=rgba,
                    **{"class": f"{name}_collision"},
                )
            )
        children.append(Xml(tag="site", name=name, pos=(0, 0, 0), size=0.01, rgba=(1, 1, 1, 0)))
        self._children = (*children, *self._children)

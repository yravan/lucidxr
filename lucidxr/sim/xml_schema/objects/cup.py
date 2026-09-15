"""Matte cup with convex collision parts."""

from .mesh_object import MeshObject


class Cup(MeshObject):
    default_name = "cup"
    default_assets = "cup_assets"
    default_scale = 0.105
    friction = "2.0 0.3 0.1"
    material_attributes = {"specular": 0.5, "shininess": 0.0, "rgba": "0.1 0.3 0.2 1.0"}
    name_visual_geoms = True

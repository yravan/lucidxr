"""Textured bowl with convex collision parts."""

from .mesh_object import MeshObject


class Bowl(MeshObject):
    default_name = "bowl"
    default_scale = 0.13
    texture = "visual/image0.png"

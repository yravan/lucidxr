"""Immutable vector arithmetic shared by coordinate conventions."""

from typing import NamedTuple

from ..base import attribute_value


class Vector3(NamedTuple):
    """
    A class representing a 3D vector.
    """

    x: float
    y: float
    z: float

    def __str__(self):
        return attribute_value(tuple(self))

    def __add__(self, other: "Vector3"):
        x, y, z = other
        return Vector3(self.x + x, self.y + y, self.z + z)

    def __sub__(self, other: "Vector3"):
        x, y, z = other
        return Vector3(self.x - x, self.y - y, self.z - z)

    def __mul__(self, scalar: float) -> "Vector3":
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __neg__(self):
        return Vector3(-self.x, -self.y, -self.z)

    def __rmul__(self, scalar: float) -> "Vector3":
        return self.__mul__(scalar)

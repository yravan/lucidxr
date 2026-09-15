"""Explicit free-body particle grids for current MuJoCo releases."""

from itertools import product

from lucidxr.sim.xml_schema.base import Raw
from lucidxr.sim.xml_schema.schema import FreeBody


def particle_grid(
    *, count=(5, 6, 7), spacing=0.018, offset=(0, 0, 0.9), radius=0.005, rgba=".8 .2 .1 1", name="particle"
) -> Raw:
    """Build a centered grid; each particle has an independent free joint."""
    if len(count) != 3 or any(n < 1 or int(n) != n for n in count):
        raise ValueError("count must contain three positive integers")
    count = tuple(map(int, count))
    if len(offset) != 3:
        raise ValueError("offset must contain three coordinates")
    if spacing <= 0 or radius <= 0:
        raise ValueError("spacing and radius must be positive")
    bodies = []
    for index in product(*(range(n) for n in count)):
        position = [origin + (i - (n - 1) / 2) * spacing for origin, i, n in zip(offset, index, count)]
        bodies.append(
            FreeBody(
                f'<geom type="sphere" size="{radius}" rgba="{rgba}"/>',
                pos=position,
                attributes={"name": name + "_" + "_".join(map(str, index))},
            )
        )
    return Raw("\n".join(map(str, bodies)))

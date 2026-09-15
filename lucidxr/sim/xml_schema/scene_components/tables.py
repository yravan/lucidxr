"""Reusable table layouts; individual table geometry remains in objects/components."""

from lucidxr.sim.xml_schema.objects.orbit_table import OpticalTable
from lucidxr.sim.xml_schema.schema import Group
from lucidxr.sim.xml_schema.simple_components.concrete_slab import ConcreteSlab


class Tabletop(Group):
    """A simple support surface with a known camera/placement origin."""

    def __init__(self, *, pos=(0, 0, 0.6), rgba="0.8 0.8 0.8 1", name="table"):
        self.surface = ConcreteSlab(pos=pos, rgba=rgba, name=name)
        super().__init__(self.surface)

    @property
    def surface_origin(self):
        return self.surface.surface_origin


class OpticalTabletop(Group):
    """Optical-table visuals plus a simple collision surface."""

    def __init__(
        self,
        *,
        table_pos=(-0.2, 0, 0.79),
        surface_pos=(0, 0, 0.777),
        surface_rgba="0.8 0 0 0.9",
        surface_group=4,
    ):
        self.table = OpticalTable(pos=table_pos, name="table_optical")
        self.surface = ConcreteSlab(pos=surface_pos, group=surface_group, rgba=surface_rgba, name="table")
        super().__init__(self.table, self.surface)

    @property
    def surface_origin(self):
        return self.surface.surface_origin

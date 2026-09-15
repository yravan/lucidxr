from lucidxr.sim.xml_schema.schema import Group
from lucidxr.sim.xml_schema.simple_components.planar_pusher import PlanarPusher


class PlanarPusherRig(Group):
    name = "moving_cylinder"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        cyl = PlanarPusher(pos=self._pos)
        _children = (
            cyl,
            cyl._mocaps,
        )

        self._children = tuple(_children)

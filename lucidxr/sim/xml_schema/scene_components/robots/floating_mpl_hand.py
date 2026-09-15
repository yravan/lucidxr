from lucidxr.sim.xml_schema import MPLRight
from lucidxr.sim.xml_schema.schema import Group


class FloatingMPLHand(Group):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        hand1 = MPLRight(
            assets="robots/mpl",
            attributes={"name": "mpl_right"},
            pos=self._pos + [0, 0, 0.3],
        )

        self._children = (
            *self._children,
            hand1,
            hand1._mocaps,
        )

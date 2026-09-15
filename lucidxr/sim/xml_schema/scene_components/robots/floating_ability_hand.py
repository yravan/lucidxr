from lucidxr.sim.xml_schema import AbilityHandLeft, AbilityHandRight
from lucidxr.sim.xml_schema.schema import Group


class FloatingAbilityHand(Group):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        hand1 = AbilityHandLeft(
            assets="robots/ability_hand",
            attributes={"name": "ability_hand_left"},
            pos=self._pos + [0, 0, 0.3],
        )

        hand2 = AbilityHandRight(
            assets="robots/ability_hand",
            attributes={"name": "ability_hand_right"},
            pos=self._pos + [0.3, 0, 0.3],
        )

        self._children = (
            *self._children,
            hand1,
            hand2,
            hand1._mocaps,
            hand2._mocaps,
        )

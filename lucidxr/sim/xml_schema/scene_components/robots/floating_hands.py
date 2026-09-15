"""Floating hand pairs share placement and camera/control-target wiring."""

from lucidxr.sim.xml_schema.robots.hands.dexhand import DexHandLeft, DexHandRight
from lucidxr.sim.xml_schema.robots.hands.shadow_hand import ShadowHandLeft, ShadowHandRight
from lucidxr.sim.xml_schema.robots.hands.xhand import XHandLeft, XHandRight
from lucidxr.sim.xml_schema.scene_components.cameras.rig import make_camera_rig
from lucidxr.sim.xml_schema.schema import Group


class FloatingHands(Group):
    """A right hand and optional left hand, without an enclosing world."""

    hand_types = ()
    hand_names = ()
    hand_options = ({}, {})

    def __init__(self, *, bimanual=True, camera_rig=None, **kwargs):
        super().__init__(**kwargs)
        camera_rig = make_camera_rig(self._pos) if camera_rig is None else camera_rig
        hands = []
        for index in range(2 if bimanual else 1):
            hand = self.hand_types[index](
                name=self.hand_names[index],
                pos=self._pos + (0, 0.15 if index == 0 else -0.15, 0.3),
                wrist_mount=camera_rig.wrist_camera(name="wrist"),
                **self.hand_options[index],
            )
            hands.append(hand)
        self._children = (*self._children, *hands, *(hand._mocaps for hand in hands))


class FloatingDexHand(FloatingHands):
    hand_types = (DexHandRight, DexHandLeft)
    hand_names = ("dex_hand_right", "dex_hand_left")
    hand_options = ({"show_mocap": True}, {"show_mocap": False})


class FloatingShadowHand(FloatingHands):
    hand_types = (ShadowHandRight, ShadowHandLeft)
    hand_names = ("shadow_hand_right", "shadow_hand_left")


class FloatingXHand(FloatingHands):
    hand_types = (XHandRight, XHandLeft)
    hand_names = ("x_hand_right", "x_hand_left")

from pathlib import Path

from vuer_mujoco.schemas.robots.ability_hand import AbilityHandLeft, AbilityHandRight
from vuer_mujoco.schemas.stage_sets.default_scene import DefaultStage


def ability_hand():
    """here we create a scene with a single panda arm (no gripper)."""
    from vuer_mujoco.schemas.utils.file import Prettify, Save

    hand_right = AbilityHandRight(name="ability_hand", assets="staging/ability_hand", pos=[0, 0, 1])
    hand_left = AbilityHandLeft(name="ability_hand_left", assets="staging/ability_hand", pos=[-0.3, 0, 1])

    # s = ibox._children_raw | Prettify()
    # print(s)

    # scene = DefaultStage(hand_right, hand_right._mocaps, model="hand")
    # scene = DefaultStage(hand_left, hand_left._mocaps, model="hand")
    scene = DefaultStage(hand_right, hand_left, hand_left._mocaps, hand_right._mocaps, model="hand")
    scene._xml | Prettify() | Save(Path(__file__).stem + ".mjcf.xml")


if __name__ == "__main__":
    ability_hand()

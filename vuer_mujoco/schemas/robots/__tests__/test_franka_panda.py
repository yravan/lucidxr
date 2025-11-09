from cmx import doc

doc @ """
# Panda Arm (with Tomika Gripper)

Here is a simple scene with a panda arm and a tomika gripper.
"""

with doc:
    from vuer_mujoco.schemas.stage_sets.default_scene import DefaultStage
    from vuer_mujoco.schemas.robots.franka_panda import Panda
    from vuer_mujoco.schemas.robots.tomika_gripper import TomikaGripper
    from vuer_mujoco.schemas.utils.file import Save, Prettify


def test_panda():
    with doc:
        """here we create a scene with a single panda arm and a tomika gripper"""

        panda = Panda(name="test_panda", pos="0 0 0", quat="0 0 0 1", assets="franka_panda")

        scene = DefaultStage(model="franka-panda", children=panda)
        scene._xml | Prettify() | Save("franka_panda.mjcf.xml")


def test_panda_tomika():
    with doc:
        """here we create a scene with a single panda arm and a tomika gripper"""

        tomika = TomikaGripper(name="tomika-1")
        # tomika._xml | Save("panda.mjcf.xml")

        panda = Panda(name="test_panda", pos="0 0 0", quat="0 0 0 1", end_effector=tomika)
        # panda._xml | Save("panda.mjcf.xml")

        scene = DefaultStage(model="franka-panda-tomika", children=panda)
        scene._xml | Prettify() | Save("framka_panda_tomika.mjcf.xml")


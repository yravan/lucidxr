from cmx import doc

doc @ """
# Xarm7 and Ufactory Gripper

Here is a simple scene with the xarm7 and the ufactory gripper.
"""

with doc:
    from vuer_envs.schemas import DefaultStage, Xarm7, UfactoryGripper
    from vuer_envs.schemas.utils import Save, Prettify

with doc:

    def build_xarm():
        """here we create a scene with a single panda arm (no gripper)."""

        xarm = Xarm7(name="test_xarm7", assets="ufactory_xarm7")
        # panda._xml | Save("panda.mjcf.xml")

        scene = DefaultStage(model="xarm7", children=xarm)
        scene._xml | Prettify() | Save("ufactory_xarm7.mjcf.xml")


with doc:

    def build_xarm_gripper():
        """here we create a scene with a single panda arm and a gripper."""

        gripper = UfactoryGripper(asets="ufactory_xarm7")
        xarm = Xarm7(
            name="test_xarm7",
            assets="ufactory_xarm7",
            children=gripper,
        )

        scene = DefaultStage(model="xarm7 gripper", children=xarm)
        scene._xml | Prettify() | Save("ufactory_xarm7_gripper.mjcf.xml")


if __name__ == "__main__":
    build_xarm()
    build_xarm_gripper()

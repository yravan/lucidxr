from vuer_mujoco.schemas.robots.robotiq_2f85 import Robotiq2F85
from vuer_mujoco.schemas.schema import Mjcf, Body


class ConcreteSlab(Body):
    _attributes = {
        "name": "concrete-slab",
        # "childclass": "concrete-slab",
    }
    _preamble = """
    <asset>
      <material name="{name}-concrete" rgba="0.4 0.4 0.4 1"/>
    </asset>
    """
    # use {childclass} when you want to use defaults. Just {name}- if no
    # defaults are involved.
    # todo: how do I make sure it has collision? what about friction?
    _children_raw = """
    <geom name="{name}-concrete" type="box" material="{name}-concrete" size="0.7 0.7 0.05" pos="0 0 -0.05"/>
    """


class FloatingBase(Body):
    _attributes = {
        "name": "floating-base",
    }
    _children_raw = """
    <joint name="{name}-floating-base" type="free"/>
    """


class DualUR5e(Mjcf):
    _attributes = {
        "model": "dual UR5e setup",
    }

    _preamble = """
    <compiler angle="radian" autolimits="true" assetdir="{assets}" meshdir="{assets}" texturedir="{assets}"/>
    <!--<statistic center="0.2 0 0.4" extent=".65"/>-->

    <visual>
      <headlight diffuse="0.6 0.6 0.6" ambient="0.3 0.3 0.3" specular="0 0 0"/>
      <rgba haze="0.15 0.25 0.35 1"/>
      <global azimuth="150" elevation="-20" offwidth="1280" offheight="1024"/>
    </visual>

    <asset>
      <texture type="skybox" builtin="gradient" rgb1="0.3 0.5 0.7" rgb2="0 0 0" width="512" height="3072"/>
      <texture type="2d" name="groundplane" builtin="checker" mark="edge" rgb1="0.2 0.3 0.4" rgb2="0.1 0.2 0.3"
        markrgb="0.8 0.8 0.8" width="300" height="300"/>
      <material name="groundplane" texture="groundplane" texuniform="true" texrepeat="5 5" reflectance="0.2"/>
    </asset>
    """

    def __init__(self, *_children, assets="../robots/assets", **kwargs):
        super().__init__(*_children, assets=assets, **kwargs)

        left_gripper = Robotiq2F85(
            assets="robotiq_2f85",
            attributes={"name": "left-gripper"},
            mocap_pos=self._pos + [-0.5, 0.8, 1.6],
        )
        right_gripper = Robotiq2F85(
            assets="robotiq_2f85",
            attributes={"name": "right-gripper"},
            mocap_pos=self._pos + [0.5, 0.8, 1.6],
        )

        self._children = (
            *self._children,
            FloatingBase(left_gripper, attributes={"name": "left-gripper-float"}),
            FloatingBase(right_gripper, attributes={"name": "right-gripper-float"}),
            # now add the mocap points.
            left_gripper._mocaps,
            right_gripper._mocaps,
        )


if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Save

    table = ConcreteSlab(pos=[0, 0, 1.2])
    scene = DualUR5e(table, pos=[0, 0, 1.2])

    scene._xml | Save(__file__.replace(".py", ".mjcf.xml"))

from vuer_mujoco.schemas.robots.camera import make_camera
from vuer_mujoco.schemas.robots.robotiq_2f85 import Robotiq2F85
from vuer_mujoco.schemas.schema import Mjcf, Body


class ConcreteSlab(Body):
    _attributes = {
        "name": "concrete-slab",
        # "childclass": "concrete-slab",
    }
    _preamble = """
    <asset>
      <material name="{name}-concrete" rgba="0.2 0.2 0.2 1" shininess="0.5"/>
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


class FloatingRobotiq2f85(Mjcf):
    _attributes = {
        "model": "dual UR5e setup",
    }

    # <option gravity='0 0 -9.806' iterations='50' solver='Newton' timestep='0.0001'/>
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

    # _children_raw = """
    # <geom type="plane" size="1 1 .01" pos="0 0 1.21" rgba="1 1 1 1"/>
    # """

    def __init__(self, *_children, assets="assets", **kwargs):
        super().__init__(*_children, assets=assets, **kwargs)

        wrist_camera = make_camera("wrist_camera", pos="0 0.1 0.064", xyaxes="1 0 0 0 0 1")
        pov_camera = make_camera("pov", pos="1.7 0 1.8", xyaxes="0 1 0 -0.4 0 1")
        table_pov = make_camera("front", pos="-1.7 0 1.8", xyaxes="0 -1 0 0.4 0 1")

        gripper = Robotiq2F85(
            assets="robotiq_2f85",
            attributes={"name": "left-gripper"},
            pos=self._pos + [0, 0, 0.3],
            quat=[0, 0, 1, 0],
            mocap_pos=self._pos + [0, 0, 0.3],
            children=wrist_camera,
        )

        self._children = (
            pov_camera,
            table_pov,
            *self._children,
            FloatingBase(gripper, attributes={"name": "gripper-float"}),
            # now add the mocap points.
            gripper._mocaps,
        )


if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Prettify, Save, Raw

    table = ConcreteSlab(pos=[0, 0, 0.6], rgba="0.8 0.8 0.8 1")
    box = Body(
        attributes=dict(name="box-1"),
        _children_raw="""
            <joint type="free" name="{name}"/>
            <geom name="box-1" type="box" pos="0 -0.12 0.7" size="0.015 0.015 0.015" rgba="1 0.5 0 1" density="10"/>
        """,
    )
    start_area = (
        Raw
        @ """
        <geom name="start-area" type="plane" pos="0 -0.12 0.601" size="0.1 0.1 0.001" rgba="1 0 0 0.1" contype="0" conaffinity="0" density="0" />
        """
    )
    goal_area = (
        Raw
        @ """
        <geom name="goal-area" type="plane" pos="0 0.12 0.601" size="0.1 0.1 0.001" rgba="0.137 0.667 1.000 0.1" contype="0" conaffinity="0" density="0" />
        """
    )
    scene = FloatingRobotiq2f85(
        table,
        start_area,
        goal_area,
        box,
        pos=[0, 0, 0.8],
    )

    scene._xml | Prettify() | Save(__file__.replace(".py", ".mjcf.xml"))

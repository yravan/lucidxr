import random
from pathlib import Path

from vuer_mujoco.schemas.utils.file import Save
from vuer_mujoco.schemas.schema import Body
from vuer_mujoco.tasks import add_env
from vuer_mujoco.tasks._floating_robotiq import FloatingRobotiq2f85
from vuer_mujoco.vendors.robosuite.robosuite_tablearena import RobosuiteTableArena


r, g, b = random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)
x1, y1 = random.uniform(-0.5, 0.2), random.uniform(-0.3, 0.3)
x2, y2 = random.uniform(-0.5, 0.2), random.uniform(-0.3, 0.3)


def make_schema(**options):
    from vuer_mujoco.schemas.utils.file import Prettify

    arena = RobosuiteTableArena()
    peg1 = Body(
        attributes=dict(name="peg-1", pos="0.23 0.1 0.65"),
        _preamble="""
        <asset>
          <texture type="cube" name="brass-metal" file="textures/brass-ambra.png"/>
          <material name="bmetal" texture="brass-metal" texuniform="true" specular="1" shininess="1" reflectance="1"/>
        </asset>
        """,
        _children_raw="""
          <geom size="0.016 0.016 0.1" type="box" rgba="0.5 0.5 0 1"/>
          <geom size="0.016 0.016 0.1" type="box" contype="0" conaffinity="0" group="1" material="bmetal"/>
         """,
    )
    peg2 = Body(
        attributes=dict(name="peg-2", pos="0.23 -0.1 0.65"),
        _preamble="""
            <asset>
              <texture type="cube" name="steel-metal" file="textures/steel-scratched.png"/>
                <material name="smetal" texture="steel-metal" texuniform="true" specular="1" shininess="1" reflectance="1"/>
            </asset>
            """,
        _children_raw="""
          <geom size="0.02 0.1" type="cylinder" rgba="0.5 0.5 0 1"/>
          <geom size="0.02 0.1" type="cylinder" contype="0" conaffinity="0" group="1" material="smetal"/>
             """,
    )
    square_nut = Body(
        attributes=dict(name="square-nut", pos=f"{x1} {y1} 0.85"),
        _preamble="""
            <asset>
              <texture type="cube" name="SquareNut_brass-metal" file="textures/brass-ambra.png"/>
              <material name="SquareNut_bmetal" texture="SquareNut_brass-metal" texuniform="true" specular="1" shininess="1" reflectance="1"/>
            </asset>
            """,
        _children_raw="""
            <joint name="SquareNut_joint0" type="free" limited="false" actuatorfrclimited="false" damping="0.0005"/>
            <geom name="SquareNut_g0" size="0.0105 0.04375 0.01" pos="-0.03325 0 0" type="box" condim="4" friction="0.95 0.3 0.2" solimp="0.998 0.998" density="100" rgba="0.5 0 0 1"/>
            <geom name="SquareNut_g1" size="0.03125 0.0105 0.01" pos="0 0.03325 0" type="box" condim="4" friction="0.95 0.3 0.1" solimp="0.998 0.998" density="100" rgba="0.5 0 0 1"/>
            <geom name="SquareNut_g2" size="0.03125 0.0105 0.01" pos="0 -0.03325 0" type="box" condim="4" friction="0.95 0.3 0.1" solimp="0.998 0.998" density="100" rgba="0.5 0 0 1"/>
            <geom name="SquareNut_g3" size="0.0105 0.04375 0.01" pos="0.03325 0 0" type="box" condim="4" friction="0.95 0.3 0.1" solimp="0.998 0.998" density="100" rgba="0.5 0 0 1"/>
            <geom name="SquareNut_g4" size="0.02525 0.015875 0.01" pos="0.054 0 0" type="box" condim="4" friction="0.95 0.3 0.1" solimp="0.998 0.998" density="100" rgba="0.5 0 0 1"/>
            <geom name="SquareNut_g0_visual" size="0.0105 0.04375 0.01" pos="-0.03325 0 0" type="box" contype="0" conaffinity="0" condim="4" group="1" friction="0.95 0.3 0.2" solimp="0.998 0.998" mass="0" material="SquareNut_bmetal"/>
            <geom name="SquareNut_g1_visual" size="0.03125 0.0105 0.01" pos="0 0.03325 0" type="box" contype="0" conaffinity="0" condim="4" group="1" friction="0.95 0.3 0.1" solimp="0.998 0.998" mass="0" material="SquareNut_bmetal"/>
            <geom name="SquareNut_g2_visual" size="0.03125 0.0105 0.01" pos="0 -0.03325 0" type="box" contype="0" conaffinity="0" condim="4" group="1" friction="0.95 0.3 0.1" solimp="0.998 0.998" mass="0" material="SquareNut_bmetal"/>
            <geom name="SquareNut_g3_visual" size="0.0105 0.04375 0.01" pos="0.03325 0 0" type="box" contype="0" conaffinity="0" condim="4" group="1" friction="0.95 0.3 0.1" solimp="0.998 0.998" mass="0" material="SquareNut_bmetal"/>
            <geom name="SquareNut_g4_visual" size="0.02525 0.015875 0.01" pos="0.054 0 0" type="box" contype="0" conaffinity="0" condim="4" group="1" friction="0.95 0.3 0.1" solimp="0.998 0.998" mass="0" material="SquareNut_bmetal"/>
            <site name="SquareNut_handle_site" pos="0.054 0 0" rgba="1 0 0 -1"/>
            <site name="SquareNut_center_site" pos="0 0 0" size="0.003" rgba="1 0 0 -1"/>
            <site name="SquareNut_default_site" pos="0 0 0" size="0.002" rgba="1 0 0 0"/>
             """,
    )
    round_nut = Body(
        attributes=dict(name="round-nut", pos=f"{x2} {y2} 0.85"),
        _preamble="""
            <asset>
              <texture type="cube" name="RoundNut_steel-metal" file="textures/steel-scratched.png"/>
              <material name="RoundNut_smetal" texture="RoundNut_steel-metal" texuniform="true" specular="1" shininess="1" reflectance="1"/>
            </asset>
            """,
        _children_raw="""
            <joint name="RoundNut_joint0" type="free" limited="false" actuatorfrclimited="false" damping="0.0005"/>
            <geom name="RoundNut_g0" size="0.01125 0.0225 0.01" pos="-0.04245 0 0" type="box" condim="4" friction="0.95 0.3 0.1" solimp="0.998 0.998" density="100" rgba="0.5 0 0 1"/>
            <geom name="RoundNut_g1" size="0.01125 0.0225 0.01" pos="0.04245 0 0" type="box" condim="4" friction="0.95 0.3 0.1" solimp="0.998 0.998" density="100" rgba="0.5 0 0 1"/>
            <geom name="RoundNut_g2" size="0.0225 0.01125 0.01" pos="0 -0.04245 0" type="box" condim="4" friction="0.95 0.3 0.1" solimp="0.998 0.998" density="100" rgba="0.5 0 0 1"/>
            <geom name="RoundNut_g3" size="0.0225 0.01125 0.01" pos="0 0.04245 0" type="box" condim="4" friction="0.95 0.3 0.1" solimp="0.998 0.998" density="100" rgba="0.5 0 0 1"/>
            <geom name="RoundNut_g4" size="0.01125 0.0225 0.01" pos="-0.03 -0.03 0" quat="0.92388 0 0 0.382683" type="box" condim="4" friction="0.95 0.3 0.1" solimp="0.998 0.998" density="100" rgba="0.5 0 0 1"/>
            <geom name="RoundNut_g5" size="0.01125 0.0225 0.01" pos="0.03 0.03 0" quat="0.92388 0 0 0.382683" type="box" condim="4" friction="0.95 0.3 0.1" solimp="0.998 0.998" density="100" rgba="0.5 0 0 1"/>
            <geom name="RoundNut_g6" size="0.0225 0.01125 0.01" pos="0.03 -0.03 0" quat="0.92388 0 0 0.382683" type="box" condim="4" friction="0.95 0.3 0.1" solimp="0.998 0.998" density="100" rgba="0.5 0 0 1"/>
            <geom name="RoundNut_g7" size="0.0225 0.01125 0.01" pos="-0.03 0.03 0" quat="0.92388 0 0 0.382683" type="box" condim="4" friction="0.95 0.3 0.1" solimp="0.998 0.998" density="100" rgba="0.5 0 0 1"/>
            <geom name="RoundNut_g8" size="0.02525 0.015875 0.01" pos="0.06 0 0" type="box" condim="4" friction="0.95 0.3 0.1" solimp="0.998 0.998" density="100" rgba="0.5 0 0 1"/>
            <geom name="RoundNut_g0_visual" size="0.01125 0.0225 0.01" pos="-0.04245 0 0" type="box" contype="0" conaffinity="0" condim="4" group="1" friction="0.95 0.3 0.1" solimp="0.998 0.998" mass="0" material="RoundNut_smetal"/>
            <geom name="RoundNut_g1_visual" size="0.01125 0.0225 0.01" pos="0.04245 0 0" type="box" contype="0" conaffinity="0" condim="4" group="1" friction="0.95 0.3 0.1" solimp="0.998 0.998" mass="0" material="RoundNut_smetal"/>
            <geom name="RoundNut_g2_visual" size="0.0225 0.01125 0.01" pos="0 -0.04245 0" type="box" contype="0" conaffinity="0" condim="4" group="1" friction="0.95 0.3 0.1" solimp="0.998 0.998" mass="0" material="RoundNut_smetal"/>
            <geom name="RoundNut_g3_visual" size="0.0225 0.01125 0.01" pos="0 0.04245 0" type="box" contype="0" conaffinity="0" condim="4" group="1" friction="0.95 0.3 0.1" solimp="0.998 0.998" mass="0" material="RoundNut_smetal"/>
            <geom name="RoundNut_g4_visual" size="0.01125 0.0225 0.01" pos="-0.03 -0.03 0" quat="0.92388 0 0 0.382683" type="box" contype="0" conaffinity="0" condim="4" group="1" friction="0.95 0.3 0.1" solimp="0.998 0.998" mass="0" material="RoundNut_smetal"/>
            <geom name="RoundNut_g5_visual" size="0.01125 0.0225 0.01" pos="0.03 0.03 0" quat="0.92388 0 0 0.382683" type="box" contype="0" conaffinity="0" condim="4" group="1" friction="0.95 0.3 0.1" solimp="0.998 0.998" mass="0" material="RoundNut_smetal"/>
            <geom name="RoundNut_g6_visual" size="0.0225 0.01125 0.01" pos="0.03 -0.03 0" quat="0.92388 0 0 0.382683" type="box" contype="0" conaffinity="0" condim="4" group="1" friction="0.95 0.3 0.1" solimp="0.998 0.998" mass="0" material="RoundNut_smetal"/>
            <geom name="RoundNut_g7_visual" size="0.0225 0.01125 0.01" pos="-0.03 0.03 0" quat="0.92388 0 0 0.382683" type="box" contype="0" conaffinity="0" condim="4" group="1" friction="0.95 0.3 0.1" solimp="0.998 0.998" mass="0" material="RoundNut_smetal"/>
            <geom name="RoundNut_g8_visual" size="0.02525 0.015875 0.01" pos="0.06 0 0" type="box" contype="0" conaffinity="0" condim="4" group="1" friction="0.95 0.3 0.1" solimp="0.998 0.998" mass="0" material="RoundNut_smetal"/>
            <site name="RoundNut_handle_site" pos="0.06 0 0" rgba="1 0 0 -1"/>
            <site name="RoundNut_center_site" pos="0 0 0" size="0.003" rgba="1 0 0 -1"/>
            <site name="RoundNut_default_site" pos="0 0 0" size="0.002" rgba="1 0 0 0"/>
             """,
    )
    scene = FloatingRobotiq2f85(
        arena,
        peg1,
        peg2,
        square_nut,
        round_nut,
        pos=[0, 0, 0.8],
        **options,
    )

    return scene._xml | Prettify()


def register():
    from vuer_mujoco.tasks.entrypoint import make_env

    add_env(
        env_id="RobosuiteNutassembly-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="robosuite_nutassembly.mjcf.xml",
            workdir=Path(__file__).parent,
            mode="multiview",
        ),
    )

    add_env(
        env_id="RobosuiteNutassembly-lucid-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="robosuite_nutassembly.mjcf.xml",
            workdir=Path(__file__).parent,
            mode="lucid",
            object_prefix="ball",
        ),
    )


if __name__ == "__main__":
    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

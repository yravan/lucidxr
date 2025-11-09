from pathlib import Path

from vuer_mujoco.schemas.schema import Body
from vuer_mujoco.schemas.objects.mj_sdf import MjSDF
from vuer_mujoco.schemas.utils.file import Save
from vuer_mujoco.schemas.components.concrete_slab import ConcreteSlab
from vuer_mujoco.schemas.components.force_plate import ForcePlate
from vuer_mujoco.schemas.components.rigs.lighting_rig import make_lighting_rig


class OpticalTable(Body):
    assets = "objects"
    classname = "optical_table"
    free = True
    alpha = 1.0
    _files = ["model"]

    _attributes = {
        "name": "object",
    }

    _preamble = """
        <default>
            <default class="{classname}-visual">
                <geom group="2" type="mesh" contype="0" conaffinity="0"/>
            </default>
            <default class="{classname}-collision">
                <geom group="3" type="mesh"/>
            </default>
        </default>
        <asset>
          <!-- Materials ported from MTL file -->
          <material name="{name}-mat_1" rgba="0.501961 0.517647 0.501961 {alpha}" roughness="0" shininess="1" specular="0.4"/>
          <material name="{name}-mat_2" rgba="1 1 1 {alpha}" roughness="0" shininess="1" specular="0.4"/>
          <material name="{name}-mat_3" rgba="0.752941 0.752941 0.752941 {alpha}" roughness="0" shininess="1" specular="0.4"/>
          <material name="{name}-mat_4" rgba="0.647059 0.619608 0.588235 {alpha}" roughness="0" shininess="1" specular="0.4"/> <!-- Good wood-like color for tabletop -->
          <material name="{name}-mat_5" rgba="0.101961 0.101961 0.101961 {alpha}" roughness="0" shininess="1" specular="0.4"/> <!-- Dark color for legs/structure -->
          <material name="{name}-mat_6" rgba="0.109804 0.109804 0.109804 {alpha}" roughness="0" shininess="1" specular="0.4"/>
          <material name="{name}-mat_7" rgba="0.792157 0.819608 0.933333 {alpha}" roughness="0" shininess="1" specular="0.4"/>
          <material name="{name}-mat_8" rgba="0.529412 0.549020 0.549020 {alpha}" roughness="0" shininess="1" specular="0.4"/>
          <material name="{name}-mat_9" rgba="0.098039 0.098039 0.098039 {alpha}" shininess=""/>
          <material name="{name}-mat_10" rgba="0 0 0 {alpha}" roughness="0" shininess="1" specular="0.4"/>
          <material name="{name}-mat_11" rgba="0.294118 0.294118 0.294118 {alpha}" roughness="0" shininess="1" specular="0.4"/>
          <material name="{name}-mat_12" rgba="0.250980 0.250980 0.250980 {alpha}" roughness="0" shininess="1" specular="0.4"/>
          <material name="{name}-mat_13" rgba="0.698039 0.698039 0.698039 {alpha}" roughness="0" shininess="1" specular="0.4"/>
          <material name="{name}-mat_14" rgba="0.956863 0.956863 0.956863 {alpha}" roughness="0" shininess="1" specular="0.4"/>

          <mesh name="{classname}-model_0" file="{assets}/model_0.obj"/>
          <mesh name="{classname}-model_1" file="{assets}/model_1.obj"/>
          <mesh name="{classname}-model_2" file="{assets}/model_2.obj"/>
          <mesh name="{classname}-model_3" file="{assets}/model_3.obj"/>
          <mesh name="{classname}-model_4" file="{assets}/model_4.obj"/>
          <mesh name="{classname}-model_5" file="{assets}/model_5.obj"/>
          <mesh name="{classname}-model_6" file="{assets}/model_6.obj"/>
          <mesh name="{classname}-model_7" file="{assets}/model_7.obj"/>
          <mesh name="{classname}-model_8" file="{assets}/model_8.obj"/>
          <mesh name="{classname}-model_9" file="{assets}/model_9.obj"/>
          <mesh name="{classname}-model_10" file="{assets}/model_10.obj"/>
          <mesh name="{classname}-model_11" file="{assets}/model_11.obj"/>
          <mesh name="{classname}-model_12" file="{assets}/model_12.obj"/>
          <mesh name="{classname}-model_13" file="{assets}/model_13.obj"/>
        </asset>
        """

    _children_raw = """
        <!--<freejoint/>-->
        <geom mesh="{classname}-model_0" class="{classname}-visual"  material="{name}-mat_1" />
        <geom mesh="{classname}-model_1" class="{classname}-visual"  material="{name}-mat_2" />
        <geom mesh="{classname}-model_2" class="{classname}-visual"  material="{name}-mat_3" />
        <geom mesh="{classname}-model_3" class="{classname}-visual"  material="{name}-mat_4" />
        <geom mesh="{classname}-model_4" class="{classname}-visual"  material="{name}-mat_5" />
        <geom mesh="{classname}-model_5" class="{classname}-visual"  material="{name}-mat_6" />
        <geom mesh="{classname}-model_6" class="{classname}-visual"  material="{name}-mat_7" />
        <geom mesh="{classname}-model_7" class="{classname}-visual"  material="{name}-mat_8" />
        <geom mesh="{classname}-model_8" class="{classname}-visual"  material="{name}-mat_9" />
        <geom mesh="{classname}-model_9" class="{classname}-visual"  material="{name}-mat_10"/>
        <geom mesh="{classname}-model_10" class="{classname}-visual" material="{name}-mat_11"/>
        <geom mesh="{classname}-model_11" class="{classname}-visual" material="{name}-mat_12"/>
        <geom mesh="{classname}-model_12" class="{classname}-visual" material="{name}-mat_13"/>
        <geom mesh="{classname}-model_13" class="{classname}-visual" material="{name}-mat_14"/>
        """


def make_schema(robot="panda", **options):
    from vuer_mujoco.schemas.utils.file import Prettify
    from vuer_mujoco.schemas.schema import Mjcf

    if robot == "panda":
        from vuer_mujoco.schemas.robots.franka_panda import Panda
        from vuer_mujoco.schemas.robots.tomika_gripper import TomikaGripper

        gripper = TomikaGripper(name="test_gripper", mocap_pos="0.25 0.0 1.10", mocap_quat="0 0 1 0")
        panda = Panda(end_effector=gripper, name="test_panda", pos=(0, 0, 0.79), quat=(1, 0, 0, 0))
    else:
        raise ValueError(f"Unknown robot: {robot}")

    optical_table = OpticalTable(
        pos=[0, 0, 0.79],
        assets="model",
        _attributes={"name": "optical_table"},
    )
    lighting = make_lighting_rig(optical_table._pos)

    from vuer_mujoco.schemas.objects import HexBlock, SquareBlock, TriangleBlock, LeBox, CircleBlock

    le_box = LeBox(attributes={"name": "insertion-box"}, assets="sort_shape", pos=[0.2, 0, 0.9])
    square_block = SquareBlock(attributes={"name": "square"}, assets="sort_shape", pos=[0.35, -0.075, 0.9])
    triangle_block = TriangleBlock(attributes={"name": "triangle"}, assets="sort_shape", pos=[0.5, -0.075, 0.9])
    hex_block = HexBlock(attributes={"name": "hex"}, assets="sort_shape", pos=[0.35, 0.075, 0.9])
    circle_block = CircleBlock(attributes={"name": "circle"}, assets="sort_shape", pos=[0.5, 0.075, 0.9])

    teddy_bear = MjSDF(
        pos=[0.2, 0.2, 0.9], assets="teddy_bear", _attributes={"name": "teddy-bear", "quat": "0 0.707 0.707 0"}, scale=".1 .1 .1"
    )
    mug_tree = MjSDF(pos=[0.2, 0.3, 0.9], assets="mug_tree", _attributes={"name": "mug-tree", "quat": "0 0.707 0.707 0"}, scale=".1 .1 .1")

    ball_sorting_toy = MjSDF(
        pos=[0.3, 0.3, 0.9], assets="mug_tree", _attributes={"name": "mug-tree", "quat": "0 0.707 0.707 0"}, scale=".1 .1 .1"
    )

    # mug = MjSDF(pos=[])

    table_slap = ConcreteSlab(assets="model", pos=[0, 0, 0.6], rgba="0.8 0.8 0.8 1")

    work_area = ForcePlate(
        name="start-area",
        pos=(0.3, 0, 0.605),
        quat=(0, 1, 0, 0),
        type="box",
        size="0.15 0.15 0.01",
        rgba="1 0 0 0.1",
    )

    scene = Mjcf(
        lighting.key,
        lighting.fill,
        lighting.back,
        optical_table,
        # le_box,
        # square_block,
        # triangle_block,
        # hex_block,
        # circle_block,
        teddy_bear,
        mug_tree,
        # panda,
        # gripper._mocaps,
    )

    # scene = FloatingRobotiq2f85(
    #     optical_table,
    #     # ibox,
    #     # square_block,
    #     # triangle_block,
    #     # hex_block,
    #     # circle_block,
    #     work_area,
    #     pos=[0, 0, 0.8],
    #     **options,
    # )

    return scene._xml | Prettify()


def register():
    from vuer_mujoco.tasks import add_env
    from vuer_mujoco.tasks.entrypoint import make_env

    add_env(
        env_id="IsaacOrbit_table-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="sort_block.mjcf.xml",
            workdir=Path(__file__).parent,
            mode="render",
        ),
    )


if __name__ == "__main__":
    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

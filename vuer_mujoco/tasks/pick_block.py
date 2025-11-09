import random
from pathlib import Path

from vuer_mujoco.schemas.schema import Body
from vuer_mujoco.schemas.utils.file import Save
from vuer_mujoco.tasks import add_env
from vuer_mujoco.tasks._floating_robotiq import FloatingRobotiq2f85
from vuer_mujoco.tasks._tile_floor import TileFloor
from vuer_mujoco.tasks.entrypoint import make_env
from vuer_mujoco.vendors.robohive.robohive_object import RobohiveObj


# Generate random values for r, g, and b
r, g, b = random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)
x, y = random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2)


def make_schema():
    from vuer_mujoco.schemas.utils.file import Prettify

    table = RobohiveObj(
        otype="furniture",
        asset_key="simpleTable/simpleWoodTable",
        pos=[0, 0, 0],
    )
    floor = TileFloor()
    box = Body(
        attributes=dict(name="box-1", pos=f"{x} {y} 0.8"),
        rgba=f"{r} {g} {b} 1.0",
        _children_raw="""
        <joint type="free" name="{name}"/>
        <geom name="box-1" type="box" size="0.015 0.015 0.015" mass="0.1" rgba="{rgba}" density="1000"/>
        """,
    )
    scene = FloatingRobotiq2f85(
        table,
        floor,
        box,
        pos=[0, 0, 0.8],
    )

    return scene._xml | Prettify()


def register():
    add_env(
        env_id="PickBlock-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="pick_block.mjcf.xml",
            workdir=Path(__file__).parent,
            mode="multiview",
        ),
    )

    add_env(
        env_id="PickBlock-depth-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="pick_block.mjcf.xml",
            workdir=Path(__file__).parent,
            mode="multiview-depth",
        ),
    )

    add_env(
        env_id="PickBlock-segmentation-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="pick_block.mjcf.xml",
            workdir=Path(__file__).parent,
            mode="multiview-segmentation",
        ),
    )

    add_env(
        env_id="PickBlock-wrist-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="pick_block.mjcf.xml",
            workdir=Path(__file__).parent,
            image_key="wrist/rgb",
            camera_id=4,
            mode="rgb",
        ),
    )

    add_env(
        env_id="PickBlock-wrist-depth-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="pick_block.mjcf.xml",
            workdir=Path(__file__).parent,
            image_key="wrist/depth",
            camera_id=4,
            mode="depth",
        ),
    )


if __name__ == "__main__":
    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

import random
from pathlib import Path

from vuer_mujoco.schemas.utils.file import Save
from vuer_mujoco.schemas.schema import Body
from vuer_mujoco.schemas.objects.mj_sdf import MjSDF
from vuer_mujoco.tasks import add_env
from vuer_mujoco.schemas.components.table_slab import Table
from vuer_mujoco.tasks._floating_robotiq import FloatingRobotiq2f85
from vuer_mujoco.tasks.entrypoint import make_env

x1, y1 = random.uniform(-0.2, 0.2), random.uniform(-0.1, -0.5)
x2, y2 = random.uniform(-0.2, 0.2), random.uniform(-0.1, -0.5)


def make_schema(**options):
    from vuer_mujoco.schemas.utils.file import Prettify

    # table = BrownTable(pos=[0, 0, -0.1], assets="brown_table")

    basket = MjSDF(pos=[0, 0.2, 0.67], assets="black_basket", _attributes={"name": "basket"})

    table = Table(pos=[0, 0, 0.6], rgba="0.7 0.65 0.57 1")
    ball = Body(
        attributes=dict(name="ball-1", pos=f"{x1} {y1} 0.7"),
        _children_raw="""
        <joint type="free" name="{name}"/>
        <geom name="sphere-1" type="sphere" size="0.03" rgba="0.5 0.5 0.5 1" mass="0.1" solref="0.003 1" solimp="0.95 0.99 0.001" friction="2 0.01 0.002"/>
        """,
    )

    can = Body(
        attributes=dict(name="can-1", pos=f"{x2} {y2} 0.7"),
        _children_raw="""
        <joint type="free" name="{name}"/>
        <geom name="can-1" type="cylinder" size="0.03 0.05" rgba="0.5 0.5 0.5 1" mass="0.1" solref="0.003 1" solimp="0.95 0.99 0.001" friction="2 0.01 0.002"/>
        """,
    )

    ground = Body(
        attributes=dict(name="ground"),
        _children_raw="""
        <geom name="ground" type="plane" pos="0 0 0" size="10 10 0.1" rgba="0.2 0.3 0.4 1"/>
        """,
    )

    scene = FloatingRobotiq2f85(
        table,
        ball,
        can,
        basket,
        ground,
        pos=[0, 0, 0.8],
    )

    return scene._xml | Prettify()


add_env(
    env_id="PickSphere-v1",
    entrypoint=make_env,
    kwargs=dict(
        xml_path="pick_sphere.mjcf.xml",
        workdir=Path(__file__).parent,
        mode="multiview",
    ),
)

add_env(
    env_id="PickSphere-lucid-v1",
    entrypoint=make_env,
    kwargs=dict(
        xml_path="pick_sphere.mjcf.xml",
        workdir=Path(__file__).parent,
        mode="lucid",
        prefix_to_class_ids={"basket": 5, "table": 100, "ball": 80, "can": 65},
        object_keys=["ball"],
    ),
)


if __name__ == "__main__":
    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

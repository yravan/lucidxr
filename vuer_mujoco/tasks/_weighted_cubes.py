from vuer_mujoco.schemas.schema import Body
from vuer_mujoco.schemas.components.concrete_slab import ConcreteSlab


def create_boxes():
    # work_area = ForcePlate(
    #     name="start-area",
    #     pos=(0, 0, 0.6052),
    #     quat=(0, 1, 0, 0),
    #     type="box",
    #     size="0.2 0.2 0.005",
    #     rgba="0.7 0.7 0.0 1.0",
    # )
    table = ConcreteSlab(pos=[0, 0, 0.6], rgba="0.8 0.8 0.8 1")

    box1 = Body(
        attributes=dict(name="box-1", pos="-0.1 0 0.7"),
        _children_raw="""
            <joint type="free" name="{name}"/>
            <geom name="{name}" type="box" size="0.015 0.015 0.015" rgba="1 0 0 1" mass="1"/>
            """,
    )

    box2 = Body(
        attributes=dict(name="box-2", pos="0 0 0.7"),
        _children_raw="""
            <joint type="free" name="{name}"/>
            <geom name="{name}" type="box" size="0.015 0.015 0.015" rgba="0 1 0 1" mass="1"/>
            """,
    )

    box3 = Body(
        attributes=dict(name="box-3", pos="0.1 0 0.7"),
        _children_raw="""
            <joint type="free" name="{name}"/>
            <geom name="{name}" type="box" size="0.015 0.015 0.015" rgba="0 0 1 1" mass="1"/>
            """,
    )
    # return work_area, table, box1, box2, box3
    return table, box1, box2, box3

from vuer_mujoco.schemas.schema import Body


def create_boxes():
    # work_area = ForcePlate(
    #     name="start-area",
    #     pos=(0, 0, 0.6052),
    #     quat=(0, 1, 0, 0),
    #     type="box",
    #     size="0.2 0.2 0.005",
    #     rgba="0.7 0.7 0.0 1.0",
    # )

    box1 = Body(
        attributes=dict(name="box-1", pos="-0.1 0 0.9"),
        _children_raw="""
            <joint type="free" name="{name}"/>
            <geom name="{name}" type="box" size="0.025 0.025 0.025" rgba="1 0 0 1" mass="0.25"/>
            """,
    )

    box2 = Body(
        attributes=dict(name="box-2", pos="0 0 0.9"),
        _children_raw="""
            <joint type="free" name="{name}"/>
            <geom name="{name}" type="box" size="0.025 0.025 0.025" rgba="0 1 0 1" mass="0.25"/>
            """,
    )

    box3 = Body(
        attributes=dict(name="box-3", pos="0.1 0 0.9"),
        _children_raw="""
            <joint type="free" name="{name}"/>
            <geom name="{name}" type="box" size="0.025 0.025 0.025" rgba="0 0 1 1" mass="0.25"/>
            """,
    )
    # return work_area, table, box1, box2, box3
    return box1, box2, box3

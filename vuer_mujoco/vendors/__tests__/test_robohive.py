def test_objrobohive():
    from vuer_mujoco.schemas.utils.file import Prettify
    from vuer_mujoco.schemas.vendors.robohive.robohive_object import RobohiveObj
    from vuer_mujoco.tasks._floating_robotiq import FloatingRobotiq2f85

    table = RobohiveObj(
        object_type="table",
        pos=[0, 0, 0.6],
        quat=[0, 0, 1, 0],
    )
    scene = FloatingRobotiq2f85(
        table,
        pos=[0, 0, 0.8],
    )

    print(scene._xml | Prettify())

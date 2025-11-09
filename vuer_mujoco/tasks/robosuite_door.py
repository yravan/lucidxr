import random
from pathlib import Path

from vuer_mujoco.schemas.utils.file import Save
from vuer_mujoco.tasks import add_env
from vuer_mujoco.tasks._floating_robotiq import FloatingRobotiq2f85
from vuer_mujoco.vendors.robosuite.robosuite_door import RobosuiteDoor
from vuer_mujoco.vendors.robosuite.robosuite_tablearena import RobosuiteTableArena


r, g, b = random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)
x, y = random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2)


def make_schema(**options):
    from vuer_mujoco.schemas.utils.file import Prettify

    arena = RobosuiteTableArena(table_pos=f"{x} {y} 0.775")
    door = RobosuiteDoor(
        _attributes=dict(name="door-1", pos=f"{x + 0.1} {y - 0.002} 1.1", quat="0.618783 0 0 -0.785562"),
    )
    scene = FloatingRobotiq2f85(
        arena,
        door,
        pos=[0, 0, 0.8],
        **options,
    )

    return scene._xml | Prettify()


def register():
    from vuer_mujoco.tasks.entrypoint import make_env

    add_env(
        env_id="RobosuiteDoor-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="robosuite_door.mjcf.xml",
            workdir=Path(__file__).parent,
            mode="multiview",
        ),
    )

    add_env(
        env_id="RobosuiteDoor-lucid-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="robosuite_door.mjcf.xml",
            workdir=Path(__file__).parent,
            mode="lucid",
            object_prefix="ball",
        ),
    )


if __name__ == "__main__":
    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

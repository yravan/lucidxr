from pathlib import Path

from vuer_mujoco.schemas.objects.bigym_dishdrainer import BigymDishDrainer
from vuer_mujoco.schemas.objects.bigym_plate import BigymPlate
from vuer_mujoco.schemas.objects.bigym_table import BigymTable
from vuer_mujoco.tasks import add_env
from vuer_mujoco.tasks._floating_robotiq import FloatingRobotiq2f85
from vuer_mujoco.schemas.components.mj_ground_plane import GroundPlane
from vuer_mujoco.tasks.entrypoint import make_env

# Generate random values for r, g, and b
# r, g, b = random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)


def make_schema():
    from vuer_mujoco.schemas.utils.file import Prettify

    ground = GroundPlane()
    table = BigymTable(pos=[0.7, 0, 0], quat=[0.7071, 0, 0, -0.7071])

    drainer1 = BigymDishDrainer(
        pos=[0.7, 0.3, 0.95],
        quat=[1, 0, 0, 0],
        prefix="drainer1",
        _attributes={
            "name": "drainer1",
        },
    )
    drainer2 = BigymDishDrainer(
        pos=[0.7, -0.3, 0.95],
        quat=[1, 0, 0, 0],
        prefix="drainer2",
        _attributes={
            "name": "drainer2",
        },
    )

    plate = BigymPlate(
        pos=[0.7, -0.18, 1.1],
        quat=[0.7071, 0.7071, 0, 0],
        prefix="plate1",
        _attributes={
            "name": "plate1",
        },
    )

    scene = FloatingRobotiq2f85(
        ground,
        table,
        drainer1,
        drainer2,
        plate,
        pos=[0, 0, 0.8],
    )

    return scene._xml | Prettify()


def register():
    add_env(
        env_id="MovePlate-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="flip_mug.mjcf.xml",
            workdir=Path(__file__).parent,
            mode="multiview",
        ),
    )

    add_env(
        env_id="MovePlate-depth-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="flip_mug.mjcf.xml",
            workdir=Path(__file__).parent,
            mode="multiview-depth",
        ),
    )

    add_env(
        env_id="MovePlate-wrist-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="flip_mug.mjcf.xml",
            workdir=Path(__file__).parent,
            image_key="wrist/rgb",
            camera_id=4,
            mode="rgb",
        ),
    )

    add_env(
        env_id="MovePlate-wrist-depth-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="flip_mug.mjcf.xml",
            workdir=Path(__file__).parent,
            image_key="wrist/depth",
            camera_id=4,
            mode="depth",
        ),
    )


if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Save

    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

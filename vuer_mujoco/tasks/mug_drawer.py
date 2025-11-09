from pathlib import Path

from vuer_mujoco.schemas.objects.vuer_mug import VuerMug
from vuer_mujoco.schemas.objects.mimicgen_drawer import MimicGenDrawer
from vuer_mujoco.tasks import add_env
from vuer_mujoco.schemas.components.concrete_slab import ConcreteSlab
from vuer_mujoco.tasks._floating_robotiq import FloatingRobotiq2f85
from vuer_mujoco.tasks.entrypoint import make_env


# Generate random values for r, g, and b
# r, g, b = random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)


def make_schema(**_,):
    from vuer_mujoco.schemas.utils.file import Prettify

    table = ConcreteSlab(pos=[0, 0, 0.6], rgba="0.8 0.8 0.8 1", roughness="0.2")

    drawer = MimicGenDrawer(pos=[0.1, 0, 0.63], quat=[1, 0, 0, 0])

    mug = VuerMug(pos=[-0.2, -0.3, 0.65], quat=[0, 0, 1, 0])

    scene = FloatingRobotiq2f85(
        drawer,
        mug,
        table,
        pos=[0, 0, 0.8],
    )

    return scene._xml | Prettify()


def register():
    add_env(
        env_id="MoveDrawer-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="mug_drawer.mjcf.xml",
            workdir=Path(__file__).parent,
            mode="multiview",
        ),
    )

    add_env(
        env_id="MoveDrawer-depth-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="mug_drawer.mjcf.xml",
            workdir=Path(__file__).parent,
            mode="multiview-depth",
        ),
    )

    add_env(
        env_id="MoveDrawer-wrist-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="mug_drawer.mjcf.xml",
            workdir=Path(__file__).parent,
            image_key="wrist/rgb",
            camera_id=4,
            mode="rgb",
        ),
    )

    add_env(
        env_id="MoveDrawer-wrist-depth-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="mug_drawer.mjcf.xml",
            workdir=Path(__file__).parent,
            image_key="wrist/depth",
            camera_id=4,
            mode="depth",
        ),
    )


if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Save

    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

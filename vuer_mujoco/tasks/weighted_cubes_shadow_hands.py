from pathlib import Path

from vuer_mujoco.tasks import add_env
from vuer_mujoco.tasks._floating_shadowhand import FloatingShadowHand
from vuer_mujoco.tasks._weighted_cubes import create_boxes
from vuer_mujoco.tasks.entrypoint import make_env


def make_schema():
    from vuer_mujoco import Prettify, Save

    scene = FloatingShadowHand(
        *create_boxes(),
        cameras.right_camera,
        cameras.right_camera_r,
        cameras.front_camera,
        cameras.top_camera,
        cameras.left_camera,
        cameras.back_camera,
        pos=[-0.5, 0, 0.8],
    )

    return scene._xml | Prettify()


def register():
    add_env(
        env_id="Weighted_cubes_shadow_hands-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="weighted_cubes_shadow_hands.mjcf.xml",
            workdir=Path(__file__).parent,
            mode="multiview",
        ),
    )


if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Save

    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

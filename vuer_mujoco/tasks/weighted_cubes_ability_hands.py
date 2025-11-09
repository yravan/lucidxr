from pathlib import Path

from vuer_mujoco.tasks import add_env
from vuer_mujoco.tasks._floating_ability_hand import FloatingAbilityHand
from vuer_mujoco.tasks._weighted_cubes import create_boxes
from vuer_mujoco.tasks.entrypoint import make_env


def make_schema():
    from vuer_mujoco.schemas.utils.file import Prettify

    scene = FloatingAbilityHand(
        *create_boxes(),
        pos=[0, 0, 0.8],
    )

    return scene._xml | Prettify()


def register():
    add_env(
        env_id=f"{Path(__file__).stem.capitalize()}-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path=f"{Path(__file__).stem}.mjcf.xml",
            workdir=Path(__file__).parent,
            mode="render",
        ),
    )


if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Save

    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

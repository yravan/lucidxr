from pathlib import Path

from vuer_mujoco.tasks import add_env
from vuer_mujoco.schemas.components.rigs.camera_rig import make_camera_rig
from vuer_mujoco.schemas.components.concrete_slab import ConcreteSlab
from vuer_mujoco.tasks._floating_shadowhand import FloatingShadowHand
from vuer_mujoco.tasks._juggle_cubes import create_boxes
from vuer_mujoco.schemas.components.rigs.lighting_rig import make_lighting_rig
from vuer_mujoco.tasks.entrypoint import make_env
from vuer_mujoco.schemas.objects.orbit_table import OpticalTable


def make_schema():
    from vuer_mujoco.schemas.utils.file import Prettify

    optical_table = OpticalTable(
        pos=[-0.2, 0, 0.79],
        assets="model",
        _attributes={"name": "table_optical"},
    )
    # camera_rig = make_camera_rig(optical_table._pos)

    table_slab = ConcreteSlab(
        assets="model",
        pos=[0, 0, 0.777],
        group=4,
        rgba="0.8 0 0 0.9",
        _attributes={
            "name": "table",
        },
    )
    lighting = make_lighting_rig(optical_table._pos)
    camera_rig = make_camera_rig(table_slab.surface_origin)

    scene = FloatingShadowHand(
        *create_boxes(),
        optical_table,
        table_slab,
        camera_rig.right_camera,
        camera_rig.right_camera_r,
        camera_rig.front_camera,
        camera_rig.top_camera,
        camera_rig.left_camera,
        camera_rig.back_camera,
        pos=[-0.5, 0, 0.8],
    )

    return scene._xml | Prettify()


def register():
    add_env(
        env_id="JuggleCubesShadowHands-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="juggle_cubes_shadow_hands.mjcf.xml",
            workdir=Path(__file__).parent,
            mode="multiview",
        ),
    )


if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Save

    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

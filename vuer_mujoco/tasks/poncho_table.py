from vuer_mujoco.schemas.components.concrete_slab import ConcreteSlab
from vuer_mujoco.tasks._floating_shadowhand import FloatingShadowHand
from vuer_mujoco.schemas.objects.poncho import Poncho
from vuer_mujoco.schemas.objects.orbit_table import OpticalTable
from vuer_mujoco.schemas.components.rigs.lighting_rig import make_lighting_rig
from vuer_mujoco.schemas.components.rigs.camera_rig import make_camera_rig


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

    poncho = Poncho(pos=[0.3, 0, 0.9], name="poncho", rgba="0.3 0.3 1 1", scale=0.3)

    scene = FloatingShadowHand(
        optical_table,
        table_slab,
        camera_rig.right_camera,
        camera_rig.right_camera_r,
        camera_rig.front_camera,
        camera_rig.top_camera,
        camera_rig.left_camera,
        camera_rig.back_camera,
        poncho,
        pos=[0, 0, 0.8],
    )

    return scene._xml | Prettify()


if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Save

    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

from vuer_mujoco.schemas.components.concrete_slab import ConcreteSlab
from vuer_mujoco.tasks._floating_shadowhand import FloatingShadowHand
from vuer_mujoco.schemas.objects.decomposed_obj import ObjMujocoObject
from vuer_mujoco.schemas.objects.cup_3 import ObjaverseMujocoCup
from vuer_mujoco.schemas.objects.bin import Bin
from vuer_mujoco.schemas.schema import Composite
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

    bin = ObjMujocoObject(
        name="bin",
        assets="bin",
        visual_count=1,
        pos=[0, 0, 0.85],
        scale=0.08,
        collision_count=18,
        textures=["Material.001"],
        randomize_colors=False,
    )
    brush = ObjMujocoObject(
        name="brush",
        assets="brush",
        visual_count=1,
        pos=[0.5, 0, 0.85],
        scale=0.01,
        collision_count=6,
        textures=["tex"],
        randomize_colors=False,
    )
    dustpan = ObjMujocoObject(
        name="dustpan",
        assets="dustpan",
        visual_count=1,
        pos=[-0.5, 0, 0.85],
        scale=0.1,
        collision_count=6,
        textures=["tex"],
        randomize_colors=False,
    )
    tub = ObjMujocoObject(
        name="medieval_tub",
        assets="medieval_tub",
        visual_count=2,
        pos=[0, 0, 0.8],
        quat=[0.7071, 0.7071, 0.0, 0.0],
        scale=0.1,
        collision_count=35,
        textures=[
            "wood_table_worn_baseColor",  # medieval_tub_0.obj
            "Metal_negro_rugoso_baseColor",  # medieval_tub_1.obj
        ],
        randomize_colors=False,
    )
    cup = ObjaverseMujocoCup(assets="kitchen/cup", pos=[0.3, 0, 0.87], name="cup", scale=0.1, collision_count=32, randomize_colors=False)

    bin = Bin(
        attributes=dict(name="bin", pos="0 0 0.8"),
    )

    particles = Composite(
        attributes=dict(type="particle", count="5 6 7", spacing="0.018", offset="0 0 0.9"),
        _children_raw="""
        <geom size=".005" rgba=".8 .2 .1 1"/>        
        """,
    )

    scene = FloatingShadowHand(
        optical_table,
        table_slab,
        camera_rig.right_camera,
        camera_rig.right_camera_r,
        camera_rig.front_camera,
        camera_rig.top_camera,
        camera_rig.left_camera,
        camera_rig.back_camera,
        bin,
        particles,
        cup,
        # brush,
        # dustpan,
        # tub,
        pos=[0, 0, 0.8],
    )

    return scene._xml | Prettify()


if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Save

    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

# Generate random values for r, g, and b
# r, g, b = random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)
from vuer_mujoco.tasks._tile_floor import TileFloor


def make_schema(**options):
    from vuer_mujoco.schemas.utils.file import Prettify
    from vuer_mujoco.vendors.robohive.robohive_object import RobohiveObj
    from vuer_mujoco.tasks._floating_robotiq import FloatingRobotiq2f85

    table = RobohiveObj(
        otype="furniture",
        asset_key="simpleTable/simpleWoodTable",
        pos=[0, 0, 0],
    )
    floor = TileFloor()
    scene = FloatingRobotiq2f85(
        table,
        floor,
        pos=[0, 0, 0.8],
        **options,
    )
    return scene._xml | Prettify()


if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Save

    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

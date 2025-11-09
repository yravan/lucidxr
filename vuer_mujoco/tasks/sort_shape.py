from pathlib import Path

from vuer_mujoco.schemas.utils.file import Save
from vuer_mujoco.schemas.components.concrete_slab import ConcreteSlab
from vuer_mujoco.tasks._floating_robotiq import FloatingRobotiq2f85
from vuer_mujoco.schemas.components.force_plate import ForcePlate


def make_schema(**options):
    from vuer_mujoco.schemas.utils.file import Prettify
    from vuer_mujoco.schemas.objects import LeBox
    from vuer_mujoco.schemas.objects import TriangleBlock
    from vuer_mujoco.schemas.objects import CircleBlock
    from vuer_mujoco.schemas.objects import SquareBlock
    from vuer_mujoco.schemas.objects.hex_block import HexBlock

    table = ConcreteSlab(pos=[0, 0, 0.6], rgba="0.8 0.8 0.8 1")

    ibox = LeBox(attributes={"name": "insertion-box"}, assets="sort_shape", pos=[0, 0, 0.7])
    square_block = SquareBlock(attributes={"name": "square"}, assets="sort_shape", pos=[0.2, -0.1, 0.7])
    triangle_block = TriangleBlock(attributes={"name": "triangle"}, assets="sort_shape", pos=[0.4, -0.1, 0.7])
    hex_block = HexBlock(attributes={"name": "hex"}, assets="sort_shape", pos=[0.2, 0.1, 0.7])
    circle_block = CircleBlock(attributes={"name": "circle"}, assets="sort_shape", pos=[0.4, 0.1, 0.7])

    work_area = ForcePlate(
        name="start-area",
        pos=(0.3, 0, 0.605),
        quat=(0, 1, 0, 0),
        type="box",
        size="0.15 0.15 0.01",
        rgba="1 0 0 0.1",
    )

    scene = FloatingRobotiq2f85(
        table,
        ibox,
        square_block,
        triangle_block,
        hex_block,
        circle_block,
        work_area,
        pos=[0, 0, 0.8],
        **options,
    )

    return scene._xml | Prettify()


def register():
    from vuer_mujoco.tasks import add_env
    from vuer_mujoco.tasks.entrypoint import make_env

    add_env(
        env_id="SortShape-v1",
        entrypoint=make_env,
        kwargs=dict(
            xml_path="sort_shape.mjcf.xml",
            workdir=Path(__file__).parent,
            mode="render",
        ),
    )


if __name__ == "__main__":
    make_schema() | Save(__file__.replace(".py", ".mjcf.xml"))

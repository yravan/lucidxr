from vuer_envs import DefaultStage, Robotiq2F85

# from vuer_envs.schemas.schema import Body
from vuer_envs.schemas.lucid_xr.furnitures.table_white import *
from vuer_envs.schemas.utils import Save, Prettify


def build_ur5e_table_scene():
    """here we create a scene with a single uR5e arm and a gripper."""

    gripper = Robotiq2F85(
        assets="robotiq_2f85",
        mocap_pos="0.4 0 1.2",
    )

    # triad = Triad(name="test")
    ur5e = UR5eForTable(
        name="ur5e",
        assets="ur5e",
        end_effector=gripper,
        attributes={"pos": "0.2 0 1.2", "quat": "1 0 0 1"},
    )
    basket = Basket(attributes={"pos": "0.7 -0.17 1.2"})
    banana = Bagel(attributes={"pos": "0.7 0.27 1.2"})
    # table = TableWhiteModern()  ## children=[basket]
    # ur5e._xml | Prettify() | Save("ur5e.mjcf.xml")

    scene = DefaultStage(
        model="ur5e table scene",
        children=(
            ur5e,
            basket,
            banana,
            gripper._mocaps,
        ),
    )
    scene._xml | Prettify() | Save("ur5e_table_scene.mjcf.xml")


if __name__ == "__main__":
    build_ur5e_table_scene()

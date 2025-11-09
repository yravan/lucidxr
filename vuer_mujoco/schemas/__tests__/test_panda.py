from vuer_mujoco import Mjcf
from vuer_mujoco.schemas.robots.franka_panda.panda import Panda
from vuer_mujoco.schemas.utils import File, Save
from vuer_mujoco.schemas.utils import minimize, minimize_many


def test_panda():
    panda = Panda(name="test_panda", pos=(0, 0, 0), quat=(0, 0, 0, 1))
    scene = Mjcf(children=panda)

    scene._xml | Save("panda.mjcf.xml")

    assert panda._minimized == File @ "panda_content_expected.xml" | minimize

    assert (panda.preamble | minimize_many) == File @ "panda_preamble_expected.xml" | minimize_many


if __name__ == "__main__":
    test_panda()

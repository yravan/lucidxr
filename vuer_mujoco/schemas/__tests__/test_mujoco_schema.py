from vuer_mujoco import minimize
from vuer_mujoco.schemas import Raw
from vuer_mujoco.schemas.schema import Body


def test_mjcf_node():
    mjcf = Body(
        tag="body",
        attributes={"name": "test_name"},
        preamble="""
        <asset> 
        <texture type='2d' name='test_texture' file='rooms/assets/textures/flat/light_gray.png'/> 
        </asset>
        """,
        children=Raw
        @ """
            <geom type='box' size='0.1 0.1 0.1' rgba='1 0 0 1'/>
            <site name='test_site' pos='0 0 0' size='0.002' rgba='1 0 0 -1'/>
        """,
    )

    assert (
        mjcf._minimized
        == """
        <body name="test_name">
            <geom type="box" size="0.1 0.1 0.1" rgba="1 0 0 1"/>
            <site name="test_site" pos="0 0 0" size="0.002" rgba="1 0 0 -1"/>
        </body>
        """
        | minimize
    )


if __name__ == "__main__":
    test_mjcf_node()

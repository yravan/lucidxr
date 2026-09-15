from lucidxr.sim.xml_schema.schema import Composite


class MuJoCoRope(Composite):
    rgba = "0.7 0 0 1"
    mass = "0.001"
    geom_size = ".004"
    damping = ".015"
    condim = "1"
    twist = "1e7"
    bend = "3e5"
    vmax = "0.005"

    _attributes = {
        "prefix": "rope_",
        "type": "cable",
        "curve": "s",
        "count": "41 1 1",
        "size": 1,
        "initial": "free",
        "offset": "0 0 0.7",
    }

    _preamble = """
        <extension>
            <plugin plugin="mujoco.elasticity.cable"/>
        </extension>
    """

    _children_raw = """
    <plugin plugin="mujoco.elasticity.cable">
        <!--Units are in Pa (SI)-->
        <config key="twist" value="{twist}"/>
        <config key="bend" value="{bend}"/>
        <config key="vmax" value="{vmax}"/>
    </plugin>
    <joint kind="main" damping="{damping}"/>
    <geom type="capsule" size="{geom_size}" rgba="{rgba}" condim="{condim}" mass="{mass}"/>
    """

from vuer_mujoco.schemas.schema import Mjcf, Body


class VuerMug(Body):
    """
    This class represents a Vuer Mug SDF body instance with pre-configured
    assets and attributes. The Signed Distance Field (SDF) is computed
    only once and reused for all instances, ensuring efficient field
    computation regardless of the number of instances.
    """
    assets = "vuer-mug"
    prefix = "v-mug"

    _attributes = {
        "name": "vuer-mug",
    }
    _preamble = """
    <extension>
      <plugin plugin="mujoco.sdf.sdflib">
        <instance name="{prefix}-sdf">
          <config key="aabb" value="0"/>
        </instance>
      </plugin>
    </extension>
    <option sdf_iterations="10" sdf_initpoints="20"/>
    
    <asset>
      <texture name="texspot" type="2d" file="{assets}/vuer.png"/>
      <material name="matspot" texture="texspot"/>
      <mesh name="spot" file="{assets}/mug.obj" scale="0.01 0.01 0.01">
        <plugin instance="{prefix}-sdf"/>
      </mesh>
    </asset>
    """

    _children_raw = """
    <freejoint/>
    <geom type="sdf" name="{name}" mesh="spot" material="matspot">
        <plugin instance="{prefix}-sdf"/>
    </geom>
    """


if __name__ == "__main__":
    from vuer_mujoco.schemas.utils.file import Prettify, Save, Raw

    mug1 = VuerMug(pos=[0, -0.1, 1.3], attributes={"name": "mug1"})
    mug2 = VuerMug(pos=[0.1, 0, 1.3], attributes={"name": "mug2"})
    plane = Raw @ "<geom type='plane' pos='0 0 0' size='1 1 1' name='floor'/>"

    scene = Mjcf(
        mug1,
        mug2,
        plane,
        assets="assets",
        _preamble="""
        <compiler angle="radian" assetdir="{assets}"/>
        """,
    )

    scene._xml | Prettify() | Save(__file__.replace(".py", ".mjcf.xml"))

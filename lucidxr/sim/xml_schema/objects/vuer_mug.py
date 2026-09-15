from lucidxr.sim.xml_schema.schema import Body


class VuerMug(Body):
    """
    This class represents a Vuer Mug SDF body instance with pre-configured
    assets and attributes. The Signed Distance Field (SDF) is computed
    only once and reused for all instances, ensuring efficient field
    computation regardless of the number of instances.
    """

    assets = "objects/vuer-mug"
    prefix = "v-mug"

    _attributes = {
        "name": "vuer-mug",
    }
    _preamble = """
    
    <option sdf_iterations="10" sdf_initpoints="20"/>
    
    <asset>
      <texture name="texspot" type="2d" file="{assets}/vuer.png"/>
      <material name="matspot" texture="texspot"/>
      <mesh name="spot" file="{assets}/mug.obj" scale="0.00933 0.0142 0.00933">
      </mesh>
    </asset>
    """

    _children_raw = """
    <freejoint/>
    <geom type="sdf" name="{name}" mesh="spot" material="matspot" mass="0.075" quat="0 0 1 1" condim="4" solimp="0.95 0.99 0.001" solref="0.003 1">
    </geom>
    <site name="mug_handle_1" pos="-0.054 0 0.075" size="0.005" rgba="1 1 1 1"/>
    <site name="mug_handle_2" pos="-0.054 0 0.056" size="0.005" rgba="1 1 1 1"/>
    <site name="mug_handle_3" pos="-0.054 0 0.037" size="0.005" rgba="1 1 1 1"/>
    """

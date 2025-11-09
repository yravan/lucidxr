from vuer_mujoco.schemas.schema import Body


class MjSDF(Body):
    assets = "objects"
    scale = "1 1 1"
    mass = 0.1
    additional_children_raw = ""
    model = "model.obj"
    texture = "texture.png"
    geom_quat = "1 0 0 0"
    additional_geom_attributes = ""

    _attributes = {
        "name": "object",
    }
    _preamble = """
    <option timestep="0.002" integrator="implicitfast" sdf_iterations="20" sdf_initpoints="40"/>
    <extension>
      <plugin plugin="mujoco.sdf.sdflib">
        <instance name="{assets}-sdf">
          <config key="aabb" value="0"/>
        </instance>
      </plugin>
    </extension>
    
    <asset>
        <texture type="2d" name="{name}-texture" file="{assets}/{texture}"/>
        <material name="{name}-material" texture="{name}-texture" specular="0.2" shininess="0.2"/>
      
        <mesh name="{name}-model" file="{assets}/{model}" scale="{scale}">
            <plugin instance="{assets}-sdf"/>
        </mesh>
    </asset>
    """

    _children_raw = """
        <joint type="free"/>
        <geom type="sdf" name="{name}-sdf" mesh="{name}-model" quat="{geom_quat}" mass="{mass}" material="{name}-material" contype="1" conaffinity="1" {additional_geom_attributes}>
            <plugin instance="{assets}-sdf"/>
        </geom>
        {additional_children_raw}
    """

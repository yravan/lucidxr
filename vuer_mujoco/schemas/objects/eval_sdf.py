from vuer_mujoco.schemas.schema import Body


class EvalSDF(Body):
    env_name = "objects"
    scale = "1 1 1"
    additional_children_raw = ""
    geom_quat = "1 0 0 0"
    additional_geom_attributes = ""
    root_asset_path = ''

    _attributes = {
        "name": "object",
    }
    _preamble = """
    <option timestep="0.002" integrator="implicitfast" sdf_iterations="20" sdf_initpoints="40"/>
    <extension>
      <plugin plugin="mujoco.sdf.sdflib">
        <instance name="{env_name}-sdf">
          <config key="aabb" value="0"/>
        </instance>
      </plugin>
    </extension>
    
    <asset>
        <material name="{name}-material" reflectance="0.5" rgba="0.2 0.2 0.2 1"/>
        <mesh name="{name}-model" file="{root_asset_path}/{env_name}/geometry/collision_mesh.obj" scale="{scale}">
            <plugin instance="{env_name}-sdf"/>
        </mesh>
    </asset>
    """

    _children_raw = """
        <geom type="sdf" mesh="{name}-model" quat="{geom_quat}" material="{name}-material" contype="1" conaffinity="1" friction="1.25 0.3 0.3" condim="4" solimp="0.95 0.99 0.001" solref="0.003 1" {additional_geom_attributes}>
            <plugin instance="{env_name}-sdf"/>
        </geom>
        {additional_children_raw}
    """

from vuer_mujoco.schemas.schema import Body


class HexBlock(Body):
    assets = "hex-block"
    prefix = "hx-block"

    _attributes = {
        "name": "hex-block",
    }
    _preamble = """
    <option timestep="0.002" integrator="implicitfast"/>

    <asset>
      <texture type="2d" name="{prefix}-warm_wood" file="{assets}/warm_wood_planks.png" />
      <material name="{prefix}-warm_wood" texture="{prefix}-warm_wood" specular="0.1" shininess="0.1" texrepeat="1 1"/>

      <mesh name="{prefix}-obj" file="{assets}/hex.obj" scale="{scale} {scale} {scale}"/>
    </asset>
    """

    _children_raw = """
        <joint type="free"/>
        <geom type="mesh" mesh="{prefix}-obj" material="{prefix}-warm_wood" />
        <site name="{name}" pos="0 0 0" size="0.02" rgba="1 1 1 0"/>
    """


class TriangleBlock(Body):
    assets = "triangle-block"
    prefix = "tr-block"

    _attributes = {
        "name": "triangle-block",
    }
    _preamble = """
    <option timestep="0.002" integrator="implicitfast"/>
    
    <asset>
      <texture type="2d" name="{prefix}-warm_wood" file="{assets}/warm_wood_planks.png" />
      <material name="{prefix}-warm_wood" texture="{prefix}-warm_wood" specular="0.1" shininess="0.1" texrepeat="1 1"/>
      
      <mesh name="{prefix}-obj" file="{assets}/triangle.obj" scale="{scale} {scale} {scale}"/>
    </asset>
    """

    _children_raw = """
        <joint type="free"/>
        <geom type="mesh" mesh="{prefix}-obj" material="{prefix}-warm_wood" />
        <site name="{name}" pos="0 0 0" size="0.02" rgba="1 1 1 0"/>
    """


class SquareBlock(Body):
    assets = "square-block"
    prefix = "sq-block"

    _attributes = {
        "name": "square-block",
    }
    _preamble = """
    <option timestep="0.002" integrator="implicitfast"/>
    
    <asset>
      <texture type="2d" name="{prefix}-warm_wood" file="{assets}/warm_wood_planks.png" />
      <material name="{prefix}-warm_wood" texture="{prefix}-warm_wood" specular="0.1" shininess="0.1" texrepeat="1 1"/>
      
      <mesh name="{prefix}-obj" file="{assets}/square.obj" scale="{scale} {scale} {scale}"/>
    </asset>
    """

    _children_raw = """
        <joint type="free"/>
        <geom type="mesh" mesh="{prefix}-obj" material="{prefix}-warm_wood" />
        <site name="{name}" pos="0 0 0" size="0.02" rgba="1 1 1 0"/>
    """


class CircleBlock(Body):
    assets = "circle-block"
    prefix = "cr-block"

    _attributes = {
        "name": "circle-block",
    }
    _preamble = """
    <option timestep="0.002" integrator="implicitfast"/>
    
    <asset>
      <texture type="2d" name="{prefix}-warm_wood" file="{assets}/warm_wood_planks.png" />
      <material name="{prefix}-warm_wood" texture="{prefix}-warm_wood" specular="0.1" shininess="0.1" texrepeat="1 1"/>
      
      <mesh name="{prefix}-obj" file="{assets}/circle.obj" scale="{scale} {scale} {scale}"/>
    </asset>
    """

    _children_raw = """
        <joint type="free"/>
        <geom type="mesh" mesh="{prefix}-obj" material="{prefix}-warm_wood" />
        <site name="{name}" pos="0 0 0" size="0.02" rgba="1 1 1 0"/>
    """


class LeBox(Body):
    assets = "insertion-box"
    prefix = "i-box"

    _attributes = {
        "name": "insertion-box",
    }
    _preamble = """
    <option timestep="0.002" integrator="implicitfast" sdf_iterations="20" sdf_initpoints="40"/>
    <extension>
      <plugin plugin="mujoco.sdf.sdflib">
        <instance name="{prefix}-sdf">
          <config key="aabb" value="0"/>
        </instance>
      </plugin>
    </extension>
    
    <asset>
      <texture type="2d" name="{prefix}-light_wood" file="{assets}/light_wood_planks.png" />
      <material name="{prefix}-light_wood" texture="{prefix}-light_wood" specular="0.1" shininess="0.1" texrepeat="1 1"/>
      
      <mesh name="{prefix}-obj" file="{assets}/block.obj" scale="{scale} {scale} {scale}">
        <plugin instance="{prefix}-sdf"/>
      </mesh>
    </asset>
    """

    _children_raw = """
    <joint type="free"/>
    <geom type="sdf" mesh="{prefix}-obj" material="{prefix}-light_wood" contype="1" conaffinity="1">
        <plugin instance="{prefix}-sdf"/>
    </geom>
    <site name="{name}-hexblock" pos="0.03 -0.033 0.1" size="0.02" rgba="1 1 1 0"/>
    <site name="{name}-squareblock" pos="-0.03 0.03 0.1" size="0.02" rgba="1 1 1 0"/>
    <site name="{name}-circleblock" pos="0.031 0.031 0.1" size="0.02" rgba="1 1 1 0"/>
    <site name="{name}-triangleblock" pos="-0.03 -0.033 0.1" size="0.02" rgba="1 1 1 0"/>
    """

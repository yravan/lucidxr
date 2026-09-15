"""Shape sorting pieces share material, contact, and marker definitions."""

from lucidxr.sim.xml_schema.schema import Body


class ShapeBlock(Body):
    assets = "objects/sort_shape"
    scale = 1.0
    shape = "hex"
    prefix = "hx-block"
    _attributes = {"name": "hex-block"}
    _preamble = """
    <option timestep="0.002" integrator="implicitfast"/>
    <asset>
      <texture type="2d" name="{prefix}-warm_wood" file="{assets}/warm_wood_planks.png"/>
      <material name="{prefix}-warm_wood" texture="{prefix}-warm_wood" specular="0.1" shininess="0.1" texrepeat="1 1"/>
      <mesh name="{prefix}-obj" file="{assets}/{shape}.obj" scale="{scale} {scale} {scale}"/>
    </asset>
    """
    _children_raw = """
    <joint type="free"/>
    <geom type="mesh" mesh="{prefix}-obj" material="{prefix}-warm_wood"/>
    <site name="{name}" pos="0 0 0" size="0.02" rgba="1 1 1 0"/>
    """


class HexBlock(ShapeBlock):
    pass


class TriangleBlock(ShapeBlock):
    shape = "triangle"
    prefix = "tr-block"
    _attributes = {"name": "triangle-block"}


class SquareBlock(ShapeBlock):
    shape = "square"
    prefix = "sq-block"
    _attributes = {"name": "square-block"}


class CircleBlock(ShapeBlock):
    shape = "circle"
    prefix = "cr-block"
    _attributes = {"name": "circle-block"}


class LeBox(Body):
    assets = "objects/sort_shape"
    prefix = "i-box"
    scale = 1.0

    _attributes = {
        "name": "insertion-box",
    }
    _preamble = """
    <option timestep="0.002" integrator="implicitfast" sdf_iterations="20" sdf_initpoints="40"/>
    
    
    <asset>
      <texture type="2d" name="{prefix}-light_wood" file="{assets}/light_wood_planks.png" />
      <material name="{prefix}-light_wood" texture="{prefix}-light_wood" specular="0.1" shininess="0.1" texrepeat="1 1"/>
      
      <mesh name="{prefix}-obj" file="{assets}/block.obj" scale="{scale} {scale} {scale}">
      </mesh>
    </asset>
    """

    _children_raw = """
    <joint type="free"/>
    <geom type="sdf" mesh="{prefix}-obj" material="{prefix}-light_wood" contype="1" conaffinity="1">
    </geom>
    <site name="{name}-hexblock" pos="0.03 -0.033 0.1" size="0.02" rgba="1 1 1 0"/>
    <site name="{name}-squareblock" pos="-0.03 0.03 0.1" size="0.02" rgba="1 1 1 0"/>
    <site name="{name}-circleblock" pos="0.031 0.031 0.1" size="0.02" rgba="1 1 1 0"/>
    <site name="{name}-triangleblock" pos="-0.03 -0.033 0.1" size="0.02" rgba="1 1 1 0"/>
    """

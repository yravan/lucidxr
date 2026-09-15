from lucidxr.sim.xml_schema.schema import Body


class Triad(Body):
    name = ""
    template = """
    <body name="{name}-triad-x" pos="1 0 0">
      <geom type="box" size="0.05 0.05 0.05" rgba="1 0 0 0.5"/>
    </body>
    <body name="{name}-axis-x" pos="0.5 0 0">
      <geom type="box" size="0.5 0.01 0.01" rgba="1 0 0 0.5"/>
    </body>
    
    <body name="{name}-triad-y" pos="0 1 0">
      <geom type="box" size="0.05 0.05 0.05" rgba="0 1 0 0.5"/>
    </body>
    <body name="{name}-axis-y" pos="0 0.5 0">
      <geom type="box" size="0.01 0.5 0.01" rgba="0 1 0 0.5"/>
    </body>
    
    <body name="{name}-triad-z" pos="0 0 1">
      <geom type="box" size="0.05 0.05 0.05" rgba="0 0 1 0.5"/>
    </body>
    <body name="{name}-axis-z" pos="0 0 0.5">
      <geom type="box" size="0.01 0.01 0.5" rgba="0 0 1 0.5"/>
    </body>
    """

from lucidxr.sim.xml_schema.schema import Body


class Box(Body):
    template = """
    <body {attributes}>
      <geom type="box" size="{size}" rgba="{rgba}"/>
    </body>
    """

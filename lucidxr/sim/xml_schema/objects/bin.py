from lucidxr.sim.xml_schema.schema import Body


class Bin(Body):
    # half‐sizes of the interior (m)
    length = 0.07  # half x‐extent
    width = 0.10  # half y‐extent
    height = 0.02  # half z‐extent of walls
    thickness = 0.005  # half z‐extent of bottom & half‐wall thickness

    @property
    def bottom_z(self):
        return self.thickness

    @property
    def wall_z(self):
        return self.height + self.thickness

    @property
    def front_y(self):
        return -(self.width - self.thickness)

    @property
    def back_y(self):
        return self.width - self.thickness

    @property
    def left_x(self):
        return -(self.length - self.thickness)

    @property
    def right_x(self):
        return self.length - self.thickness

    rgba = "0.7 0.7 0.7 1.0"

    _attributes = {
        "name": "bin",
    }

    _children_raw = """
    <!-- free‐floating bin -->
    <joint type="free" name="{name}_joint"/>

    <!-- bottom panel -->
    <geom name="{name}_bottom"
          type="box"
          size="{length} {width} {thickness}"
          pos="0 0 {bottom_z}"
          rgba="{rgba}"/>

    <!-- front & back walls -->
    <geom name="{name}_front"
          type="box"
          size="{length} {thickness} {height}"
          pos="0 {front_y} {wall_z}"
          rgba="{rgba}"/>
    <geom name="{name}_back"
          type="box"
          size="{length} {thickness} {height}"
          pos="0 {back_y} {wall_z}"
          rgba="{rgba}"/>

    <!-- left & right walls -->
    <geom name="{name}_left"
          type="box"
          size="{thickness} {width} {height}"
          pos="{left_x} 0 {wall_z}"
          rgba="{rgba}"/>
    <geom name="{name}_right"
          type="box"
          size="{thickness} {width} {height}"
          pos="{right_x} 0 {wall_z}"
          rgba="{rgba}"/>
    """.strip()

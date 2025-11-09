from vuer_mujoco.schemas.schema import Body

class Bin(Body):
    # half‐sizes of the interior (m)
    length     = 0.07   # half x‐extent
    width      = 0.10   # half y‐extent
    height     = 0.02   # half z‐extent of walls
    thickness  = 0.005  # half z‐extent of bottom & half‐wall thickness

    # precomputed positions (m)
    bottom_z   = thickness
    wall_z     = height + thickness
    front_y    = -(width  - thickness)
    back_y     =  (width  - thickness)
    left_x     = -(length - thickness)
    right_x    =  (length - thickness)

    rgba       = "0.7 0.7 0.7 1.0"

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

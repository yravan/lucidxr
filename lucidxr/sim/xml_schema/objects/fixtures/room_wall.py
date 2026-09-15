from lucidxr.sim.xml_schema.schema import Body


class RoomWall(Body):
    """
    A single rectangular wall panel, with an optional thicker *backing* slab
    sitting 12 cm behind it.
    ───────────────────────────────────────────────────────────────────
    • `panel_sz = (½-width, ½-height, ½-thickness)`  –  for the visible wall
    • `backing_sz` defaults to panel_sz with `z` = backing_thickness
    • visual geoms are mass-0, non-colliding (group 1)
    • collision geoms are opaque red boxes (group 3) – change as you like
    """

    # textures / materials --------------------------------------------------
    assets = "wall"  # folder with wall textures
    prefix = "wall"  # XML-name stem
    show_texture = True

    _preamble = """
    <asset>
        <texture type="2d" name="{prefix}_tex_paint" file="{assets}/paint.png"/>
        <material name="{prefix}_paint_mat" texture="{prefix}_tex_paint" shininess="0.15"/>
    </asset>"""

    # -----------------------------------------------------------------------
    def __init__(
        self,
        *,
        panel_sz: tuple[float, float, float],  # (½w, ½h, ½t)
        pos: tuple[float, float, float],  # world-space position
        quat: tuple[float, float, float, float],  # orientation
        name: str = "room_wall",
        backing: bool = True,  # include backing slab?
        backing_thickness: float = 0.10,  # metres
        **kwargs,
    ):
        self.panel_sz = panel_sz
        self.backing = backing

        # backing geom uses the same half-width & half-height but larger z
        hx, hy, hz = panel_sz
        self.backing_sz = f"{hx} {hy} {backing_thickness / 2:.3f}"

        attributes = dict(name=name, pos=" ".join(map(str, pos)), quat=" ".join(map(str, quat)))

        # feed through to Body-base
        self.show_texture = kwargs.get("show_texture", self.show_texture)
        if not self.show_texture:
            self._preamble = """
            <asset>
                <material name="{prefix}_paint_mat" rgba="0.7 0.7 0.7 1" shininess="0.15"/>
            </asset>
            """  # disable texture/material preamble
        super().__init__(attributes=attributes, **kwargs)

    # -----------------------------------------------------------------------
    @property
    def _children_raw(self) -> str:
        hx, hy, hz = self.panel_sz
        panel_sz_str = f"{hx} {hy} {hz}"

        backing_raw = (
            f"""
        <geom name="{{name}}_back_col" size="{self.backing_sz}"
              type="box" group="3" rgba="0.5 0 0 1"/>
        <geom name="{{name}}_back_vis" size="{self.backing_sz}"
              type="box" contype="0" conaffinity="0" group="0" mass="0"
              material="{{prefix}}_paint_mat"/>"""
            if self.backing
            else ""
        )

        return f"""
    <geom name="{{name}}_panel_col" size="{panel_sz_str}"
          type="box" group="3" rgba="0.5 0 0 1"/>
    <geom name="{{name}}_panel_vis" size="{panel_sz_str}"
          type="box" contype="0" conaffinity="0" group="0" mass="0"
          material="{{prefix}}_paint_mat"/>{backing_raw}
    """

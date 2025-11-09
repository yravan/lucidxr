# file: kitchen_modules/drawer_stack.py
from vuer_mujoco.schemas.schema import Body
from vuer_mujoco.schemas.room_xmls.room_components.drawer          import KitchenDrawer
from vuer_mujoco.schemas.room_xmls.room_components.drawer_visual   import KitchenDrawerVisual
from vuer_mujoco.schemas.room_xmls.room_components.single_cabinet  import KitchenSingleCabinet

class DrawerStack(Body):
    """
    Drawer-plus-cabinet stack.

    base_pos / base_quat  – pose of the *frame* (back of the cabinet).  
    width                 – half-width passed straight to KitchenDrawer.  
    All sub-parts are children of this body, so moving / rotating the
    DrawerStack moves the whole assembly.
    """

    # fixed vertical offsets of the three sub-parts (metres)
    _Z_DRAWER   = 0.78
    _Z_CABINET  = 0.362
    _Z_BAR      = 0.025

    def __init__(
        self,
        *,
        base_pos:   str | tuple,
        base_quat:  str | tuple = "1 0 0 0",
        width:      float       = 0.25,
        assets:     str         = "assets",
        name:       str         = "stack",
        visual:     bool        = False,
        **kwargs,
    ):
        # turn tuples into strings if needed
        pos_str  = " ".join(map(str, base_pos))  if isinstance(base_pos,  (tuple, list)) else base_pos
        quat_str = " ".join(map(str, base_quat)) if isinstance(base_quat, (tuple, list)) else base_quat

        # ── root-body attributes (pose of the whole stack) ──
        attributes = dict(name=name, pos=pos_str, quat=quat_str)

        # children: drawer + cabinet + bottom bar
        if visual:
            drawer = KitchenDrawerVisual( assets=f"{assets}/drawer",
                                          width=width,
                                          attributes=dict(name=f"{name}_drawer",
                                                          pos=f"0 0 {self._Z_DRAWER}",
                                                          quat="1 0 0 0"),**kwargs )
        else:
            drawer   = KitchenDrawer( assets=f"{assets}/drawer",
                                    width=width,
                                      prefix=f"{name}_drawer",
                                    attributes=dict(name=f"{name}_drawer",
                                                    pos=f"0 0 {self._Z_DRAWER}",
                                                    quat="1 0 0 0"),**kwargs )

        cabinet  = KitchenSingleCabinet( assets=f"{assets}/cabinet",
                                         attributes=dict(name=f"{name}_cab",
                                                         pos=f"0 0 {self._Z_CABINET}",
                                                         quat="1 0 0 0"),**kwargs )

        bottom   = Body(
            attributes=dict(name=f"{name}_bar", pos=f"0 0 {self._Z_BAR}"),
            _children_raw="""
                <geom name="{name}_bar_geom"
                      type="box" size="0.25 0.25 0.025"
                      density="1000"
                      material="single-cabinet_body_mat"/>
            """,**kwargs
        )

        # feed everything to the Body base-class
        super().__init__(drawer, cabinet, bottom, attributes=attributes, **kwargs)

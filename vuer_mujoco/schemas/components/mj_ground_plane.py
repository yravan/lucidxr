from vuer_mujoco.schemas.schema import Body


class GroundPlane(Body):
    _attributes = {
        "name": "ground-plane",
        # "childclass": "concrete-slab",
    }
    _preamble = """
    <asset>
      <texture type="2d" name="{name}-ground-plane" builtin="checker" mark="edge" rgb1="0.2 0.3 0.4" rgb2="0.1 0.2 0.3" markrgb="0.8 0.8 0.8" width="300" height="300"/>
      <material name="{name}-ground-plane" texture="{name}-ground-plane" texuniform="true" texrepeat="5 5" reflectance="0.2"/>
    </asset>
    """
    _children_raw = """
    <body name="{name}-floor">
      <geom name="{name}-floor" size="0 0 0.05" type="plane" material="{name}-ground-plane"/>
    </body>
    """

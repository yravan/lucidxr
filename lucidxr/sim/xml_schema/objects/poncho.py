"""Triangulated cloth with native MuJoCo bending elasticity."""

import json

from lucidxr.sim.assets import asset_root
from lucidxr.sim.xml_schema.schema import Body


class Poncho(Body):
    _attributes = {"name": "poncho"}
    _preamble = """
    <option timestep="0.01" integrator="implicitfast" viscosity=".3" solver="CG" tolerance="1e-6">
      <flag energy="enable"/>
    </option>
    
    """

    def __init__(self, name, rgba, scale: float = 1.0, asset_directory=None, **kwargs):
        super().__init__(attributes=kwargs.pop("attributes", {}) or {}, **kwargs)

        # 1) scale the points exactly as before…
        mesh = json.loads((asset_root(asset_directory) / "objects/poncho/mesh.json").read_text())
        nums = [value for point in mesh["points"] for value in point]
        scaled = []
        for x, y, z in zip(nums[0::3], nums[1::3], nums[2::3]):
            scaled.extend([x * scale, y * scale, z])
        point_str = "\n                ".join(
            f"{scaled[i]:.6f} {scaled[i + 1]:.6f} {scaled[i + 2]:.6f}" for i in range(0, len(scaled), 3)
        )

        element_str = " ".join(str(value) for triangle in mesh["triangles"] for value in triangle)

        self._children_raw = f"""
        <flexcomp name="{name}" type="direct" rgba="{rgba}" radius="{0.01 * scale:.6f}" dim="2"
                mass="1"
                point="{point_str}"
                    element="{element_str}">
        <edge equality="true" damping="0.1"/>
        <contact solref="0.003"/>
        <elasticity poisson="0" thickness="{8e-3 * scale:.6e}" young="3e5" elastic2d="bend"/>
        </flexcomp>
        """

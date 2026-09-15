"""Camera elements and look-at orientation in MuJoCo coordinates."""

import numpy as np

from lucidxr.sim.xml_schema.base import Raw, Xml


def xyaxes(origin, anchor):
    """Camera X/Y axes, using world Z as up except at the vertical poles."""
    origin = np.asarray(origin.split() if isinstance(origin, str) else origin, dtype=float)
    anchor = np.asarray(anchor.split() if isinstance(anchor, str) else anchor, dtype=float)
    if origin.shape != (3,) or anchor.shape != (3,):
        raise ValueError("Camera position and lookat must have three coordinates")
    z = origin - anchor
    norm = np.linalg.norm(z)
    if not np.isfinite(norm) or norm == 0:
        raise ValueError("Camera position and lookat must be finite and distinct")
    z /= norm
    x = np.cross((0, 0, 1), z)
    if np.linalg.norm(x) < 1e-12:
        x = np.cross((0, 1, 0), z)
    x /= np.linalg.norm(x)
    return [*x, *np.cross(z, x)]


def make_camera(name="camera", *, pos, lookat=None, **attributes) -> Raw:
    if lookat is not None:
        if any(key in attributes for key in ("quat", "axisangle", "euler", "xyaxes", "zaxis")):
            raise ValueError("Use lookat or an explicit camera orientation")
        attributes["xyaxes"] = xyaxes(pos, lookat)
    return Raw(str(Xml(tag="camera", name=name, pos=pos, **attributes)))

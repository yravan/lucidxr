"""Reusable three-point lighting, expressed in MuJoCo coordinates."""

from lucidxr.sim.xml_schema.schema import Group
from lucidxr.sim.xml_schema.simple_components.light import make_light
from lucidxr.sim.xml_schema.transforms.mujoco import Vector3, t2m_vec


class LightingRig(Group):
    """Three lights positioned relative to a scene-selected origin."""

    def __init__(self, pos=(0, 0, 0)):
        origin = Vector3(*pos)
        specifications = (
            ("key", (1, 0.5, -0.5), (-1, -0.5, 0.5), 45, 0.3),
            ("fill", (0.8, 0.4, 0.7), (-0.8, -0.6, -0.5), 60, 0.18),
            ("back", (-0.8, 1.2, 0), (-1, 1, 0), 50, 0.5),
        )
        lights = []
        for name, offset, direction, cutoff, intensity in specifications:
            light = make_light(
                name,
                pos=origin + t2m_vec(*offset),
                dir=t2m_vec(*direction),
                cutoff=cutoff,
                diffuse=(intensity,) * 3,
                directional=True,
            )
            setattr(self, name, light)
            lights.append(light)
        super().__init__(*lights)


def make_lighting_rig(pos=(0, 0, 0)) -> LightingRig:
    return LightingRig(pos)

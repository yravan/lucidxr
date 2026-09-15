"""Push t: composed from the shared XML schema library."""

from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.objects.tshape import TShape
from lucidxr.sim.xml_schema.scene_components.cameras.rig_ortho import make_camera_rig
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.planar_pusher import PlanarPusherRig
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.schema import Mjcf
from lucidxr.sim.xml_schema.simple_components.concrete_slab import ConcreteSlabT as ConcreteSlab
from lucidxr.sim.xml_schema.transforms.mujoco import Vector3


class PushT(Scene):
    def build(self) -> Mjcf:
        table = ConcreteSlab(pos=[0, 0, 0.6], rgba="0.8 0.8 0.8 1", roughness="0.2")
        rig_origin = table.surface_origin + Vector3(x=-0.55, y=0, z=-0.3)
        camera_rig = make_camera_rig(rig_origin)
        tee = TShape(pos=[0, -0.09, 0.6])
        scene = Mjcf(
            WorldSettings("pastel"),
            LightingRig([0, 0.19, 0.65]),
            table,
            tee,
            *camera_rig.get_cameras(),
            PlanarPusherRig(pos=[0, 0.19, 0.65]),
        )
        return scene

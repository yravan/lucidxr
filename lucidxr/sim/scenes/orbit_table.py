"""Orbit table: composed from the shared XML schema library."""

from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.objects.mj_sdf import MjSDF
from lucidxr.sim.xml_schema.objects.orbit_table import OpticalTable
from lucidxr.sim.xml_schema.scene_components.cameras.rig import make_camera_rig
from lucidxr.sim.xml_schema.scene_components.lighting import make_lighting_rig
from lucidxr.sim.xml_schema.schema import Mjcf


class OrbitTable(Scene):
    def build(self) -> Mjcf:
        from lucidxr.sim.xml_schema.schema import Mjcf

        optical_table = OpticalTable(
            pos=[0, 0, 0.79], assets="objects/optical_table", _attributes={"name": "optical_table"}
        )
        lighting = make_lighting_rig(optical_table._pos)
        teddy_bear = MjSDF(
            pos=[0.2, 0.2, 0.9],
            assets="objects/teddy_bear",
            _attributes={"name": "teddy-bear", "quat": "0 0.707 0.707 0"},
            scale=".1 .1 .1",
        )
        mug_tree = MjSDF(
            pos=[0.2, 0.3, 0.9],
            assets="objects/mug_tree",
            _attributes={"name": "mug-tree", "quat": "0 0.707 0.707 0"},
            scale=".1 .1 .1",
        )
        camera_stereo_rig = make_camera_rig(optical_table._pos + [0.35, 0, 0])
        scene = Mjcf(
            lighting.key,
            camera_stereo_rig.top_camera,
            camera_stereo_rig.left_camera,
            camera_stereo_rig.right_camera,
            camera_stereo_rig.front_camera,
            lighting.fill,
            lighting.back,
            optical_table,
            teddy_bear,
            mug_tree,
        )
        return scene

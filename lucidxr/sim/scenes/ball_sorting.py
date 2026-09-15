"""Ball sorting: composed from the shared XML schema library."""

from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.adapters.robohive.robohive_object import RobohiveObj
from lucidxr.sim.xml_schema.objects.mj_sdf import MjSDF
from lucidxr.sim.xml_schema.scene_components.cameras.rig_calibrated import make_camera_rig
from lucidxr.sim.xml_schema.scene_components.cameras.rig_stereo import make_origin_stereo_rig
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.ur5 import UR5Robotiq2f85
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.schema import Mjcf


class BallSorting(Scene):
    def build(self) -> Mjcf:
        options = dict(self.options)
        asset_directory = self.assets
        x_center, y_center = (0.5, -0.15)
        from lucidxr.sim.xml_schema.objects.cylinder import Cylinder

        robohive_table = RobohiveObj(
            otype="furniture",
            asset_key="simpleTable/simpleWoodTable",
            pos=[0.4, 0, 0],
            quat=[0.7071, 0, 0, 0.7071],
            local_robohive_root=asset_directory / "adapters/robohive" if asset_directory else None,
        )
        camera_rig = make_camera_rig(pos=[0, 0, 0.77])
        stereo_rig = make_origin_stereo_rig(pos=[0, 0, 0.77])
        box = MjSDF(
            pos=[0.465, 0.07, 0.82],
            quat=[1, 0, 0, 0],
            assets="objects/ball_sorting_toy",
            geom_quat="-0.5 -0.5 0.5 0.5",
            _attributes={"name": "ball-sorting-toy"},
            scale="0.12 0.12 0.12",
            additional_children_raw="""
        <site name="hole-1" pos="0.08 0 0.05" size="0.03" rgba="1 0 0 0" type="sphere"/>
        """,
        )
        ball_1 = Cylinder(
            pos=[x_center + 0.05, y_center, 0.79],
            quat=[0, 0, 1, 0],
            rgba="1 0.5 0 1",
            _attributes={"name": "cylinder-orange"},
        )
        ball_2 = Cylinder(
            pos=[x_center - 0.05, y_center, 0.79],
            quat=[0, 0, 1, 0],
            rgba="0 0 1 1",
            _attributes={"name": "cylinder-blue"},
        )
        children = [*camera_rig.get_cameras(), *stereo_rig.get_cameras(), robohive_table, box, ball_1, ball_2]
        scene = Mjcf(
            WorldSettings("pastel"),
            LightingRig([0, 0, 0.77]),
            *children,
            UR5Robotiq2f85(pos=[0, 0, 0.77], **options, camera_rig=camera_rig),
        )
        return scene

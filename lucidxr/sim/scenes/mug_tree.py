"""Mug tree: composed from the shared XML schema library."""

from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.objects.mj_sdf import MjSDF
from lucidxr.sim.xml_schema.objects.orbit_table import OpticalTable
from lucidxr.sim.xml_schema.objects.vuer_mug import VuerMug
from lucidxr.sim.xml_schema.scene_components.cameras.rig_calibrated import make_camera_rig
from lucidxr.sim.xml_schema.scene_components.cameras.rig_stereo import make_origin_stereo_rig
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.floating_robotiq import FloatingRobotiq2f85
from lucidxr.sim.xml_schema.scene_components.robots.ur5 import UR5Robotiq2f85
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.schema import Mjcf
from lucidxr.sim.xml_schema.simple_components.concrete_slab import ConcreteSlab


class MugTree(Scene):
    def build(self) -> Mjcf:
        options = dict(self.options)
        mode = options.pop("mode", "cameraready")
        show_robot = options.pop("show_robot", False)
        center = 0
        x1, y1 = (center - 0.05, -0.025)
        x2, y2 = (center + 0.17, 0.0)
        optical_table = OpticalTable(
            pos=[-0.4, 0, 0.77], assets="objects/optical_table", _attributes={"name": "table_optical"}
        )
        table = ConcreteSlab(
            assets="objects/optical_table",
            pos=[0, 0, 0.76],
            group=4,
            rgba="0.8 0 0 0.0",
            _attributes={"name": "table"},
        )
        stereo_cameras = make_origin_stereo_rig(pos=[-0.4, 0, 0.77])
        camera_rig = make_camera_rig(pos=[-0.4, 0, 0.77])
        mug = VuerMug(pos=[x1, y1, 0.85], quat=[0, 0, 0, 1], _attributes={"name": "mug"})
        mug_tree = MjSDF(
            pos=[x2, y2, 1],
            assets="objects/mug_tree",
            mass=0.3,
            _attributes={"name": "tree", "quat": "0.5 0.5 0.5 0.5"},
            additional_children_raw="""	<site name="tree_goal_1" pos="-.03 0.076 -0.036" size="0.007" rgba="1 1 1 1"/>
                                      	<site name="tree_goal_2" pos="-.03 0.066 -0.016" size="0.007" rgba="1 1 1 1"/>
                                      	<site name="tree_goal_3" pos="-.03 0.071 -0.026" size="0.007" rgba="1 1 1 1"/>
                                      	<site name="tree_goal_4" pos="-.03 0.081 -0.046" size="0.007" rgba="1 1 1 1"/>
                                      	<site name="tree_goal_5" pos="-.03 0.086 -0.056" size="0.007" rgba="1 1 1 1"/>
                                      	<site name="tree_goal_6" pos="-.03 0.091 -0.066" size="0.007" rgba="1 1 1 1"/>
                                        """,
            scale="0.17 0.2118 0.17",
        )
        children = [*camera_rig.get_cameras(), *stereo_cameras.get_cameras(), mug_tree, mug, table]
        if mode == "demo":
            pass
        elif mode == "cameraready":
            children += [optical_table]
        if show_robot:
            scene = Mjcf(
                WorldSettings("pastel"),
                LightingRig([-0.4, 0, 0.77]),
                *children,
                UR5Robotiq2f85(pos=[-0.4, 0, 0.77], **options, camera_rig=camera_rig),
            )
        else:
            scene = Mjcf(
                WorldSettings("pastel"),
                LightingRig([-0.1, 0, 0.9]),
                *children,
                FloatingRobotiq2f85(pos=[-0.1, 0, 0.9], **options, camera_rig=camera_rig),
            )
        return scene

"""Tie knot: composed from the shared XML schema library."""

from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.objects.orbit_table import OpticalTable
from lucidxr.sim.xml_schema.scene_components.cameras.rig_calibrated import make_camera_rig
from lucidxr.sim.xml_schema.scene_components.cameras.rig_stereo import make_origin_stereo_rig
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.floating_robotiq import FloatingRobotiq2f85
from lucidxr.sim.xml_schema.scene_components.robots.panda import PandaTomika
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.schema import Body, FreeBody, Mjcf
from lucidxr.sim.xml_schema.simple_components.concrete_slab import ConcreteSlab


class TieKnot(Scene):
    def build(self) -> Mjcf:
        options = dict(self.options)
        mode = options.pop("mode", "cameraready")
        robot = options.pop("robot", "panda")
        show_robot = options.pop("show_robot", False)
        x1, y1 = (0.05, 0)
        from lucidxr.sim.xml_schema.objects.rope import MuJoCoRope

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
        camera_rig = make_camera_rig(
            pos=(-0.3, 0, 1.07),
            positions={"left": (0.14, 0.355, 1.2), "right": (0.075, -0.355, 1.2)},
            wrist_pos="0.1 0.0 0.01",
            wrist_quat="-0.11 0.7 -0.7 0.11",
        )
        stereo_cameras = make_origin_stereo_rig(pos=(-0.3, 0, 1.07))

        if robot != "panda":
            raise ValueError(f"Unknown robot: {robot}")
        panda = PandaTomika(
            name="test_panda", gripper_name="test_gripper", wrist_mount=camera_rig.wrist_camera(name="panda_wrist")
        )
        rope = MuJoCoRope(
            pos=[x1, y1, 1.1],
            damping=0.0005,
            twist=10.0,
            bend=10.0,
            geom_size=0.008,
            attributes={
                "prefix": "rope_",
                "count": "50 1 1",
                "curve": "s",
                "size": "0.43",
                "initial": "none",
                "offset": "0 0 0.8",
            },
        )
        rope_anchor = Body(
            """
          <!-- translate along x -->
        <joint name="jx" type="slide" axis="1 0 0"
               damping="500" frictionloss="200" armature="5"/>
        <!-- translate along y -->
        <joint name="jy" type="slide" axis="0 1 0"
               damping="500" frictionloss="200" armature="5"/>
        <!-- optional: rotate about z in the plane -->
        <!-- <joint name="jz" type="hinge" axis="0 0 1"
               damping="200" frictionloss="50" armature="1"/> -->
        <!-- your geoms here -->
        <geom type="sphere" size="0.01" contype="0" conaffinity="0" rgba="1 1 1 0"/>
        """,
            pos=[x1, y1, 1.1],
            quat=[1, 0, 0, 0],
            attributes={"name": "rope_anchor"},
            postamble="""
        <equality>
            <weld body1="rope_B_first" body2="rope_anchor" relpose="0 0 0  1 0 0 0" solref="0.001 3" solimp="0.9 0.95 0.01"/>
        </equality>
        """,
        )
        rope = FreeBody(rope)
        children = [*camera_rig.get_cameras(), *stereo_cameras.get_cameras(), table, rope, rope_anchor]
        if mode == "demo":
            pass
        elif mode == "cameraready":
            children += [optical_table]
        if show_robot:
            children.append(panda)
        scene = Mjcf(
            WorldSettings("pastel"),
            LightingRig([-0.0, 0, 1.2]),
            *children,
            FloatingRobotiq2f85(pos=[-0.0, 0, 1.2], camera_rig=camera_rig, **options),
        )
        return scene

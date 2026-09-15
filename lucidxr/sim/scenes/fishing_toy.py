"""Fishing toy: composed from the shared XML schema library."""

from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.base import Raw
from lucidxr.sim.xml_schema.objects.mj_sdf import MjSDF
from lucidxr.sim.xml_schema.scene_components.cameras.rig import make_camera_rig
from lucidxr.sim.xml_schema.scene_components.lighting import make_lighting_rig
from lucidxr.sim.xml_schema.scene_components.robots.panda import PandaTomika
from lucidxr.sim.xml_schema.scene_components.tables import OpticalTabletop
from lucidxr.sim.xml_schema.schema import Mjcf


class FishingToy(Scene):
    def build(self) -> Mjcf:
        workspace = OpticalTabletop()
        options = dict(self.options)
        mode = options.pop("mode", "cameraready")
        robot = options.pop("robot", "panda")
        show_robot = options.pop("show_robot", False)
        dual_gripper = options.pop("dual_gripper", True)
        from lucidxr.sim.xml_schema.objects.rope import MuJoCoRope
        from lucidxr.sim.xml_schema.schema import Mjcf

        if robot != "panda":
            raise ValueError(f"Unknown robot: {robot}")
        panda = PandaTomika(name="test_panda", gripper_name="test_gripper", wrist_mount="")
        light_rig = make_lighting_rig(workspace.surface_origin)
        camera_rig = make_camera_rig(workspace.surface_origin)
        rope = MuJoCoRope(
            rgba="0.6 0.6 0.6 1.0",
            geom_size=".003",
            damping="0.0001",
            bend="3e3",
            twist="1e5",
            vmax="0.001",
            attributes={
                "prefix": "rope_",
                "count": "25 1 1",
                "size": "0.24",
                "curve": "s",
                "offset": "0 0 1.1",
            },
            postamble="""
        <equality>
            <connect name="anchor" body1="{prefix}B_first" body2="slider-anchor" anchor="0.0 0 0" solref="0.02 1" solimp="0.95 0.95 0.001"/>
            <connect name="anchor-2" body1="{prefix}B_3" body2="slider-anchor-2" anchor="0 0 0" solref="0.02 1" solimp="0.95 0.95 0.001"/>
            <connect name="hook" body1="{prefix}B_last" body2="hook-sphere" anchor="0 0 0" solref="0.02 1" solimp="0.95 0.95 0.001"/>
        </equality>
        <contact>
            <exclude body1="{prefix}B_first" body2="mocap-handle"/>
            <exclude body1="{prefix}B_first" body2="slider-anchor"/>
            <exclude body1="{prefix}B_1" body2="mocap-handle"/>
            <exclude body1="{prefix}B_1" body2="slider-anchor"/>
            <exclude body1="{prefix}B_3" body2="slider-anchor-2"/>
            <exclude body1="{prefix}B_4" body2="slider-anchor-2"/>
            <exclude body1="hook-sphere" body2="{prefix}B_last"/>
            <exclude body1="hook-sphere" body2="{prefix}B_22"/>
            <exclude body1="hook-sphere" body2="{prefix}B_21"/>
        </contact>
        <actuator>
           <!--<adhesion name="magnetic-hook" body="hook-sphere" ctrlrange="0.4 0.41" gain="1"/>-->
           <adhesion name="fish-1-mag" body="fish-1-magnet" ctrlrange="0.15 0.16" gain="1"/>
           <adhesion name="fish-2-mag" body="fish-2-magnet" ctrlrange="0.15 0.16" gain="1"/>
           <adhesion name="fish-3-mag" body="fish-3-magnet" ctrlrange="0.15 0.16" gain="1"/>
        </actuator>
        """,
        )

        fishing_rod = Raw("""
    <body name="mocap-handle" mocap="true" pos="-0.15 0 1.1">
      <site name="mocap-site" size="0.002" />
      <body name="slider-anchor" pos="0.15 0 0">
        <geom type="capsule" pos="-0.075 0 0" size=".002 0.075 0.002" rgba="1 0 0 1" quat="1 0 1 0" />
      </body>
      <body name="slider-anchor-2" pos="0.165 0 0">
        <site name="slider_body_2-site" size="0.002" />
      </body>
    </body>
    """)
        hook_sphere = Raw("""
    <body name="hook-sphere" pos="0.24 0 1.1">
        <joint type="free"/>
        <geom type="sphere" size=".01" rgba="1 0 0 1" margin=".001" gap=".001" mass="0.020"/>
    </body>
    """)
        abc_box = MjSDF(
            mass="0.200",
            scale="1.5 1.9 1.5",
            assets="objects/fishing_toy/abc_box",
            texture="light_wood_texture.png",
            model="model_small.obj",
            geom_quat="0 0 1 1",
            attributes=dict(name="abc-box", pos="0.2 0.07 0.8"),
        )

        def get_magnet(name, size=0.002):
            return Raw(
                f'\n            <body name="{name}-magnet" pos="0 0 0.042">\n            <geom type="sphere" pos="0 0 0" size="{size}" rgba="0.6 0.7 0.5 1" quat="1 0 0 0" mass="0.001"/>\n            </body>\n            '
            )

        fish = MjSDF(
            get_magnet("fish-1"),
            mass="0.010",
            scale="1.5 1.5 1.5",
            assets="objects/fishing_toy/red_fish",
            texture="red_fish.png",
            geom_quat="0 0 1 1",
            attributes=dict(name="fish-1", pos="0.15 -0.1 0.8"),
        )
        fish_2 = MjSDF(
            get_magnet("fish-2"),
            mass="0.010",
            scale="1.5 1.5 1.5",
            assets="objects/fishing_toy/red_fish",
            texture="teal_fish.png",
            geom_quat="0 0 1 1",
            attributes=dict(name="fish-2", pos="0.2 -0.1 0.8"),
        )
        fish_3 = MjSDF(
            get_magnet("fish-3"),
            mass="0.010",
            scale="1.5 1.5 1.5",
            assets="objects/fishing_toy/red_fish",
            texture="orange_fish.png",
            geom_quat="0 0 1 1",
            attributes=dict(name="fish-3", pos="0.25 -0.1 0.8"),
        )
        children = [
            light_rig.key,
            light_rig.back,
            light_rig.fill,
            *camera_rig.get_cameras(),
            workspace.surface,
            rope,
            fishing_rod,
            hook_sphere,
            abc_box,
            fish,
            fish_2,
            fish_3,
        ]
        if mode == "demo":
            pass
        elif mode == "cameraready":
            children += [workspace.table]
        if show_robot:
            children.append(panda)
        scene = Mjcf(
            *children,
            dual_gripper=dual_gripper,
            assets="assets",
            pos=[0, 0, 0.8],
            **options,
            preamble="""
        <compiler angle="radian" autolimits="true" assetdir="{assets}" meshdir="{assets}" texturedir="{assets}"/>

        <visual>
          <headlight diffuse="0.6 0.6 0.6" ambient="0.3 0.3 0.3" specular="0 0 0"/>
          <rgba haze="0.15 0.25 0.35 1"/>
          <global azimuth="150" elevation="-20" offwidth="1280" offheight="1024"/>
        </visual>

        <asset>
          <texture type="skybox" builtin="gradient" rgb1="0.9 0.7 0.9" rgb2="0.94 0.97 0.97"  width="512" height="3072"/>
          <texture type="2d" name="groundplane" builtin="checker" mark="edge" rgb1="0.2 0.3 0.4" rgb2="0.1 0.2 0.3"
            markrgb="0.8 0.8 0.8" width="300" height="300"/>
          <material name="groundplane" texture="groundplane" texuniform="true" texrepeat="5 5" reflectance="0.2"/>
        </asset>
        """,
        )
        return scene

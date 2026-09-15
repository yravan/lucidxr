"""Particle pour: composed from the shared XML schema library."""

from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema.adapters.robohive.robohive_object import RobohiveObj
from lucidxr.sim.xml_schema.objects.vuer_mug import VuerMug
from lucidxr.sim.xml_schema.scene_components.cameras.rig_hand import make_camera_rig
from lucidxr.sim.xml_schema.scene_components.lighting import LightingRig
from lucidxr.sim.xml_schema.scene_components.robots.floating_hands import FloatingShadowHand
from lucidxr.sim.xml_schema.scene_components.settings import WorldSettings
from lucidxr.sim.xml_schema.schema import Body, Mjcf, Replicate


class ParticlePour(Scene):
    def build(self) -> Mjcf:
        asset_directory = self.assets
        robohive_table = RobohiveObj(
            otype="furniture",
            asset_key="simpleTable/simpleWoodTable",
            pos=[0, 0, 0],
            quat=[0.7071, 0, 0, 0.7071],
            local_robohive_root=asset_directory / "adapters/robohive" if asset_directory else None,
        )
        robohive_table_2 = RobohiveObj(
            otype="furniture",
            asset_key="simpleTable/simpleWoodTable",
            name="robohive_table_2",
            pos=[0.75, 0, 0],
            quat=[0.7071, 0, 0, 0.7071],
            local_robohive_root=asset_directory / "adapters/robohive" if asset_directory else None,
        )
        particles = Replicate(
            Replicate(
                Replicate(
                    Body(
                        name="particle",
                        pos=[0.295, 0.195, 0.85],
                        _children_raw="""
                                    <freejoint/>
                                    <geom size=".008" mass="0.001" rgba=".8 .2 .1 1" condim="1"/>
                                """,
                    ),
                    _attributes=dict(count=2, offset="0.0 0.0 0.01"),
                ),
                _attributes=dict(count=2, offset="0.0 0.01 0.0"),
            ),
            _attributes=dict(count=3, offset="0.01 0.0 0.0"),
        )
        camera_rig = make_camera_rig(pos=[-0.4, 0, 0.77])
        vuer_mug = VuerMug(pos=[0.3, -0.2, 0.8])
        from lucidxr.sim.xml_schema.objects.cup import Cup

        cup = Cup(
            assets="rooms/kitchen/cup",
            pos=[0.3, 0.2, 0.8],
            name="cup",
            collision_count=32,
            randomize_colors=False,
        )
        scene = Mjcf(
            WorldSettings("pastel"),
            LightingRig([-0.4, 0, 0.77]),
            vuer_mug,
            cup,
            particles,
            robohive_table,
            robohive_table_2,
            *camera_rig.get_cameras(),
            FloatingShadowHand(bimanual=False, camera_rig=camera_rig, pos=[-0.4, 0, 0.77]),
        )
        return scene

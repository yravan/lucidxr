from vuer_mujoco import Mjcf
from vuer_mujoco import AbilityHandLeft, AbilityHandRight
from vuer_mujoco.schemas.components.rigs.camera_rig import make_camera_rig
from vuer_mujoco.schemas.components.rigs.lighting_rig import make_lighting_rig


class FloatingAbilityHand(Mjcf):
    _attributes = {
        "model": "ability hand setup",
    }

    _preamble = """
    <compiler angle="radian" autolimits="true" assetdir="{assets}" meshdir="{assets}" texturedir="{assets}"/>

    <visual>
      <headlight diffuse="0.6 0.6 0.6" ambient="0.3 0.3 0.3" specular="0 0 0"/>
      <rgba haze="0.15 0.25 0.35 1"/>
      <global azimuth="150" elevation="-20" offwidth="1280" offheight="1024"/>
    </visual>

    <asset>
      <texture type="skybox" builtin="gradient" rgb1="0.3 0.5 0.7" rgb2="0 0 0" width="512" height="3072"/>
      <texture type="2d" name="groundplane" builtin="checker" mark="edge" rgb1="0.2 0.3 0.4" rgb2="0.1 0.2 0.3"
        markrgb="0.8 0.8 0.8" width="300" height="300"/>
      <material name="groundplane" texture="groundplane" texuniform="true" texrepeat="5 5" reflectance="0.2"/>
    </asset>
    """

    # _children_raw = """
    # <geom type="plane" size="1 1 .01" pos="0 0 1.21" rgba="1 1 1 1"/>
    # """

    def __init__(self, *_children, assets="assets", **kwargs):
        super().__init__(*_children, assets=assets, **kwargs)

        camera_rig = make_camera_rig(self._pos)
        light_rig = make_lighting_rig(self._pos)

        hand1 = AbilityHandLeft(
            assets="ability_hand",
            attributes={"name": "ability_hand_left"},
            # set this to a small number to avoid unreasonable forces.
            pos=self._pos + [0, 0, 0.3],
            # wrist_mount=camera_rig.wrist_camera,
        )

        hand2 = AbilityHandRight(
            assets="ability_hand",
            attributes={"name": "ability_hand_right"},
            # set this to a small number to avoid unreasonable forces.
            pos=self._pos + [0.3, 0, 0.3],
            # wrist_mount=camera_rig.wrist_camera,
        )

        self._children = (
            camera_rig.front_camera,
            camera_rig.top_camera,
            camera_rig.left_camera,
            camera_rig.right_camera,
            light_rig.key,
            light_rig.fill,
            light_rig.back,
            *self._children,
            hand1,
            hand2,
            # now add the mocap points.
            hand1._mocaps,
            hand2._mocaps,
        )

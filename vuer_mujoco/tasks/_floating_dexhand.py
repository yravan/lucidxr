from vuer_mujoco.schemas.robots.dexhand import DexHandRight, DexHandLeft
from vuer_mujoco.schemas.schema import Mjcf
from vuer_mujoco.schemas.components.rigs.camera_rig import make_camera_rig
from vuer_mujoco.schemas.components.rigs.lighting_rig import make_lighting_rig


class FloatingDexHand(Mjcf):
    _attributes = {
        "model": "xhand setup",
    }

    _preamble = """
    <compiler angle="radian" autolimits="true" assetdir="{assets}" meshdir="{assets}" texturedir="{assets}"/>
    <option iterations="200" tolerance="1e-10" solver="Newton" integrator="implicit"/>
    <size njmax="1000" nconmax="1000"/>
    <visual>
      <headlight diffuse="0.6 0.6 0.6" ambient="0.3 0.3 0.3" specular="0 0 0"/>
      <rgba haze="0.15 0.25 0.35 1"/>
      <global offwidth="1920" offheight="1080"/>
    </visual>
    <default>
      <joint damping="0.1"/>
      <geom condim="6" solref="0.001 1.0" solimp="0.95 0.9999 0.0005" friction="5. 2. 2."/>
    </default>
    <asset>
      <texture type="skybox" builtin="gradient" rgb1="0.9 0.7 0.9" rgb2="0.94 0.97 0.97"  width="512" height="3072"/>
      <texture type="2d" name="groundplane" builtin="checker" mark="edge" rgb1="0.2 0.3 0.4" rgb2="0.1 0.2 0.3"
        markrgb="0.8 0.8 0.8" width="300" height="300"/>
      <material name="groundplane" texture="groundplane" texuniform="true" texrepeat="5 5" reflectance="0.2"/>
    </asset>
    """

    # _children_raw = """
    # <geom type="plane" size="1 1 .01" pos="0 0 1.21" rgba="1 1 1 1"/>
    # """

    def __init__(self, *_children, assets="assets", bimanual=True, camera_rig=None, **kwargs):
        super().__init__(*_children, assets=assets, **kwargs)
        if camera_rig is None:
            camera_rig = make_camera_rig(self._pos)
        light_rig = make_lighting_rig(self._pos)

        hand1 = DexHandRight(
            show_mocap=True,
            assets="dex_hand_right",
            attributes={"name": "dex_hand_right"},
            # set this to a small number to avoid unreasonable forces.
            pos=self._pos + [0, 0.15, 0.3],
            wrist_mount=camera_rig.wrist_camera(name="wrist"),
        )
        hands = [hand1]
        hand_mocaps = [hand1._mocaps]

        if bimanual:
            hand2 = DexHandLeft(
                show_mocap=False,
                assets="dex_hand_left",
                attributes={"name": "dex_hand_left"},
                # set this to a small number to avoid unreasonable forces.
                pos=self._pos + [0, -0.15, 0.3],
                wrist_mount=camera_rig.wrist_camera(name="wrist"),
            )
            hands.append(hand2)
            hand_mocaps.append(hand2._mocaps)

        self._children = (
            light_rig.key,
            light_rig.fill,
            light_rig.back,
            *self._children,
            *hands,
            # now add the mocap points.
            *hand_mocaps,
        )

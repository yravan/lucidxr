"""Shared MJCF presentation fragments for the assembly presets."""

from lucidxr.sim.xml_schema.schema import Group

PASTEL_PRESENTATION = """
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
    """

DARK_SKY_PRESENTATION = """
    <compiler angle="radian" autolimits="true" assetdir="{assets}" meshdir="{assets}" texturedir="{assets}"/>
    <!--<statistic center="0.2 0 0.4" extent=".65"/>-->

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

DEXTEROUS_SETTINGS = '\n    <compiler angle="radian" autolimits="true" assetdir="{assets}" meshdir="{assets}" texturedir="{assets}"/>\n    <option iterations="200" tolerance="1e-10" solver="Newton" integrator="implicit"/>\n    <size njmax="1000" nconmax="1000"/>\n    <visual>\n      <headlight diffuse="0.6 0.6 0.6" ambient="0.3 0.3 0.3" specular="0 0 0"/>\n      <rgba haze="0.15 0.25 0.35 1"/>\n      <global offwidth="1920" offheight="1080"/>\n    </visual>\n    <default>\n      <joint damping="0.1"/>\n      <geom condim="6" solref="0.001 1.0" solimp="0.95 0.9999 0.0005" friction="5. 2. 2."/>\n    </default>\n    <asset>\n      <texture type="skybox" builtin="gradient" rgb1="0.9 0.7 0.9" rgb2="0.94 0.97 0.97"  width="512" height="3072"/>\n      <texture type="2d" name="groundplane" builtin="checker" mark="edge" rgb1="0.2 0.3 0.4" rgb2="0.1 0.2 0.3"\n        markrgb="0.8 0.8 0.8" width="300" height="300"/>\n      <material name="groundplane" texture="groundplane" texuniform="true" texrepeat="5 5" reflectance="0.2"/>\n    </asset>\n    '


class WorldSettings(Group):
    """Explicit rendering/compiler defaults selected at the task boundary."""

    def __init__(self, preset="pastel"):
        presets = {
            "pastel": PASTEL_PRESENTATION,
            "dark": DARK_SKY_PRESENTATION,
            "dexterous": DEXTEROUS_SETTINGS,
        }
        try:
            preamble = presets[preset]
        except KeyError:
            raise ValueError(f"Unknown world preset: {preset!r}") from None
        super().__init__(assets=".", preamble=preamble)

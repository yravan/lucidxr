from lucidxr.sim.xml_schema.schema import Group


class StagingLayout(Group):
    _attributes = {"model": "lucid-xr staging scene"}

    _preamble = """
    <compiler angle="radian" autolimits="true"/>
    <statistic center="0.2 0 0.4" extent=".65"/>

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

    template = """
    
      
      
        <light pos="0 0 1.5" dir="0 0 -1" directional="true"/>
        <geom name="floor" size="0 0 0.05" type="plane" material="groundplane"/>
        
        <!-- Camera definitions copied from robocasa.  -->
        <camera name="robotO_robotview" pos="1 0 0.4" quat="0.653098 0.271041 0.271041 0.653098"/>
        
        <camera name="robotO_agentview_center" pos="-0.6 0 1.15" quat="0.636946 0.332519 -0.319924 -0.61756"/>

        <camera name="robotO_agentview_left" pos="-0.5 0.35 1.05" quat="0.556238 0.299353 -0.376787 -0.677509" fovy="60"/>

        <camera name="robotO_agentview_right" pos="-0.5 -0.35 1.05" quat="0.677509 0.376787 -0.299353 -0.556239" fovy="60"/>

        <camera name="robotO_frontview" pos="-0.5 0 0.95" quat="0.608894 0.381468 -0.367391 -0.590555" fovy="60"/>

        <camera name="robotO_eye_in_hand" pos="0.05 0 0" quat="0 0.707107 0.707107 0" fovy="75"/>
        
        
        {children}
      
      
    
    """

from lucidxr.sim.xml_schema.schema import Body


class AbilityHandRight(Body):
    assets: str = "robots/ability_hand"

    _attributes = {
        "name": "ability_hand-right",
        # "childclass": "ability_hand",
        "pos": "0 0 0",
        "quat": "1 0 0 0",
    }

    _mocaps_raw = """
        <body mocap="true" name="right-wrist" 
              pos="{pos_wrist}" 
              quat="0.707107 0.707107 0 0">
          <site pos="0 0 0" name="right-wrist-site" rgba="0.658 0.411 0.75 1" size="0.002 0.002 0.002" group="5"/>
        </body>

        <body mocap="true" name="right-index-finger-tip"
              pos="{pos_index}"
              quat="0.707107 0.707107 0 0">
          <site pos="0 0 0" name="right-index-finger-tip-site" rgba="0.658 0.411 0.75 1" size="0.002 0.002 0.002" group="5"/>
        </body>

        <body mocap="true" name="right-middle-finger-tip"
              pos="{pos_middle}"
              quat="0.707107 0.707107 0 0">
          <site pos="0 0 0" name="right-middle-finger-tip-site" rgba="0.658 0.411 0.75 1" size="0.002 0.002 0.002" group="5"/>
        </body>

        <body mocap="true" name="right-ring-finger-tip"
              pos="{pos_ring}"
              quat="0.707107 0.707107 0 0">
          <site pos="0 0 0" name="right-ring-finger-tip-site" rgba="0.658 0.411 0.75 1" size="0.002 0.002 0.002" group="5"/>
        </body>

        <body mocap="true" name="right-pinky-finger-tip"
              pos="{pos_pinky}"
              quat="0.707107 0.707107 0 0">
          <site name="right-pinky-finger-tip-site" rgba="0.658 0.411 0.75 1" size="0.002 0.002 0.002" group="5"/>
        </body>

        <body mocap="true" name="right-thumb-tip"
              pos="{pos_thumb}"
              quat="0.20674 0.67621 -0.67621 -0.20674">
          <site name="right-thumb-tip-site" rgba="0.658 0.411 0.75 1" size="0.002 0.002 0.002" group="5"/>
        </body>
    """

    def __init__(self, *_children, **kwargs):
        super().__init__(*_children, **kwargs)

        self.pos_wrist = self._pos
        self.pos_index = self._pos + [-0.033, -0.0375, 0.172]
        self.pos_middle = self._pos + [-0.009, -0.04, 0.174]
        self.pos_ring = self._pos + [0.016, -0.0385, 0.172]
        self.pos_pinky = self._pos + [0.0365, -0.0355, 0.166]
        self.pos_thumb = self._pos + [-0.115, -0.003, 0.081]

        values = self._format_dict()
        self._mocaps = self._mocaps_raw.format(**values)

    _preamble = """
      <option impratio="20" cone="elliptic" density="0.2" viscosity="0.0002" timestep="0.002"/>
    
      <default>
        <default class="proximal">
          <joint damping="0.1" range="0 2.5" armature="0.001" frictionloss="0.001" actuatorfrcrange="-40 40"/>
          <position kp="1.2" ctrlrange="-0.5 2.5" forcerange="-40 40"/>
          <geom group="4"/>
        </default>
    
        <default class="distal">
          <joint axis="1 0 0" range="0 2.5" damping="0.1" armature="0.001" frictionloss="0.001" actuatorfrcrange="-10 10"/>
          <position kp="1.2" ctrlrange="0.61 2.5" forcerange="-10 10"/>
          <geom group="4"/>
        </default>
    
        <default class="thumb-proximal">
          <joint damping="0.1" armature="0.001" frictionloss="0.001" actuatorfrcrange="-10 10"/>
          <position kp="1.2" ctrlrange="0 2" forcerange="-10 10" gear="-1"/>
          <geom group="4"/>
        </default>
    
        <default class="thumb">
          <joint damping="0.1" armature="0.001" frictionloss="0.001" actuatorfrcrange="-10 10"/>
          <position kp="1.2" ctrlrange="0 6" forcerange="-10 10"/>
          <geom group="4"/>
        </default>
    
        <default class="collision">
          <geom group="4"/>
        </default>
    
        <default class="collision-ball">
          <geom type="sphere" density="1.2" contype="1" conaffinity="1" group="4"/>
        </default>
    
        <default class="collision-box">
          <geom type="box" density="0.001" contype="1" conaffinity="1" group="4"/>
        </default>
    
        <default class="plastic">
          <geom type="mesh" contype="0" conaffinity="0" group="0" density="0.001"/>
        </default>
    
        <default class="rubber">
          <geom type="mesh" contype="0" conaffinity="0" group="0" rgba="0.2 0.2 0.2 1" density="0.001"/>
        </default>
      </default>
    
      <asset>
        <mesh class="plastic" name="wristmesh" file="{assets}/wristmesh.obj"/>
        <mesh class="plastic" name="wristmesh_C" file="{assets}/wristmesh_C.obj"/>
        <mesh class="plastic" name="FB_palm_ref_MIR" file="{assets}/FB_palm_ref_MIR.obj"/>
        <mesh class="rubber" name="idx-F1" file="{assets}/idx-F1.obj"/>
        <mesh class="rubber" name="idx-F2" file="{assets}/idx-F2.obj"/>
        <mesh class="rubber" name="idx-F2_C" file="{assets}/idx-F2_C.obj"/>
        <mesh class="rubber" name="thumb-F1-MIR" file="{assets}/thumb-F1-MIR.obj"/>
        <mesh class="rubber" name="thumb-F1-MIR_C" file="{assets}/thumb-F1-MIR_C.obj"/>
        <mesh class="rubber" name="thumb-F2" file="{assets}/thumb-F2.obj"/>
        <mesh class="rubber" name="thumb-F2_C" file="{assets}/thumb-F2_C.obj"/>
      </asset>
    """

    _children_raw = """
    <joint type="free"/>
      <site name="right_wrist_site" size="0.002" pos="0 0 0" quat="0.707107 0.707107 0 0" rgba="0.5 0.5 0.5 1"/>
      <geom name="wrist_mesh_right" type="mesh" contype="0" conaffinity="0" group="1" density="0" mesh="wristmesh"/>
      <geom class="collision" type="mesh" mesh="wristmesh_C"/>
      <geom name="palm_mesh" class="rubber" pos="-0.0240477 0.00378125 0.0323296" quat="0.0442297 0.00061027 -0.999021 -2.70192e-05" type="mesh"
            contype="0" conaffinity="0" group="1" density="0" mesh="FB_palm_ref_MIR"/>
      <geom pos="-0.0240477 0.00378125 0.0323296" quat="0.0442297 0.00061027 -0.999021 -2.70192e-05" type="mesh" mesh="FB_palm_ref_MIR"/>


      <body name="index_L1" pos="-0.0279216 -0.00927034 0.0958706" quat="0.685906 0.0469401 -0.714459 -0.129917">
        <joint name="right-index_q1" class="proximal" pos="0 0 0" axis="0 0 1"/>
        <geom name="index_mesh_1" class="rubber" pos="0.0384727 0.0032577 0" quat="0.999108 0 0 0.0422244" type="mesh"
              mesh="idx-F1"/>
        <geom class="collision-ball" size="0.0085" pos="0.036 -0.00175 0"/>
        <geom class="collision-box" size="0.005 0.009 0.006" pos="0.023 0 0" quat="0.999108 0 0 0.0422374" type="box"/>
        <body name="index_L2" pos="0.0384727 0.0032577 0" quat="0.999108 0 0 0.0422244">
          <joint name="right-index_q2" class="distal" pos="0 0 0" axis="0 0 1" range="0 2.6586" actuatorfrcrange="-6 6" frictionloss="0.001"/>
          <geom name="index_mesh_2" class="rubber" pos="0.0091241 0 0" quat="1 0 0 0" type="mesh" contype="0" conaffinity="0" group="1" density="0"
                mesh="idx-F2"/>
          <geom class="collision" type="mesh" mesh="idx-F2_C"/>
          <geom class="collision" size="0.006" pos="0.03 -0.016 0"/>
            <site name="index_L2_right_site" size="0.002" group="4" pos="0.04 -0.016 0" quat="0.5 0.5 0.5 -0.5"/>
        </body>
      </body>

      <body name="middle_L1" pos="-0.00841718 -0.0115172 0.0990634" quat="0.704562 0.0715738 -0.698395 -0.103508">
        <joint name="right-middle_q1" class="proximal" pos="0 0 0" axis="0 0 1" range="0 2.0944" actuatorfrcrange="-6 6" frictionloss="0.001"/>
        <geom name="middle_mesh_1" class="rubber" pos="0.0384727 0.0032577 0" quat="0.999108 0 0 0.0422244" type="mesh"
              mesh="idx-F1"/>
        <geom class="collision-ball" size="0.0085" pos="0.036 -0.00175 0"/>
        <geom class="collision-box" size="0.005 0.009 0.006" pos="0.023 0 0" quat="0.999108 0 0 0.0422374" type="box"/>
        <body name="middle_L2" pos="0.0384727 0.0032577 0" quat="0.999108 0 0 0.0422244">
          <joint name="right-middle_q2" class="distal" pos="0 0 0" axis="0 0 1" range="0 2.6586" actuatorfrcrange="-6 6" frictionloss="0.001"/>
          <geom name="middle_mesh_2" class="rubber" pos="0.0091241 0 0" quat="1 0 0 0" type="mesh" contype="0" conaffinity="0" group="1" density="0"
                mesh="idx-F2"/>
          <geom type="mesh" class="collision" mesh="idx-F2_C"/>
          <geom class="collision" size="0.006" pos="0.03 -0.016 0"/>
          <body pos="0.04 -0.016 0" quat="0.5 0.5 0.5 -0.5">
            <site name="middle_L2_right_site" size="0.002" group="4"/>

<!--            <site pos="0 0 0.075" size="0.003 0.003 0.1" type="box" name="site1" rgba="0 0 1 1"/>-->
<!--            <site pos="0 0.075 0" size="0.003 0.1 0.003" type="box" name="site2" rgba="0 1 0 1"/>-->
<!--            <site pos="0.075 0 0" size="0.1 0.003 0.003" type="box" name="site3" rgba="1 0 0 1"/>-->
          </body>
        </body>
      </body>
      <body name="ring_L1" pos="0.0117529 -0.0103946 0.0967038" quat="0.721351 0.0986547 -0.681173 -0.0769649">
        <joint name="right-ring_q1" class="proximal" pos="0 0 0" axis="0 0 1" range="0 2.0944" actuatorfrcrange="-6 6"  frictionloss="0.001"/>
        <geom name="ring_mesh_1" class="rubber" pos="0.0384727 0.0032577 0" quat="0.999108 0 0 0.0422244" type="mesh"
              mesh="idx-F1"/>
        <geom class="collision-ball" size="0.0085" pos="0.036 -0.00175 0"/>
        <geom class="collision-box" size="0.005 0.009 0.006" pos="0.023 0 0" quat="0.999108 0 0 0.0422374" type="box"/>
        <body name="ring_L2" pos="0.0384727 0.0032577 0" quat="0.999108 0 0 0.0422244">
          <joint name="right-ring_q2" class="distal" pos="0 0 0" axis="0 0 1" range="0 2.6586" actuatorfrcrange="-6 6" frictionloss="0.001"/>
          <geom name="ring_mesh_2" class="rubber" pos="0.0091241 0 0" quat="1 0 0 0" type="mesh" contype="0" conaffinity="0" group="1" density="0"
                mesh="idx-F2"/>
          <geom class="collision" type="mesh" mesh="idx-F2_C"/>
          <geom class="collision" size="0.006" pos="0.03 -0.016 0"/>
           <site name="ring_L2_right_site" size="0.002" group="4" pos="0.04 -0.016 0" quat="0.5 0.5 0.5 -0.5"/>
        </body>
      </body>
      <body name="pinky_L1" pos="0.0308633 -0.00716283 0.0907346" quat="0.719226 0.122363 -0.681748 -0.0544096">
        <joint name="right-pinky_q1" class="proximal" pos="0 0 0" axis="0 0 1" range="0 2.0944" actuatorfrcrange="-6 6" frictionloss="0.001"/>
        <geom name="pinky_mesh_1" class="rubber" pos="0.0384727 0.0032577 0" quat="0.999108 0 0 0.0422244" type="mesh"
              mesh="idx-F1"/>
        <geom class="collision-ball" size="0.0085" pos="0.036 -0.00175 0"/>
        <geom class="collision-box" size="0.005 0.009 0.006" pos="0.023 0 0" quat="0.999108 0 0 0.0422374" type="box"/>

        <body name="pinky_L2" pos="0.0384727 0.0032577 0" quat="0.999108 0 0 0.0422244">
          <joint name="right-pinky_q2" class="distal" pos="0 0 0" axis="0 0 1" range="0 2.6586" actuatorfrcrange="-6 6" frictionloss="0.001"/>
          <geom name="pinky_mesh_2" class="rubber" pos="0.0091241 0 0" quat="1 0 0 0" type="mesh" contype="0" conaffinity="0" group="1" density="0"
                mesh="idx-F2"/>
          <geom class="collision" type="mesh" mesh="idx-F2_C"/>
          <geom class="collision" size="0.006" pos="0.03 -0.016 0"/>
          <site name="pinky_L2_right_site" size="0.002" group="4" pos="0.04 -0.016 0" quat="0.5 0.5 0.5 -0.5"/>
        </body>
      </body>

      <body name="thumb_L1" pos="-0.0240477 0.00378125 0.0323296" quat="-0.0947972 0.0440301 -0.00419696 0.994514">
        <joint name="right-thumb_q1" class="thumb-proximal" pos="0 0 0" axis="0 0 1" range="-2.0944 0" actuatorfrcrange="-1.2 1.2" frictionloss="0.001"/>
        <geom name="thumb_mesh_1" class="plastic" pos="0.0278284 0 0.0147507" quat="0.608761 0.793353 0 0" type="mesh" contype="0" conaffinity="0" group="1"
              density="0" mesh="thumb-F1-MIR"/>
        <geom class="collision" pos="0.0278284 0 0.0147507" quat="0.608761 0.793353 0 0" type="mesh" mesh="thumb-F1-MIR_C"/>
        <body name="thumb_L2" pos="0.0278284 0 0.0147507" quat="0.608761 0.793353 0 0">
          <inertial pos="0.0300205 0.00559476 -0.00415044" quat="0.00721249 0.656735 -0.223684 0.720148" mass="0.0055"
                    diaginertia="0.00180207 0.00170892 0.000287855"/>
          <joint name="right-thumb_q2" class="thumb" pos="0 0 0" axis="0 0 1" range="0 2.0944" actuatorfrcrange="-6 6" frictionloss="0.001"/>
          <geom name="thumb_mesh_2" class="rubber" pos="0.0651867 0.0233402 0.00393483" quat="3.21978e-07 -0.985259 -0.171069 5.59046e-08" type="mesh"
                contype="0" conaffinity="0" group="1" density="0" mesh="thumb-F2"/>
          <geom class="collision" pos="0.0651867 0.0233402 0.00393483" quat="3.21978e-07 -0.985259 -0.171069 5.59046e-08" type="mesh" mesh="thumb-F2_C"/>
          <site name="thumb_L2_right_site" size="0.002" group="4" pos="0.066 0.025 0.005" quat="0.6415 0.2986 0.6415 -0.2986"/>
        </body>
      </body>
    """

    _postamble = """
      <actuator>
        <position name="act_index_q1-right" class="proximal" joint="right-index_q1" />
        <position name="act_index_q2-right" class="distal" joint="right-index_q2"/>
    
        <position name="act_middle_q1-right" class="proximal" joint="right-middle_q1" />
        <position name="act_middle_q2-right" class="distal" joint="right-middle_q2"/>
    
        <position name="act_ring_q1-right" class="proximal" joint="right-ring_q1" />
        <position name="act_ring_q2-right" class="distal" joint="right-ring_q2"/>
    
        <position name="act_pinky_q1-right" class="proximal" joint="right-pinky_q1" />
        <position name="act_pinky_q2-right" class="distal" joint="right-pinky_q2"/>
    
        <position name="act_thumb_q1-right" class="thumb-proximal" joint="right-thumb_q1" />
        <position name="act_thumb_q2-right" class="distal" joint="right-thumb_q2"/>
      </actuator>
    
      <equality>
        <weld site1="right-wrist-site" site2="right_wrist_site"/>
        <weld site1="right-index-finger-tip-site" site2="index_L2_right_site" />
        <weld site1="right-middle-finger-tip-site" site2="middle_L2_right_site" />
        <weld site1="right-ring-finger-tip-site" site2="ring_L2_right_site" />
        <weld site1="right-pinky-finger-tip-site" site2="pinky_L2_right_site" />
        <weld site1="right-thumb-tip-site" site2="thumb_L2_right_site" />
      </equality> 
    """


class AbilityHandLeft(Body):
    """"""

    assets: str = "robots/ability_hand"

    _attributes = {
        "name": "ability_hand-left",
        # "childclass": "ability_hand",
        "pos": "0 0 0",
        "quat": "1 0 0 0",
    }

    _mocaps_raw = """
        <body mocap="true" name="left-wrist" 
              pos="{pos_wrist}" 
              quat="0.7071 0.7071 0 0">
          <site pos="0 0 0" name="left-wrist-site" rgba="0.658 0.411 0.75 1" size="0.002 0.002 0.002"/>
        </body>

        <body mocap="true" name="left-index-finger-tip" 
              pos="{pos_index}" 
              quat="0.7071 0.7071 0 0">
          <site pos="0 0 0" name="left-index-finger-tip-site" rgba="0.658 0.411 0.75 1" size="0.002 0.002 0.002"/>
        </body>

        <body mocap="true" name="left-middle-finger-tip" 
              pos="{pos_middle}" 
              quat="0.7071 0.7071 0 0">
          <site pos="0 0 0" name="left-middle-finger-tip-site" rgba="0.658 0.411 0.75 1" size="0.002 0.002 0.002"/>
        </body>

        <body mocap="true" name="left-ring-finger-tip" 
              pos="{pos_ring}" 
              quat="0.7071 0.7071 0 0">
          <site pos="0 0 0" name="left-ring-finger-tip-site" rgba="0.658 0.411 0.75 1" size="0.002 0.002 0.002"/>
        </body>

        <body mocap="true" name="left-pinky-finger-tip" 
              pos="{pos_pinky}" 
              quat="0.7071 0.7071 0 0">
          <site name="left-pinky-finger-tip-site" rgba="0.658 0.411 0.75 1" size="0.002 0.002 0.002"/>
        </body>

        <body mocap="true" name="left-thumb-tip" 
              pos="{pos_thumb}" 
              quat="0.4330 0.6830 0.6830 0.1830">
          <site name="left-thumb-tip-site" rgba="0.658 0.411 0.75 1" size="0.002 0.002 0.002"/>
        </body>
    """

    def __init__(self, *_children, **kwargs):
        super().__init__(*_children, **kwargs)

        self.pos_wrist = self._pos
        self.pos_index = self._pos + [0.033, -0.036, 0.173]
        self.pos_middle = self._pos + [0.010, -0.039, 0.173]
        self.pos_ring = self._pos + [-0.016, -0.036, 0.171]
        self.pos_pinky = self._pos + [-0.036, -0.0342, 0.164]
        self.pos_thumb = self._pos + [0.118, -0.004, 0.077]

        values = self._format_dict()
        self._mocaps = self._mocaps_raw.format(**values)

    _preamble = """
        <option impratio="20" cone="elliptic" density="0.2" viscosity="0.0002" timestep="0.002"/>
        
        <default>
            <default class="proximal">
              <joint damping="0.1" range="0 2.5" armature="0.001" frictionloss="0.001" actuatorfrcrange="-40 40"/>
              <position kp="1.2" ctrlrange="-0.5 2.5" forcerange="-40 40"/>
              <geom group="4"/>
            </default>
        
            <default class="distal">
              <joint axis="1 0 0" range="0 2.5" damping="0.1" armature="0.001" frictionloss="0.001" actuatorfrcrange="-10 10"/>
              <position kp="1.2" ctrlrange="0.61 2.5" forcerange="-10 10"/>
              <geom group="4"/>
            </default>
        
            <default class="thumb-proximal">
              <joint damping="0.1" armature="0.001" frictionloss="0.001" actuatorfrcrange="-10 10"/>
              <position kp="1.2" ctrlrange="0 2" forcerange="-10 10" gear="-1"/>
              <geom group="4"/>
            </default>
        
            <default class="thumb">
              <joint damping="0.1" armature="0.001" frictionloss="0.001" actuatorfrcrange="-10 10"/>
              <position kp="1.2" ctrlrange="0 6" forcerange="-10 10"/>
              <geom group="4"/>
            </default>
        
            <default class="collision">
              <geom group="4"/>
            </default>
        
            <default class="collision-ball">
              <geom type="sphere" density="1.2" contype="1" conaffinity="1" group="4"/>
            </default>
        
            <default class="collision-box">
              <geom type="box" density="0.001" contype="1" conaffinity="1" group="4"/>
            </default>
        
            <default class="plastic">
              <geom type="mesh" contype="0" conaffinity="0" group="0" density="0.001"/>
            </default>
        
            <default class="rubber">
              <geom type="mesh" contype="0" conaffinity="0" group="0" rgba="0.2 0.2 0.2 1" density="0.001"/>
            </default>
        </default>
        
        <asset>
            <mesh class="plastic" name="wristmesh_left" file="{assets}/wristmesh.obj"/>
            <mesh class="plastic" name="wristmesh_C_left" file="{assets}/wristmesh_C.obj"/>
            <mesh class="plastic" name="FB_palm_ref_left" file="{assets}/FB_palm_ref.obj"/>
            <mesh class="rubber" name="idx-F1_left" file="{assets}/idx-F1.obj"/>
            <mesh class="rubber" name="idx-F2_left" file="{assets}/idx-F2.obj"/>
            <mesh class="rubber" name="idx-F2_C_left" file="{assets}/idx-F2_C.obj"/>
            <mesh class="rubber" name="thumb-F1_left" file="{assets}/thumb-F1.obj"/>
            <mesh class="rubber" name="thumb-F1_C_left" file="{assets}/thumb-F1_C.obj"/>
            <mesh class="rubber" name="thumb-F2_left" file="{assets}/thumb-F2.obj"/>
            <mesh class="rubber" name="thumb-F2_C_left" file="{assets}/thumb-F2_C.obj"/>
            
            <texture type="skybox" builtin="gradient" rgb1="0.3 0.5 0.7" rgb2="0 0 0" width="512" height="3072"/>
            <texture type="2d" name="groundplane" builtin="checker" mark="edge" rgb1="0.2 0.3 0.4" rgb2="0.1 0.2 0.3"
                     markrgb="0.8 0.8 0.8" width="300" height="300"/>
            <material name="groundplane" texture="groundplane" texuniform="true" texrepeat="5 5" reflectance="0.2"/>
        </asset>
    """

    _children_raw = """
          <joint type="free"/>
          <site name="left_wrist_site" pos="0 0 0" quat="0.7071 0.7071 0 0" rgba="0.5 0.5 0.5 1"/>
          <geom name="wrist_mesh_left" type="mesh" contype="0" conaffinity="0" group="1" density="0" mesh="wristmesh_left"/>
          <geom class="collision" type="mesh" mesh="wristmesh_C_left"/>
          <geom name="palm_mesh_left" class="rubber" pos="0.0240477 0.00378125 0.0323296" quat="0.0442297 0.00061027 0.999021 2.70192e-05"
                type="mesh" mesh="FB_palm_ref_left"/>
          <geom pos="0.0240477 0.00378125 0.0323296" quat="0.0442297 0.00061027 0.999021 2.70192e-05" type="mesh" mesh="FB_palm_ref_left"/>
    
          <body name="index_L1_left" pos="0.0279216 -0.00927034 0.0958706" quat="-0.714459 -0.129917 0.685906 0.0469401">
            <joint name="left-index_q1" class="proximal" pos="0 0 0" axis="0 0 1"/>
            <geom name="index_mesh_1_left" class="rubber" pos="0.0384727 0.0032577 0" quat="0.999108 0 0 0.0422244" type="mesh"
                  mesh="idx-F1_left"/>
            <geom class="collision-ball" size="0.0085" pos="0.036 -0.00175 0"/>
            <geom class="collision-box" size="0.005 0.009 0.006" pos="0.023 0 0" quat="0.999108 0 0 0.0422374" type="box"/>
            <body name="index_L2_left" pos="0.0384727 0.0032577 0" quat="0.999108 0 0 0.0422244">
              <joint name="left-index_q2" class="distal" pos="0 0 0" axis="0 0 1" range="-6.223 2.6586"/>
              <geom name="index_mesh_2_left" class="rubber" pos="0.0091241 0 0" quat="1 0 0 0" type="mesh" mesh="idx-F2_left"/>
              <geom class="collision" type="mesh" mesh="idx-F2_C_left"/>
              <geom class="collision" size="0.006" pos="0.03 -0.016 0"/>
              <site name="index_L2_left_site" group="4" size="0.002" pos="0.04 -0.016 0" quat="0.5 0.5 0.5 -0.5"/>
            </body>
          </body>
    
          <body name="middle_L1_left" pos="0.00841718 -0.0115172 0.0990634" quat="-0.698395 -0.103508 0.704562 0.0715738">
            <joint name="left-middle_q1" class="proximal" pos="0 0 0" axis="0 0 1"/>
            <geom name="middle_mesh_1_left" class="rubber" pos="0.0384727 0.0032577 0" quat="0.999108 0 0 0.0422244" type="mesh"
                  mesh="idx-F1_left"/>
            <geom class="collision-ball" size="0.0085" pos="0.036 -0.00175 0"/>
            <geom class="collision-box" size="0.005 0.009 0.006" pos="0.023 0 0" quat="0.999108 0 0 0.0422374" type="box"/>
    
            <body name="middle_L2_left" pos="0.0384727 0.0032577 0" quat="0.999108 0 0 0.0422244">
              <joint name="left-middle_q2" class="distal" pos="0 0 0" axis="0 0 1" range="-6.223 2.6586"/>
              <geom name="middle_mesh_2_left" class="rubber" pos="0.0091241 0 0" quat="1 0 0 0" type="mesh" mesh="idx-F2_left"/>
              <geom type="mesh" class="collision" mesh="idx-F2_C_left"/>
              <geom class="collision" size="0.006" pos="0.03 -0.016 0"/>
              <site name="middle_L2_left_site" group="4" size="0.002" pos="0.04 -0.016 0" quat="0.5 0.5 0.5 -0.5"/>
            </body>
          </body>
    
          <body name="ring_L1_left" pos="-0.0117529 -0.0103946 0.0967038" quat="-0.681173 -0.0769649 0.721351 0.0986547">
            <joint name="left-ring_q1" class="proximal" pos="0 0 0" axis="0 0 1"/>
            <geom name="ring_mesh_1_left" class="rubber" pos="0.0384727 0.0032577 0" quat="0.999108 0 0 0.0422244" type="mesh"
                  mesh="idx-F1_left"/>
            <geom class="collision-ball" size="0.0085" pos="0.036 -0.00175 0"/>
            <geom class="collision-box" size="0.005 0.009 0.006" pos="0.023 0 0" quat="0.999108 0 0 0.0422374" type="box"/>
            <body name="ring_L2_left" pos="0.0384727 0.0032577 0" quat="0.999108 0 0 0.0422244">
              <joint name="left-ring_q2" class="distal" pos="0 0 0" axis="0 0 1" range="-6.223 2.6586"/>
              <geom name="ring_mesh_2_left" class="rubber" pos="0.0091241 0 0" quat="1 0 0 0" type="mesh" mesh="idx-F2_left"/>
              <geom type="mesh" class="collision" mesh="idx-F2_C_left"/>
              <geom class="collision" size="0.006" pos="0.03 -0.016 0"/>
              <site name="ring_L2_left_site" group="4" size="0.002" pos="0.04 -0.016 0" quat="0.5 0.5 0.5 -0.5"/>
            </body>
          </body>
    
          <body name="pinky_L1_left" pos="-0.0308633 -0.00716283 0.0907346" quat="-0.681748 -0.0544096 0.719226 0.122363">
            <joint name="left-pinky_q1" class="proximal" pos="0 0 0" axis="0 0 1"/>
            <geom name="pinky_mesh_1_left" class="rubber" pos="0.0384727 0.0032577 0" quat="0.999108 0 0 0.0422244" type="mesh"
                  mesh="idx-F1_left"/>
            <geom class="collision-ball" size="0.0085" pos="0.036 -0.00175 0"/>
            <geom class="collision-box" size="0.005 0.009 0.006" pos="0.023 0 0" quat="0.999108 0 0 0.0422374" type="box"/>
    
            <body name="pinky_L2_left" pos="0.0384727 0.0032577 0" quat="0.999108 0 0 0.0422244">
              <joint name="left-pinky_q2" class="distal" pos="0 0 0" axis="0 0 1" range="-6.223 2.6586"/>
              <geom name="pinky_mesh_2_left" class="rubber" pos="0.0091241 0 0" quat="1 0 0 0" type="mesh" mesh="idx-F2_left"/>
              <geom type="mesh" class="collision" mesh="idx-F2_C_left"/>
              <geom class="collision" size="0.006" pos="0.03 -0.016 0"/>
              <site name="pinky_L2_left_site" group="4" size="0.002" pos="0.04 -0.016 0" quat="0.5 0.5 0.5 -0.5"/>
            </body>
          </body>
    
          <body name="thumb_L1_left" pos="0.0240477 0.00378125 0.0323296" quat="-0.00419696 0.994514 -0.0947972 0.0440301">
            <joint name="left-thumb_q1" class="thumb-proximal" pos="0 0 0" axis="0 0 1"/>
            <geom name="thumb_mesh_1_left" class="plastic" pos="0.0278284 0 -0.0147507" quat="-0.608761 0.793353 0 0" type="mesh" contype="0"
                  conaffinity="0"
                  group="1" density="0" mesh="thumb-F1_left"/>
            <geom class="collision" pos="0.0278284 0 -0.0147507" quat="-0.608761 0.793353 0 0" type="mesh" mesh="thumb-F1_C_left"/>
            <body name="thumb_L2_left" pos="0.0278284 0 -0.0147507" quat="-0.608761 0.793353 0 0">
              <joint name="left-thumb_q2" class="thumb" pos="0 0 0" axis="0 0 1"/>
              <geom name="thumb_mesh_2_left" class="rubber" pos="0.0651867 0.0233402 -0.00393483"
                    quat="3.21978e-07 0.985259 0.171069 5.59046e-08" type="mesh"
                    mesh="thumb-F2_left"/>
              <geom class="collision" pos="0.0651867 0.0233402 -0.00393483" quat="3.21978e-07 0.985259 0.171069 5.59046e-08" type="mesh" mesh="thumb-F2_C_left"/>
              <site name="thumb_L2_left_site" group="4" size="0.002" pos="0.069 0.024 -0.005" quat="0.6415 0.2986 0.6415 -0.2986"/>
            </body>
          </body>
    
    """

    _postamble = """
    <actuator>
        <position name="act_index_q1-left" class="proximal" joint="left-index_q1"/>
        <position name="act_index_q2-left" class="distal" joint="left-index_q2"/>
    
        <position name="act_middle_q1-left" class="proximal" joint="left-middle_q1"/>
        <position name="act_middle_q2-left" class="distal" joint="left-middle_q2"/>
    
        <position name="act_ring_q1-left" class="proximal" joint="left-ring_q1"/>
        <position name="act_ring_q2-left" class="distal" joint="left-ring_q2"/>
    
        <position name="act_pinky_q1-left" class="proximal" joint="left-pinky_q1"/>
        <position name="act_pinky_q2-left" class="distal" joint="left-pinky_q2"/>
    
        <position name="act_thumb_q1-left" class="thumb-proximal" joint="left-thumb_q1"/>
        <position name="act_thumb_q2-left" class="thumb" joint="left-thumb_q2" ctrlrange="0 2.4"/>
      </actuator>
    
      <equality>
        <weld site1="left-wrist-site" site2="left_wrist_site"/>
        <weld site1="left-index-finger-tip-site" site2="index_L2_left_site"/>
        <weld site1="left-middle-finger-tip-site" site2="middle_L2_left_site"/>
        <weld site1="left-ring-finger-tip-site" site2="ring_L2_left_site"/>
        <weld site1="left-pinky-finger-tip-site" site2="pinky_L2_left_site"/>
        <weld site1="left-thumb-tip-site" site2="thumb_L2_left_site"/>
    </equality>
    """


class AbilityHand(Body):
    pass

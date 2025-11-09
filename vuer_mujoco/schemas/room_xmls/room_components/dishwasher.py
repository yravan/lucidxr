from vuer_mujoco.schemas.schema import Body


class KitchenDishwasher(Body):
    """Template class generated from the original dishwasher MJCF.

    All asset filenames are parameterised so they resolve relative to the
    class-level ``assets`` directory.  Every texture, material, mesh, body,
    geom, joint and site from the XML is preserved verbatim so that no
    fidelity is lost compared with the hand‑written MJCF, while still giving
    you the flexibility to tweak
    * ``assets`` – where the files live on disk;
    * ``prefix``  – a short string that is prepended to *all* MJCF names so
      that multiple dishwashers can co‑exist in a single model without name
      clashes.
    """

    # ------------------------- high‑level configuration -------------------- #

    assets = "dishwasher"  # directory under ``meshdir`` / ``texturedir``
    prefix = "dw"          # change this to avoid name collisions
    mesh_scale = "1.0 1.0 1.0"

    _attributes = {
        "name": "{prefix}-frame",  # overridable name of the root body
        "childclass": "{prefix}",
    }
    
    # --------------------------------------------------------------------- #
    # Everything below this point mirrors the MJCF 1‑for‑1, with *only* the
    # file paths and MJCF names parameterised by ``{assets}`` / ``{prefix}``.
    # --------------------------------------------------------------------- #

    _preamble = f"""
    <asset>
        <!-- textures -->
        <texture type="2d" name="{{prefix}}-basket" file="{{assets}}/basket.png"/>
        <texture type="2d" name="{{prefix}}-body"   file="{{assets}}/body.png"/>
        <texture type="2d" name="{{prefix}}-bottom" file="{{assets}}/bottom.png"/>
        <texture type="2d" name="{{prefix}}-door"   file="{{assets}}/door.png"/>
        <texture type="2d" name="{{prefix}}-middle" file="{{assets}}/middle.png"/>

        <!-- materials -->
        <material name="{{prefix}}-dishwasher" rgba="0.3 0.3 0.3 1"/>
        <material name="{{prefix}}-basket"     texture="{{prefix}}-basket" rgba="0.3 0.3 0.3 1"/>
        <material name="{{prefix}}-body"       texture="{{prefix}}-body"/>
        <material name="{{prefix}}-bottom"     texture="{{prefix}}-bottom"/>
        <material name="{{prefix}}-door"       texture="{{prefix}}-door"/>
        <material name="{{prefix}}-middle"     texture="{{prefix}}-middle"/>

        <!-- meshes – visual -->
        <mesh name="{{prefix}}-dish_washer_body_001"  file="{{assets}}/visual/dish_washer_body_001.obj" scale="{{mesh_scale}}"/>
        <mesh name="{{prefix}}-dish_washer_door_001"  file="{{assets}}/visual/dish_washer_door_001.obj" scale="{{mesh_scale}}"/>
        <mesh name="{{prefix}}-dish_washer_mid_001"   file="{{assets}}/visual/dish_washer_mid_001.obj" scale="{{mesh_scale}}"/>
        <mesh name="{{prefix}}-dish_washer_mid_sprinkle" file="{{assets}}/visual/dish_washer_mid_sprinkle.obj" scale="{{mesh_scale}}"/>
        <mesh name="{{prefix}}-dish_washer_bottom_001" file="{{assets}}/visual/dish_washer_bottom_001.obj" scale="{{mesh_scale}}"/>
        <mesh name="{{prefix}}-dish_washer_bottom_wheel" file="{{assets}}/visual/dish_washer_bottom_wheel.obj" scale="{{mesh_scale}}"/>
        <mesh name="{{prefix}}-dish_washer_bottom_plates_holder_001" file="{{assets}}/visual/dish_washer_bottom_plates_holder_001.obj" scale="{{mesh_scale}}"/>
        <mesh name="{{prefix}}-dish_washer_bottom_cuttlery_basket_001" file="{{assets}}/visual/dish_washer_bottom_cuttlery_basket_001.obj" scale="{{mesh_scale}}"/>

        <!-- meshes – collision (parameterised helper) -->
        {"".join([f'<mesh name="{{prefix}}-collision_door_{idx:03d}" file="{{assets}}/collision/collision_door_{idx:03d}.obj" scale="{{mesh_scale}}"/>' for idx in (1,3,4,6,7,8,9)])}
        {"".join([f'<mesh name="{{prefix}}-collision_tray_mid_{idx:03d}" file="{{assets}}/collision/collision_tray_mid_{idx:03d}.obj" scale="{{mesh_scale}}"/>' for idx in range(1,28)])}
        {"".join([f'<mesh name="{{prefix}}-collision_tray_{idx:03d}" file="{{assets}}/collision/collision_tray_{idx:03d}.obj" scale="{{mesh_scale}}"/>' for idx in range(1,34)])}
        {"".join([f'<mesh name="{{prefix}}-collision_holder_{idx:03d}" file="{{assets}}/collision/collision_holder_{idx:03d}.obj" scale="{{mesh_scale}}"/>' for idx in range(1,15)])}
        {"".join([f'<mesh name="{{prefix}}-collision_dish_washer_mid_sprinkle" file="{{assets}}/collision/collision_dish_washer_mid_sprinkle.obj" scale="{{mesh_scale}}"/>'])}
        {"".join([f'<mesh name="{{prefix}}-collision_dish_washer_bottom_basket_{idx:03d}" file="{{assets}}/collision/collision_dish_washer_bottom_basket_{idx:03d}.obj" scale="{{mesh_scale}}"/>' for idx in range(1,16)])}
    </asset>
    <default>
        <default class="{{prefix}}">
            <default class="{{prefix}}-visual">
                <geom type="mesh" contype="0" conaffinity="0" group="0" mass="0"/>
            </default>
            <default class="{{prefix}}-collision">
                <geom type="mesh" group="3" friction="0.1" solimp="0.998 0.998 0.001" solref="0.004 1" density="1"/>
            </default>
            <default class="{{prefix}}-collision_basket">
                <geom type="mesh" group="3" friction="0.1" solimp="0.998 0.998 0.001" solref="0.004 1" density="1"/>
            </default>
            <default class="{{prefix}}-collision_holder">
                <geom type="mesh" group="3" friction="0.1" solimp="0.998 0.998 0.001" solref="0.004 1" density="1"/>
            </default>
        </default>
    </default>
    """

    # ----------------------------- worldbody ------------------------------ #
    _children_raw = """
    <geom material="{prefix}-body" mesh="{prefix}-dish_washer_body_001" class="{prefix}-visual" euler="1.5708 0 0"/>
      <geom pos="0 -0.258 0.129" size="0.3 0.258 0.129" type="box" class="{prefix}-collision"/>
      <geom pos="0 -0.278 0.269" size="0.3 0.278 0.011" type="box" class="{prefix}-collision"/>
      <geom pos="0.286 -0.278 0.531" size="0.014 0.278 0.274" type="box" class="{prefix}-collision"/>
      <geom pos="-0.286 -0.278 0.531" size="0.014 0.278 0.274" type="box" class="{prefix}-collision"/>
      <geom pos="0 -0.008 0.531" size="0.3 0.008 0.274" type="box" class="{prefix}-collision"/>
      <geom pos="0 -0.278 0.808" size="0.3 0.278 0.0128" type="box" class="{prefix}-collision"/>
      <body name="{prefix}door" pos="0 -0.57 0.245" euler="1.5708 0 0">
        <joint name="{prefix}door_hinge" axis="1 0 0" range="0 1.5708" damping="0.01" solimplimit="0.998 0.998 0.001" solreflimit="0.004 1"/>
        <inertial mass="0.01" pos="0 0 0" quat="1 0 0 0" diaginertia="0.0001 0.0001 0.0001"/>
        <geom material="{prefix}-door" mesh="{prefix}-dish_washer_door_001" class="{prefix}-visual"/>
        <geom pos="0 0.517 0.086" size="0.019 0.28" type="cylinder" class="{prefix}-collision" euler="0 1.5708 0"/>
        <geom pos="0.238 0.517 0.06" size="0.031 0.025 0.014" type="box" class="{prefix}-collision" euler="1.5708 0 0"/>
        <geom pos="-0.238 0.517 0.06" size="0.031 0.025 0.014" type="box" class="{prefix}-collision" euler="1.5708 0 0"/>
        <geom pos="0 0.261 0.03" size="0.295 0.016 0.295" type="box" class="{prefix}-collision" euler="1.5708 0 0"/>
        <geom pos="0 0.546 0.0192" size="0.295 0.02603 0.019" type="box" class="{prefix}-collision" euler="1.5708 0 0"/>
        <geom pos="0 0.0148 0.0192" size="0.295 0.02603 0.0584" type="box" class="{prefix}-collision" euler="1.5708 0 0"/>
        <geom pos="0.275 0.2606 0.0192" size="0.0216 0.02603 0.295" type="box" class="{prefix}-collision" euler="1.5708 0 0"/>
        <geom pos="-0.275 0.2606 0.0192" size="0.0216 0.02603 0.295" type="box" class="{prefix}-collision" euler="1.5708 0 0"/>
        <geom mesh="{prefix}-collision_door_001" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_door_003" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_door_004" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_door_006" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_door_007" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_door_008" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_door_009" class="{prefix}-collision"/>
      </body>
      <body name="{prefix}tray_mid" pos="0 -0.248 0.6" euler="1.5708 0 0">
        <joint name="{prefix}tray_mid_linear" type="slide" axis="0 0 1" range="0 0.45" damping="5" solimplimit="0.998 0.998 0.001" solreflimit="0.004 1"/>
        <geom material="{prefix}-middle" mesh="{prefix}-dish_washer_mid_001" class="{prefix}-visual"/>
        <geom mesh="{prefix}-collision_tray_mid_001" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_mid_002" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_mid_003" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_mid_004" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_mid_005" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_mid_006" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_mid_007" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_mid_008" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_mid_009" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_mid_010" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_mid_011" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_mid_012" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_mid_013" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_mid_014" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_mid_015" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_mid_016" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_mid_017" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_mid_018" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_mid_019" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_mid_020" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_mid_021" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_mid_022" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_mid_023" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_mid_024" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_mid_025" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_mid_026" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_mid_027" class="{prefix}-collision"/>
        <!-- plates holders -->
        <body name="{prefix}dish_washer_mid_holder_1" pos="0.085 0.0025 0" euler="0 1.5708 0">
          <geom material="{prefix}-dishwasher" mesh="{prefix}-dish_washer_bottom_plates_holder_001" class="{prefix}-visual"/>
          <geom mesh="{prefix}-collision_holder_001" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_002" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_003" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_004" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_005" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_006" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_007" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_008" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_009" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_010" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_011" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_012" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_013" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_014" class="{prefix}-collision_holder"/>
        </body>
        <body name="{prefix}dish_washer_mid_holder_2" pos="-0.085 0.0025 0" euler="0 1.5708 0">
          <geom material="{prefix}-dishwasher" mesh="{prefix}-dish_washer_bottom_plates_holder_001" class="{prefix}-visual"/>
          <geom mesh="{prefix}-collision_holder_001" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_002" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_003" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_004" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_005" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_006" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_007" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_008" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_009" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_010" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_011" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_012" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_013" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_014" class="{prefix}-collision_holder"/>

        </body>
        <!-- sprinkler -->
        <body name="{prefix}tray_mid_sprinkler" pos="0 -0.029338 0">
          <joint name="{prefix}tray_mid_sprinkler" axis="0 1 0" limited="false" damping="0.001"/>
          <inertial mass="0.01" pos="0 0 0" quat="1 0 0 0" diaginertia="0.001 0.001 0.001"/>
          <geom material="{prefix}-dishwasher" mesh="{prefix}-dish_washer_mid_sprinkle" class="{prefix}-visual"/>
          <geom mesh="{prefix}-collision_dish_washer_mid_sprinkle" class="{prefix}-collision"/>
        </body>
      </body>
      <body name="{prefix}tray_bottom" pos="0 -0.309 0.35" euler="1.5708 0 0">
        <joint name="{prefix}tray_bottom_linear" type="slide" axis="0 0 1" range="0 0.5" damping="5" solimplimit="0.998 0.998 0.001" solreflimit="0.004 1"/>
        <geom material="{prefix}-bottom" mesh="{prefix}-dish_washer_bottom_001" class="{prefix}-visual"/>
        <geom mesh="{prefix}-collision_tray_001" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_002" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_003" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_004" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_005" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_006" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_007" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_008" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_009" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_010" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_011" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_012" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_013" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_014" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_015" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_016" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_017" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_018" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_019" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_020" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_021" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_022" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_023" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_024" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_025" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_026" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_027" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_028" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_029" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_030" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_031" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_032" class="{prefix}-collision"/>
        <geom mesh="{prefix}-collision_tray_033" class="{prefix}-collision"/>
        <!-- plates holders -->
        <body name="{prefix}dish_washer_bottom_holder_1" pos="-0.047521 -0.048164 0.145" euler="0.523599 0 0">
          <geom material="{prefix}-dishwasher" mesh="{prefix}-dish_washer_bottom_plates_holder_001" class="{prefix}-visual"/>
          <geom mesh="{prefix}-collision_holder_001" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_002" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_003" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_004" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_005" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_006" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_007" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_008" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_009" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_010" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_011" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_012" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_013" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_014" class="{prefix}-collision_holder"/>
        </body>
        <body name="{prefix}dish_washer_bottom_holder_2" pos="-0.047521 -0.048164 0.088794" euler="-0.523599 0 0">
          <geom material="{prefix}-dishwasher" mesh="{prefix}-dish_washer_bottom_plates_holder_001" class="{prefix}-visual"/>
          <geom mesh="{prefix}-collision_holder_001" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_002" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_003" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_004" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_005" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_006" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_007" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_008" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_009" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_010" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_011" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_012" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_013" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_014" class="{prefix}-collision_holder"/>
        </body>
        <body name="{prefix}dish_washer_bottom_holder_3" pos="-0.047521 -0.048164 -0.1133" euler="0.523599 0 0">
          <geom material="{prefix}-dishwasher" mesh="{prefix}-dish_washer_bottom_plates_holder_001" class="{prefix}-visual"/>
          <geom mesh="{prefix}-collision_holder_001" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_002" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_003" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_004" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_005" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_006" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_007" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_008" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_009" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_010" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_011" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_012" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_013" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_014" class="{prefix}-collision_holder"/>
        </body>
        <body name="{prefix}dish_washer_bottom_holder_4" pos="-0.047521 -0.048164 -0.189036" euler="-0.523599 0 0">
          <geom material="{prefix}-dishwasher" mesh="{prefix}-dish_washer_bottom_plates_holder_001" class="{prefix}-visual"/>
          <geom mesh="{prefix}-collision_holder_001" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_002" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_003" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_004" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_005" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_006" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_007" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_008" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_009" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_010" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_011" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_012" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_013" class="{prefix}-collision_holder"/>
          <geom mesh="{prefix}-collision_holder_014" class="{prefix}-collision_holder"/>
        </body>
        <!-- wheels -->
        <body name="{prefix}dish_washer_bottom_wheel_1_l" pos="0.250505 -0.049095 0.139046">
          <geom material="{prefix}-dishwasher" mesh="{prefix}-dish_washer_bottom_wheel" class="{prefix}-visual"/>
          <geom mesh="{prefix}-dish_washer_bottom_wheel" class="{prefix}-collision"/>
        </body>
        <body name="{prefix}dish_washer_bottom_wheel_2_l" pos="0.250505 -0.049095 0.040992">
          <geom material="{prefix}-dishwasher" mesh="{prefix}-dish_washer_bottom_wheel" class="{prefix}-visual"/>
          <geom mesh="{prefix}-dish_washer_bottom_wheel" class="{prefix}-collision"/>
        </body>
        <body name="{prefix}dish_washer_bottom_wheel_3_l" pos="0.250505 -0.049095 -0.087648">
          <geom material="{prefix}-dishwasher" mesh="{prefix}-dish_washer_bottom_wheel" class="{prefix}-visual"/>
          <geom mesh="{prefix}-dish_washer_bottom_wheel" class="{prefix}-collision"/>
        </body>
        <body name="{prefix}dish_washer_bottom_wheel_4_l" pos="0.250505 -0.049095 -0.190549">
          <geom material="{prefix}-dishwasher" mesh="{prefix}-dish_washer_bottom_wheel" class="{prefix}-visual"/>
          <geom mesh="{prefix}-dish_washer_bottom_wheel" class="{prefix}-collision"/>
        </body>
        <body name="{prefix}dish_washer_bottom_wheel_1_r" pos="-0.250505 -0.049095 0.139046" euler="0 3.14159 0">
          <geom material="{prefix}-dishwasher" mesh="{prefix}-dish_washer_bottom_wheel" class="{prefix}-visual"/>
          <geom mesh="{prefix}-dish_washer_bottom_wheel" class="{prefix}-collision"/>
        </body>
        <body name="{prefix}dish_washer_bottom_wheel_2_r" pos="-0.250505 -0.049095 0.040992" euler="0 3.14159 0">
          <geom material="{prefix}-dishwasher" mesh="{prefix}-dish_washer_bottom_wheel" class="{prefix}-visual"/>
          <geom mesh="{prefix}-dish_washer_bottom_wheel" class="{prefix}-collision"/>
        </body>
        <body name="{prefix}dish_washer_bottom_wheel_3_r" pos="-0.250505 -0.049095 -0.087648" euler="0 3.14159 0">
          <geom material="{prefix}-dishwasher" mesh="{prefix}-dish_washer_bottom_wheel" class="{prefix}-visual"/>
          <geom mesh="{prefix}-dish_washer_bottom_wheel" class="{prefix}-collision"/>
        </body>
        <body name="{prefix}dish_washer_bottom_wheel_4_r" pos="-0.250505 -0.049095 -0.190549" euler="0 3.14159 0">
          <geom material="{prefix}-dishwasher" mesh="{prefix}-dish_washer_bottom_wheel" class="{prefix}-visual"/>
          <geom mesh="{prefix}-dish_washer_bottom_wheel" class="{prefix}-collision"/>
        </body>
        <!-- basket -->
        <body name="{prefix}-cuttlery_basket" pos="0.218 0.030 -0.02">
          <geom material="{prefix}-basket" mesh="{prefix}-dish_washer_bottom_cuttlery_basket_001" class="{prefix}-visual"/>
          <geom mesh="{prefix}-collision_dish_washer_bottom_basket_001" class="{prefix}-collision_basket"/>
          <geom mesh="{prefix}-collision_dish_washer_bottom_basket_002" class="{prefix}-collision_basket"/>
          <geom mesh="{prefix}-collision_dish_washer_bottom_basket_003" class="{prefix}-collision_basket"/>
          <geom mesh="{prefix}-collision_dish_washer_bottom_basket_004" class="{prefix}-collision_basket"/>
          <geom mesh="{prefix}-collision_dish_washer_bottom_basket_005" class="{prefix}-collision_basket"/>
          <geom mesh="{prefix}-collision_dish_washer_bottom_basket_006" class="{prefix}-collision_basket"/>
          <geom mesh="{prefix}-collision_dish_washer_bottom_basket_007" class="{prefix}-collision_basket"/>
          <geom mesh="{prefix}-collision_dish_washer_bottom_basket_008" class="{prefix}-collision_basket"/>
          <geom mesh="{prefix}-collision_dish_washer_bottom_basket_009" class="{prefix}-collision_basket"/>
          <geom mesh="{prefix}-collision_dish_washer_bottom_basket_010" class="{prefix}-collision_basket"/>
          <geom mesh="{prefix}-collision_dish_washer_bottom_basket_011" class="{prefix}-collision_basket"/>
          <geom mesh="{prefix}-collision_dish_washer_bottom_basket_012" class="{prefix}-collision_basket"/>
          <geom mesh="{prefix}-collision_dish_washer_bottom_basket_013" class="{prefix}-collision_basket"/>
          <geom mesh="{prefix}-collision_dish_washer_bottom_basket_014" class="{prefix}-collision_basket"/>
          <geom mesh="{prefix}-collision_dish_washer_bottom_basket_015" class="{prefix}-collision_basket"/>
        </body>
      </body>
    """

    _postamble = """
    <contact>
        <exclude body1="{name}" body2="{prefix}door"/>
        <exclude body1="{name}" body2="{prefix}tray_mid"/>
        <exclude body1="{name}" body2="{prefix}tray_bottom"/>
        <exclude body1="{prefix}dish_washer_bottom_wheel_1_l" body2="{name}"/>
        <exclude body1="{prefix}dish_washer_bottom_wheel_2_l" body2="{name}"/>
        <exclude body1="{prefix}dish_washer_bottom_wheel_3_l" body2="{name}"/>
        <exclude body1="{prefix}dish_washer_bottom_wheel_4_l" body2="{name}"/>
        <exclude body1="{prefix}dish_washer_bottom_wheel_1_r" body2="{name}"/>
        <exclude body1="{prefix}dish_washer_bottom_wheel_2_r" body2="{name}"/>
        <exclude body1="{prefix}dish_washer_bottom_wheel_3_r" body2="{name}"/>
        <exclude body1="{prefix}dish_washer_bottom_wheel_4_r" body2="{name}"/>
    </contact>
    """

    # --------------------------------------------------------------------- #
    # You can extend the class with helper properties / methods if desired.
    # --------------------------------------------------------------------- #

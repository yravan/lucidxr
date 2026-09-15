# Simulation source review record

The cleanup reviewed the simulation package by responsibility: XML construction and
merging; primitive components; object and fixture templates; arm, hand, and gripper
models; reusable scene components; adapters and resource resolution; numerical
transforms; and every scene builder. Large MJCF templates were reviewed separately
from executable setup code. Asset mesh/texture contents are data, covered by the
manifest and model loading rather than a source-code review.

The table identifies the source snapshot for this review. The hashes record scope;
they are not a substitute for reviewing code or evidence that every possible input
is correct. Read `../REORGANIZATION.md` for the method, findings, and decisions, and
`xml_schema/README.md` for the resulting architecture.

Validation covers all 32 default scene builds, repeatable construction, ordinary
MuJoCo loading and stepping, robot model/rig loading, selected robot variants,
installed packaging, and asset relocation. Focused tests cover core composition,
instance isolation, seeded export, and quaternion correctness. It does not validate
trained policies, all parameter combinations, differentiable tensor operations, or
physical calibration of imported models. Generic external adapters and unused
furniture presets may require caller-provided resources.

| Reviewed Python module | SHA-256 prefix |
| --- | --- |
| `__init__.py` | `3c4ba0a24669` |
| `assets/__init__.py` | `8fbebf56b090` |
| `scenes/__init__.py` | `0903cb843bb1` |
| `scenes/__main__.py` | `452d106d7e72` |
| `scenes/_sampling.py` | `cf5bc99927fc` |
| `scenes/ball_sorting.py` | `290b698524e4` |
| `scenes/base.py` | `f60c403c74d6` |
| `scenes/basketball_shot.py` | `a6cd530be907` |
| `scenes/fishing_toy.py` | `8d1e1ddef3a9` |
| `scenes/flip_mug.py` | `ea245a7ca6d8` |
| `scenes/insert_shapes.py` | `27ff1df1ceab` |
| `scenes/juggle_cubes.py` | `d40f27ced686` |
| `scenes/kitchen_room.py` | `aa76d49c73df` |
| `scenes/microwave_muffin.py` | `72cda13b2f90` |
| `scenes/move_plate.py` | `d03658b7fa1a` |
| `scenes/mug_drawer.py` | `3c9d592c3bb4` |
| `scenes/mug_tree.py` | `72b2a1ee4dac` |
| `scenes/object_permanence.py` | `491c59205c93` |
| `scenes/orbit_table.py` | `f2d7366b3328` |
| `scenes/particle_pour.py` | `692ee0aa56fc` |
| `scenes/particle_sweep.py` | `95e89e92bec7` |
| `scenes/pick_block.py` | `eff9191826ec` |
| `scenes/pick_place.py` | `14b81a27e166` |
| `scenes/pick_sphere.py` | `cb9055c1b547` |
| `scenes/poncho_table.py` | `9fc4c7c83212` |
| `scenes/pour_liquid.py` | `bc957a08a121` |
| `scenes/push_t.py` | `4e11404faa8d` |
| `scenes/robosuite_door.py` | `e072621ca574` |
| `scenes/robosuite_lift.py` | `2083c03d9dfa` |
| `scenes/robosuite_nutassembly.py` | `e5b11008012a` |
| `scenes/robosuite_pickplace.py` | `9efb348568f9` |
| `scenes/robosuite_stack.py` | `9ae150904a4d` |
| `scenes/sort_shapes.py` | `dc783cd9dd7d` |
| `scenes/stack_blocks.py` | `56149196d29c` |
| `scenes/teddy_bear_table.py` | `d4e31f1e50b6` |
| `scenes/tie_knot.py` | `90c1e25ee320` |
| `scenes/utensil_drawer.py` | `76cc0b84570f` |
| `scenes/weighted_cubes.py` | `8eac4c2ba08a` |
| `xml_schema/__init__.py` | `71d31858717e` |
| `xml_schema/adapters/__init__.py` | `e3b0c44298fc` |
| `xml_schema/adapters/robohive/__init__.py` | `e3b0c44298fc` |
| `xml_schema/adapters/robohive/robohive_object.py` | `4d346f307608` |
| `xml_schema/adapters/robosuite/__init__.py` | `e3b0c44298fc` |
| `xml_schema/adapters/robosuite/robosuite_bin.py` | `64750fcc9e64` |
| `xml_schema/adapters/robosuite/robosuite_door.py` | `9ecd3f91b44a` |
| `xml_schema/adapters/robosuite/robosuite_tablearena.py` | `7ae07c3aa2cc` |
| `xml_schema/base.py` | `90972d6a0838` |
| `xml_schema/document.py` | `eaef85d6e9bb` |
| `xml_schema/objects/__init__.py` | `7a82c59387c8` |
| `xml_schema/objects/bagel.py` | `395ecbbe3be5` |
| `xml_schema/objects/ball.py` | `da9b6d9a9f3e` |
| `xml_schema/objects/basket.py` | `b2ae0c1757aa` |
| `xml_schema/objects/bigym_dishdrainer.py` | `b1aefe72ef27` |
| `xml_schema/objects/bigym_plate.py` | `ca892347f03d` |
| `xml_schema/objects/bigym_table.py` | `6e51b268c319` |
| `xml_schema/objects/bin.py` | `9620708b9eae` |
| `xml_schema/objects/block.py` | `c7a727822897` |
| `xml_schema/objects/bowl.py` | `477f09827cf2` |
| `xml_schema/objects/brown_table.py` | `56ff3e81ba7e` |
| `xml_schema/objects/concrete_slab.py` | `338b2a1abddb` |
| `xml_schema/objects/cube.py` | `a07dc71daa15` |
| `xml_schema/objects/cup.py` | `d9d5db26dcd0` |
| `xml_schema/objects/cylinder.py` | `f41410ae1916` |
| `xml_schema/objects/decomposed_obj.py` | `472d61b4c478` |
| `xml_schema/objects/eval_sdf.py` | `a656c9cefc2d` |
| `xml_schema/objects/fixtures/__init__.py` | `e3b0c44298fc` |
| `xml_schema/objects/fixtures/cabinet.py` | `c8698a9cdd1f` |
| `xml_schema/objects/fixtures/cupcake.py` | `54ab13999b3f` |
| `xml_schema/objects/fixtures/dishwasher.py` | `33f3737fe953` |
| `xml_schema/objects/fixtures/drawer.py` | `b722dfa38b43` |
| `xml_schema/objects/fixtures/drawer_stack.py` | `3f3b48321711` |
| `xml_schema/objects/fixtures/drawer_visual.py` | `3642f7297aa7` |
| `xml_schema/objects/fixtures/granite_countertop.py` | `4db3426d6a64` |
| `xml_schema/objects/fixtures/microwave.py` | `715392d6c107` |
| `xml_schema/objects/fixtures/microwave_scaled.py` | `91a107015657` |
| `xml_schema/objects/fixtures/oven.py` | `5fd3a379e27d` |
| `xml_schema/objects/fixtures/refrigerator.py` | `93e00db7d22b` |
| `xml_schema/objects/fixtures/room_wall.py` | `c5e4182cd445` |
| `xml_schema/objects/fixtures/single_cabinet.py` | `e0e3ab704739` |
| `xml_schema/objects/fixtures/sink.py` | `d50fb5c4488b` |
| `xml_schema/objects/fixtures/sink_wide.py` | `f12441e396de` |
| `xml_schema/objects/mesh_object.py` | `651a5c373c12` |
| `xml_schema/objects/mimicgen_drawer.py` | `2eb3f22ca3f7` |
| `xml_schema/objects/mj_obj.py` | `ead3b84f0e83` |
| `xml_schema/objects/mj_sdf.py` | `b081bc745d30` |
| `xml_schema/objects/mug.py` | `dbd1535b07ba` |
| `xml_schema/objects/mujoco_mug.py` | `160c96c491b4` |
| `xml_schema/objects/orbit_table.py` | `e902573b840b` |
| `xml_schema/objects/plate.py` | `fbf70ca3271d` |
| `xml_schema/objects/poncho.py` | `24fdb48f0656` |
| `xml_schema/objects/rope.py` | `6f23c2432179` |
| `xml_schema/objects/sort_shapes.py` | `2269f581cf09` |
| `xml_schema/objects/spoon_7.py` | `5efbca62a00e` |
| `xml_schema/objects/tshape.py` | `457ac18f8474` |
| `xml_schema/objects/vuer_mug.py` | `fa21e7eddc67` |
| `xml_schema/objects/white_table.py` | `cdb3dea5702c` |
| `xml_schema/robots/__init__.py` | `e3b0c44298fc` |
| `xml_schema/robots/arms/__init__.py` | `e3b0c44298fc` |
| `xml_schema/robots/arms/astribot.py` | `c676dfb41c5b` |
| `xml_schema/robots/arms/franka_panda.py` | `7da54c404b54` |
| `xml_schema/robots/arms/lift.py` | `f56aa3e692f7` |
| `xml_schema/robots/arms/ufactory_xarm7.py` | `6776e57f998b` |
| `xml_schema/robots/arms/ur5e.py` | `7237a9416539` |
| `xml_schema/robots/grippers/__init__.py` | `e3b0c44298fc` |
| `xml_schema/robots/grippers/robotiq_2f85.py` | `59aaba90ce5a` |
| `xml_schema/robots/grippers/tomika_gripper.py` | `cff32111a6d5` |
| `xml_schema/robots/grippers/ufactory_gripper.py` | `2f0419059bab` |
| `xml_schema/robots/hands/__init__.py` | `e3b0c44298fc` |
| `xml_schema/robots/hands/ability_hand.py` | `3bde634fc879` |
| `xml_schema/robots/hands/dexhand.py` | `bacbd388c4eb` |
| `xml_schema/robots/hands/mpl_hand.py` | `bd1163205c26` |
| `xml_schema/robots/hands/shadow_hand.py` | `7fdf5fb306b3` |
| `xml_schema/robots/hands/xhand.py` | `84e8d4a44a77` |
| `xml_schema/scene_components/__init__.py` | `9df9cf56df89` |
| `xml_schema/scene_components/cameras/__init__.py` | `e3b0c44298fc` |
| `xml_schema/scene_components/cameras/presets.py` | `861c0cf147ad` |
| `xml_schema/scene_components/cameras/rig.py` | `38f7ba95a1e2` |
| `xml_schema/scene_components/cameras/rig_calibrated.py` | `cc1b13b1c3c8` |
| `xml_schema/scene_components/cameras/rig_hand.py` | `00f32e131c31` |
| `xml_schema/scene_components/cameras/rig_lower_fov.py` | `a14b8dfebf55` |
| `xml_schema/scene_components/cameras/rig_ortho.py` | `eb2cac8bf223` |
| `xml_schema/scene_components/cameras/rig_stereo.py` | `be964e9d71cc` |
| `xml_schema/scene_components/cameras/rig_zoomed_out.py` | `4f02476c66dc` |
| `xml_schema/scene_components/lighting.py` | `9a2524f9d8d6` |
| `xml_schema/scene_components/robots/__init__.py` | `832c7f6e8676` |
| `xml_schema/scene_components/robots/astribot.py` | `189e0ef33eca` |
| `xml_schema/scene_components/robots/dual_panda.py` | `42016f386a48` |
| `xml_schema/scene_components/robots/dual_robotiq_2f85.py` | `c0c276794602` |
| `xml_schema/scene_components/robots/dual_ur5e.py` | `ad1b611537bf` |
| `xml_schema/scene_components/robots/floating_ability_hand.py` | `f2eb9c34b50b` |
| `xml_schema/scene_components/robots/floating_hands.py` | `cf876ac44b30` |
| `xml_schema/scene_components/robots/floating_mpl_hand.py` | `b9195cc1e683` |
| `xml_schema/scene_components/robots/floating_robotiq.py` | `b22e1d1b1319` |
| `xml_schema/scene_components/robots/lift.py` | `12eb70b94ea3` |
| `xml_schema/scene_components/robots/panda.py` | `e4cd684321ca` |
| `xml_schema/scene_components/robots/planar_pusher.py` | `d236cba14694` |
| `xml_schema/scene_components/robots/ur5.py` | `264e392192e1` |
| `xml_schema/scene_components/rooms/__init__.py` | `57654785b74a` |
| `xml_schema/scene_components/rooms/brick_room.py` | `2119485fde1f` |
| `xml_schema/scene_components/rooms/kitchen.py` | `133ddf7927d4` |
| `xml_schema/scene_components/rooms/plain_room.py` | `f9f955a0bac3` |
| `xml_schema/scene_components/rooms/stage.py` | `18a74b343d4b` |
| `xml_schema/scene_components/rooms/staging.py` | `72e40f3ff077` |
| `xml_schema/scene_components/settings.py` | `7e30c407b566` |
| `xml_schema/scene_components/tables.py` | `dc931777a70b` |
| `xml_schema/schema.py` | `8880704c0a15` |
| `xml_schema/simple_components/__init__.py` | `e3b0c44298fc` |
| `xml_schema/simple_components/box.py` | `389cb15953ec` |
| `xml_schema/simple_components/camera.py` | `34f58439303c` |
| `xml_schema/simple_components/concrete_slab.py` | `569fed6b33e3` |
| `xml_schema/simple_components/coordinate_axes.py` | `4a22b701323d` |
| `xml_schema/simple_components/force_plate.py` | `7244faa71138` |
| `xml_schema/simple_components/light.py` | `f044dd379cf7` |
| `xml_schema/simple_components/mj_ground_plane.py` | `1bfda673d016` |
| `xml_schema/simple_components/motion.py` | `012f9ab12aef` |
| `xml_schema/simple_components/particles.py` | `3f2d838987e0` |
| `xml_schema/simple_components/placeholder_obj.py` | `88b83dd007d5` |
| `xml_schema/simple_components/planar_pusher.py` | `eb3267314b38` |
| `xml_schema/simple_components/table_slab.py` | `79d8600d2d1b` |
| `xml_schema/simple_components/tile_floor.py` | `946eeb92c026` |
| `xml_schema/transforms/__init__.py` | `e3b0c44298fc` |
| `xml_schema/transforms/helpers.py` | `c1f3136d8c09` |
| `xml_schema/transforms/mujoco.py` | `ec939c1047d8` |
| `xml_schema/transforms/rotation6d.py` | `7f4c6ac0c37b` |
| `xml_schema/transforms/three.py` | `f4661bd9f7b6` |
| `xml_schema/transforms/vector.py` | `b527363037e4` |
| `xml_schema/utils/__init__.py` | `92f55647ae5d` |
| `xml_schema/utils/collect_asset_paths.py` | `14a790f03e58` |
| `xml_schema/utils/file.py` | `7d80b1f72bdd` |
| `xml_schema/utils/flatten_paths.py` | `33d9459abd65` |
| `xml_schema/utils/minimizer.py` | `abdaa8f7e53d` |
| `xml_schema/utils/path_rewrite.py` | `ad0ce20a1609` |
| `xml_schema/utils/tree_merge.py` | `11daca309049` |
| `xml_schema/utils/whitener.py` | `60d333a37023` |

# Environment migration: dependency and behavior audit

The old package did not pin dm_control, dm_env, gym_dmc or MuJoCo. This audit
compares the local original source with current upstream source; it cannot
establish which dependency versions produced an old recording.

## Dependency chain

`tasks/entrypoint.py` builds `SimplePhysics`, a subclass of dm_control's
`mujoco.Physics`, then a `PlaybackTask` subclass, then
`dm_control.rl.control.Environment`, then `LucidEnv`, then gym_dmc's
`FlattenObservation` and image wrappers.

- dm_control owns model/data, reset contexts, physics stepping and rendering.
- dm_control's suite Task supplies actuator limits, control assignment and RNG.
- dm_env supplies array specs and FIRST/MID/LAST timesteps with discounts.
- gym_dmc supplies a vendored Gym interface, space conversion and flattening.
- LucidEnv adds frame restoration, action extraction, settling and frame skipping.
- MuJoCo performs simulation. NumPy and schema rotation transforms encode poses.
- New image wrappers add RGB, depth, segmentation, masks, overlays, calibration,
  inverse-depth conditioning and domain randomization. Gaussian-splat rendering
  additionally depends on an external `neverwhere` integration.
- Vuer collects physics frames through its browser simulator; pandas-based
  workers replay these into the Python environment to produce training data.
  Neither Vuer nor pandas needs to be an environment runtime dependency.

Upstream sources inspected:
- https://github.com/geyang/gym-dmc/blob/master/gym_dmc/dmc_env.py
- https://github.com/google-deepmind/dm_control/blob/main/dm_control/rl/control.py
- https://github.com/google-deepmind/dm_control/blob/main/dm_control/suite/base.py

## Behavior that the new design must retain

1. Compile a schema Scene with its asset resolver directly, without changing cwd
   or requiring generated XML files. Each environment owns its model and data.
2. Expose native actuator controls and world-space mocap position/quaternion
   arrays in a Gymnasium Dict action space. The old learned format was
   `[position(3), rotation6d(6)]` per target, then ctrl. That is a policy encoding,
   not the simulator interface. Quaternion/6D conversion and vector packing belong
   in policy adapters; MuJoCo's native quaternion order is wxyz.
3. Preserve the ability to command hand targets, but convert wrist-relative
   fingers into world-space targets in policy adapters. The environment does not
   infer hands, six-target groupings, or relative action representations.
4. Return native measured site positions/matrices separately from commanded
   targets. Site selection, flattening and encoding belong in policy preprocessing;
   do not infer measured sites from an array tail or mocap-body ordering.
5. Replay recorded qpos, qvel, act, ctrl and mocap poses without stepping. Recompute
   derived sites/sensors and render observation wrappers from the restored state.
   Frame restoration, observation, reward evaluation and episode advancement must
   be separate operations. Reading a frame must not increment success counters
   or resample domain randomization.
6. Preserve a full simulator snapshot for exact continuation separately from
   partial legacy recording frames, which omit time, warmstart and other inputs.
7. Explicit physics substeps/control interval, reset settling and keyframes.
   The old factory used 0.02 s control steps (10 x 0.002 s), 50 settling steps and
   a 25-second limit. These are configuration, not universal scene properties.
8. Episode initialization, rewards, success and termination remain extensible.
   Scene describes physical composition; runtime episode rules must not force
   every Scene subclass to implement more than build(). Existing task rewards
   are heuristics (some explicitly untested), not validated benchmark metrics.
9. Gymnasium reset returns (observation, info); step returns observation, reward,
   terminated, truncated, info. Time limits are distinct from task termination.
   Observation wrappers must declare accurate shapes, bounds and dtypes.
10. Multi-camera RGB, metric depth, RGBD, calibration, geometry segmentation,
    semantic remapping, object masks, robot overlays and inverse depth support
    the offline dataset path as well as online rollouts. Geometry IDs stay int32;
    background stays -1; masks retain image shape. Randomization is seeded and
    restores model defaults instead of accumulating drift.

## Bugs to avoid reproducing

- gym_dmc converts unbounded observations to [-pi, pi] and advertises stale specs.
- PlaybackTask advertises a fixed length-10 observation regardless of the model.
- MocapHandTask slices with `[:-0]` when no actuators exist and assumes six
  consecutive targets per hand. Measured site ordering is a separate array.
- get_prev_action actually returns the command encoded from current target/ctrl
  state, not necessarily the previous policy action.
- get_ordi calls termination logic with side effects during offline rendering.
- set_to_frame ignores its qvel argument and can partially write mismatched arrays.
- reset initializes an episode twice; several counters/buffers are class state.
- dm_control termination returns a discount or None, not a Gym boolean. Returning
  True from the old success hook ended the episode with discount 1, which is an
  ambiguous signal when translated through the old four-item Gym API.
- render wrappers expose undeclared observation keys, truncate geom IDs to 8 bits,
  mutate visibility globally and couple randomization to observation reads.

Real robot environments and old_info_wrappers are excluded. Training launchers,
teleop UI and external splat-model loading are separate integration work; the
runtime should offer clear state/action/render interfaces for them.

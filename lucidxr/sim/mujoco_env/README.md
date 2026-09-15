# Native MuJoCo environments

`MujocoEnv` compiles a `Scene` directly and owns its model, data, episode lifecycle
and lazy rendering. Actions and observations are dictionaries of physical
quantities. Policy-specific encodings belong in policy input/output adapters.

```python
from lucidxr.sim.mujoco_env import make_env

with make_env("pick_block", max_episode_steps=1250) as env:
    observation, info = env.reset(seed=7)
    action = env.unwrapped.current_action()
    # Change an actuator command or a world-space mocap target here.
    observation, reward, terminated, truncated, info = env.step(action)
```

## Commands and observations

`action_space` is a Gymnasium `Dict`:

| Field | Shape | Meaning |
| --- | --- | --- |
| ctrl | (nu,) | Native actuator commands, within model control limits |
| mocap_pos | (nmocap, 3) | Absolute world-space target positions, meters |
| mocap_quat | (nmocap, 4) | World-space target orientations, wxyz |

Mocap keys are present only when the model has mocap bodies. `ctrl` is always
present, including an empty array for models without actuators. Each step requires
exactly the declared fields. All fields are validated before writing: wrong
shapes, nonfinite values, out-of-range commands and zero quaternions raise.
Nonzero quaternion rows inside [-1,1] are normalized before application. The
Box describes component bounds; the additional nonzero constraint is checked at
runtime. Caller arrays are never modified. `current_action()` returns copies of
the current commanded values, not a previous policy output or measured pose.

Observations contain qpos, qvel, act, ctrl, mocap_pos, mocap_quat, sensordata,
site_xpos and site_xmat. These use native MuJoCo shapes, including (nsite, 9) for
site rotation matrices. Sites are measured quantities, separately from mocap
targets. Use model named access and body_mocapid to map names to array indices.
All returned arrays are copies.

Flattening, normalization, quaternion/6D conversion, delta actions and
wrist-relative finger coordinates belong in the policy layer. The simulator
has no ActuatorControl/MocapControl classes or encoded Proprioception wrapper.
Recorded data can therefore be reused across policies with different encodings.

## Episode and playback lifecycle

A Scene still overrides only `build()`. `make_env` accepts an instance or catalogue
name with `scene_options`. Scene.seed controls physical construction;
reset(seed=...) seeds runtime sampling and does not rebuild the Scene.

Subclass `Episode` for objectives: reset(env) initializes state with env.np_random,
after_step(env) updates counters, and read-only evaluate(env) returns
(reward, terminated, info). Defaults permit free rollout with zero reward.
Historical task reward heuristics are not automatically attached to scenes.

frame_skip defaults to 10 physical steps per action; env.dt uses the model's
actual timestep. Optional settle_steps runs during reset. Gymnasium TimeLimit
sets truncated independently of task termination. MuJoCo instability raises
FloatingPointError instead of returning fabricated data; reset before continuing.

reset options accept a keyframe name/ID and/or a partial frame. Without a keyframe,
default ctrl is clamped to actuator bounds before episode initialization.
frame() records qpos, qvel, act, ctrl and mocap poses. restore_frame(frame) validates
all supplied fields, writes them and recomputes derived sites/sensors without
stepping or incrementing counters. Select these fields explicitly from old rows;
recorded site arrays are derived outputs, not writable inputs.

snapshot()/restore_snapshot() preserve MuJoCo integration state, including time
and warmstart, for the same model. They do not capture episode/wrapper counters,
RNG state or randomized model properties. Old partial frames are suitable for
rerendering, but do not promise bitwise historical trajectory reproduction.

## Wrappers

Each randomizer now has a dedicated parameter dataclass and shares the lifecycle
in RandomizationWrapper. CameraRandomization and LightingRandomization compose
shared PositionRandomization/RotationRandomization samplers. MaterialRandomization
handles surface properties; TextureRandomization handles role-aware pixel edits.

```python
from lucidxr.sim.mujoco_env.wrappers import (
    Camera,
    CameraWrapper,
    CameraRandomization,
    CameraRandomizationParams,
    LightingRandomization,
    LightingRandomizationParams,
    PositionRandomization,
)

env = make_env("pick_block")
env = CameraRandomization(
    env,
    CameraRandomizationParams(
        names=("wrist",),
        position=PositionRandomization(0.01),
        fovy=3.0,
    ),
)
env = LightingRandomization(env, LightingRandomizationParams(active_probability=0.75))
env = CameraWrapper(env, [Camera("wrist", products=("rgb", "depth", "segmentation"))])
try:
    obs, info = env.reset(seed=7)
    env.unwrapped.restore_frame(env.unwrapped.frame())
    obs = env.observe()
finally:
    env.close()
```

See [the complete randomization guide](RANDOMIZATION.md) for parameter tables,
light-pool counts, texture types/roles and patterns, material properties, scheduling,
GPU uploads, performance boundaries and coverage against the original wrappers.

CameraWrapper is only observation composition. CameraView binds each configuration
to model IDs, declares spaces and captures products. Each Camera supports:

| Product | Output |
| --- | --- |
| rgb / overlay | H x W x 3 uint8; overlay keeps masks, white elsewhere |
| depth | H x W float32 metric optical-axis depth |
| rgbd | H x W x 4 float32, RGB 0–255 plus metric depth |
| segmentation | H x W int32 geom IDs; background/non-geoms -1 |
| semantic | H x W int32 from exact geom-name → class mapping; unmatched -1 |
| inverse_depth / masked_inverse_depth | H x W float32 [0,1], configured near/far |
| mask/name | H x W boolean body-subtree mask |
| K / C2W | Pinhole calibration and OpenCV camera-to-world pose |

Use masks={"robot": ("robot_body",)}, semantic={"geom_name": 12}, and
hide_bodies=("robot_body",) as needed. Hidden geometry affects visualization only.
key="background" changes the output prefix so multiple configurations can share
one camera. Calibration defaults on; disable it for orthographic cameras. Metric
depth products are intended for perspective cameras.

## Performance boundaries

Adjacent compatible observation wrappers execute in one iterative pass. Built-in
camera wrappers add fields to one owned dictionary rather than copying a growing
dictionary per wrapper. Adjacent randomizers reset/sample in one pass with one
model refresh; step() bypasses their forwarding chain when periodic sampling is disabled. Fusion
stops at third-party wrappers and custom lifecycle overrides, preserving their
behavior. Keep randomizers together, followed by observation wrappers.

Identical image/calibration requests across the observation pass are computed
once; returned arrays remain independently writable. The cache ends with that
observation, so replay edits and later simulation steps cannot reuse stale images.
A bounded pool retains four render resolutions. Geometry IDs, masks and semantic
lookup tables are resolved once at construction. These optimizations do not make
100 distinct high-resolution renders free: real image computation and output
memory still scale with what is requested.

Run the manual microbenchmark with:
`uv run python lucidxr/tests/benchmark_wrappers.py`.
It compares the same small scene with no wrappers, 100 identity wrappers,
100 randomizers, and 1 versus 100 identical camera requests. Focused tests also
assert one render per observation for 100 cameras and one refresh per reset for
100 randomizers; timing thresholds are deliberately not unit-test assertions.

## Migration boundaries

This replaces SimplePhysics/dm_control/gym_dmc/LucidEnv with native MuJoCo and
Gymnasium. Old training workers need command/observation adapters. get_prev_action
becomes current_action; set_to_frame/get_ordi become explicit restore_frame,
observe and Episode.evaluate operations. Camera/depth/segmentation/mask/overlay
wrappers become camera products. MidasDepth wrappers were inverse-depth
normalization, not learned depth models. DomainRandomizationWrapper is replaced
by the independently composable randomizers above.

Real robots, old_info_wrappers, external Gaussian-splat loading, ADE palette
visualization are not ported. Human viewer
interaction and cluster GPU rendering have not been tested. Physics-only workers
create no graphics context; close() releases render resources. On macOS use
`uv run mjpython ...` for human rendering. Offscreen tests exercise macOS OpenGL,
which reports limited depth precision without ARB_clip_control; RGB comparisons
allow one intensity unit of render-mode rounding variation.

See [the original dependency and behavior audit](DESIGN.md).

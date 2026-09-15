# Scene-backed MuJoCo environments

`MujocoEnv` owns a compiled `Scene`, `MjModel`, `MjData`, and lazy rendering.
It implements Gymnasium directly. No dm_control, gym_dmc, logging service,
working-directory changes or generated XML files are required.

```python
from lucidxr.sim.mujoco_env import MocapControl, make_env

with make_env("pick_block", control=MocapControl(), max_episode_steps=1250) as env:
    observation, info = env.reset(seed=7)
    action = env.unwrapped.current_action()  # hold the current commanded pose
    observation, reward, terminated, truncated, info = env.step(action)
```

The default control is `ActuatorControl`: a vector in model actuator order.
Choose `MocapControl` for floating grippers/hands or mocap-driven robot arms.
This takes `[x,y,z, rotation6d]` for every mocap body, followed by actuator ctrl.
Rotation6d concatenates the first two rotation-matrix columns. Zero/collinear
rotation columns are rejected. The supported quaternion convention is wxyz.
Raw MuJoCo control limits are retained; actions are not normalized to [-1,1].
The encoder clips numerical rotation roundoff to its mathematical bounds.

Hands can use `MocapControl(relative_to={"finger_target": "wrist_target"})`:
use actual mocap body names from your scene. Parent wrists are world-relative;
finger positions/rotations are relative to their wrist. Model ordering determines
vector ordering, so inspect `model.body_mocapid` before reusing an old dataset.
There is no implicit grouping of six bodies or assumption about site ordering.

`Proprioception(env, sites=("pinch_site", ...), relative_to={...})` provides
measured site poses plus ctrl under `observation["state"]`. Its optional mapping
uses **site names**, independently from the controller's mocap **body names**.
The default environment observation is a dictionary of qpos, qvel, act, ctrl,
mocap_pos, mocap_quat and sensordata. All returned arrays are copies.

## Scenes and episode rules

A Scene still overrides only `build()`. Pass a Scene instance directly to
`MujocoEnv`, or a catalogue name to `make_env`. Scene construction randomness uses
`Scene.seed`; `reset(seed=...)` seeds runtime episode/randomization sampling and
does not rebuild the scene. Use `scene_options={"seed": 7}` with `make_env` to
choose a scene construction seed.

Runtime objectives subclass `Episode` and use the environment's named model/data
access. `reset(env)` initializes episode state with `env.np_random`;
`after_step(env)` updates any counters; `evaluate(env)` returns
`(reward, terminated, info)` and must be read-only. Defaults are zero reward and
no task termination, suitable for teleop and playback. Historical per-task reward
heuristics are not automatically attached to the scene catalogue or claimed to
be validated benchmarks.

`frame_skip` is the number of physics steps per control action (default 10).
`env.dt` uses the model timestep rather than assuming every scene uses 0.002 s.
`settle_steps` optionally advances physics during reset (default 0), before the
returned initial observation. Time limits use Gymnasium's `TimeLimit` wrapper;
timeouts set `truncated`, while Episode rules set `terminated`.

Reset accepts `options={"keyframe": "name"}` or a numeric keyframe ID, and/or
`options={"frame": {...}}`. Without a keyframe, default ctrl is clamped into
actuator bounds before initialization. Explicit recording frames retain their
ctrl values; unsupported keys and wrong shapes raise instead of partial writes.
MuJoCo instability raises `FloatingPointError`; reset before continuing. The env
does not substitute random observations or silently treat an automatic physics
reset as a successful transition.

## Recording and playback

```python
from lucidxr.sim.mujoco_env.wrappers import Camera, CameraWrapper

env = CameraWrapper(
    make_env("pick_block", control=MocapControl()),
    [
        Camera("wrist", width=320, height=240, products=("rgb", "depth", "segmentation")),
    ],
)
try:
    obs, info = env.reset(seed=7)
    frame = env.unwrapped.frame()
    env.unwrapped.restore_frame(frame)
    obs = env.observe()  # all configured image products, no simulation step
    action = env.unwrapped.current_action()
finally:
    env.close()
```

`frame()` returns portable qpos/qvel/act/ctrl/mocap arrays. For old dataframe rows,
select those fields explicitly; old site positions/matrices are derived outputs,
not writable simulator state. `restore_frame` validates every supplied field
before writing and calls `mj_forward` to update derived quantities. It never
increments episode counters, advances time, or randomizes the model.

`snapshot()` / `restore_snapshot()` use MuJoCo's full integration-state API,
including time and warmstart. These are for continuation with the **same model**;
they do not include Episode state, wrapper counters, RNG state or randomized model
parameters. Portable old frames omit some integration inputs, so they are suitable
for rerendering but cannot promise bitwise historical trajectory reproduction.
For wrappers outside this package, use `env.get_wrapper_attr("observe")()`.

## Image products and randomization

One `CameraWrapper` accepts multiple `Camera` configurations. Outputs use
`<camera>/<product>` keys and declare their actual observation spaces:

| Product | Format |
| --- | --- |
| rgb | H x W x 3 uint8 |
| depth | H x W float32, optical-axis distance in meters |
| rgbd | H x W x 4 float32: RGB 0–255 and metric depth |
| segmentation | H x W int32 geometry IDs, background/non-geometry -1 |
| semantic | H x W int32 classes from exact geom-name mapping; unmatched -1 |
| inverse_depth | H x W float32 in [0,1], using configured near/far |
| masked_inverse_depth | inverse depth retained inside the configured masks |
| overlay | RGB inside the union of masks, white elsewhere |
| mask/name | H x W boolean mask for named body subtrees |
| K, C2W | float64 pinhole calibration and OpenCV camera-to-world pose |

Set `masks={"robot": ("robot_root_body",)}` and/or
`semantic={"geom_name": 12}`. `hide_bodies=("robot_root_body",)` removes entire
subtrees from rendered images without changing model geometry. Use two Camera configurations with distinct `key="full"` / `key="background"`
output prefixes if you need both full and robot-free views from one camera. Prefix-based
selection, 8-bit ID truncation, packed masks and implicit ADE class tables are
replaced by explicit names and mappings. Pinhole calibration rejects orthographic
cameras; metric depth products are intended for perspective cameras.

`DomainRandomization(env, VisualRandomization(...))` samples camera pose/FOV,
lighting position/colors, geometry/material colors, and optional texture tints.
Wrap it **inside** Proprioception/CameraWrapper. It samples at reset using the
environment RNG; call `randomize()` explicitly for another offline variant.
Every sample starts from captured defaults. `observe()` never resamples.
Textures are opt-in to avoid copying large texture buffers unnecessarily.
Model dynamics are not randomized (the old wrapper also refused that mode).

## Old-to-new mapping

| Original | Replacement |
| --- | --- |
| SimplePhysics + dm_control Environment + LucidEnv/DMCEnv | MujocoEnv(Scene) |
| JointSpaceTask | ActuatorControl + explicit Proprioception sites |
| MocapTask / MocapHandTask | MocapControl, with named relative_to mapping for hands |
| PlaybackTask initialization/reward/success | Episode hooks, separate from physical Scene |
| get_prev_action | current_action (accurately describes its behavior) |
| set_to_frame / get_obs / get_ordi | restore_frame, observe, Episode.evaluate separately |
| CameraWrapper / DepthWrapper / RGBDWrapper | Camera.products |
| SegmentationWrapper / SegmentationRGBWrapper | segmentation / semantic products; colorize class IDs downstream |
| MaskWrapper / OverlayWrapper | Camera.masks / overlay |
| MidasDepthWrapper / MaskedMidasDepthWrapper | inverse_depth / masked_inverse_depth; these never loaded a MiDaS model |
| create_multiview_env | CameraWrapper with multiple Camera configurations |
| DomainRandomizationWrapper + large mjmod helper | DomainRandomization + VisualRandomization |

This is an API redesign, not a drop-in adapter for deprecated training workers.
Texture checker/noise synthesis, ADE palette visualization, Gaussian-splat model
loading (`neverwhere`), and offline real-camera passthrough are not ported into
this native simulator layer. Existing learned weights need their original
observation/action preprocessing when migrating. Real-robot implementations and
old_info_wrappers are excluded.

Rendering is lazy; physics-only workers do not create a graphics context.
Call `close()` or use a context manager. Human rendering uses MuJoCo's passive
viewer; on macOS run it with `uv run mjpython ...`. Offscreen RGB/depth/segmentation
were exercised on macOS OpenGL, which reports limited depth precision without
ARB_clip_control; RGB can differ by one intensity unit across rendering modes.
Human viewer interaction and GPU cluster rendering have not been exercised here.

See [the dependency and behavior audit](DESIGN.md) for the evidence behind these
boundaries and the original failure modes.

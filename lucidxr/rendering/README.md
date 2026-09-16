# Offline rendering

Render recorded physical states through the existing simulator camera code. Install
`uv sync --extra rendering` and run:

```sh
uv run --extra rendering python -m lucidxr.scripts.render_demo recording.npz \
  --output /path/to/renders --cameras wrist --width 640 --height 360 \
  --products rgb depth segmentation
```

Use `--output-location renders --infra-config /path/to/infra.toml` instead of
`--output` to resolve a root from infra. List scene camera names with `view_scene
SCENE --describe`. The initial backend is native MuJoCo. Set `MUJOCO_GL=egl` before
starting Python on headless Linux GPU nodes; no silent change of renderer backend.

## Explicit identity, ordinary files

The entry point for a finished render is the JSON completion record printed by the
command. It contains the source SHA256, render configuration, code/dependency
fingerprints, recording metadata, frame count, relative artifact paths and checksums.
No task, camera, split or variant is inferred from directory names. Moving the entire
output root preserves the references. Different requests produce different work IDs;
repeating a request verifies and reuses its accepted output.

Each attempt owns one HDF5 plus one MP4 per camera. HDF5 stores rendered physical
fields, source elapsed times/frame indices, explicit camera names, video frame
mapping, K/C2W calibration and requested lossless depth/segmentation. RGB is H.264
CRF 18, yuv420p, no B frames, a one-second maximum GOP. It is lossy; it is not an
exact RGB archival format. Video playback fps is explicit and does not resample
states or establish a control rate. All arrays/video streams preserve source order.

New recordings use simulation seconds from a MuJoCo clock sensor. Commands at
frame i drive the interval ending at i; frame 0 supplies an initial condition.
`simulation_time` records the actual rendered simulation clock, while `elapsed`
keeps the source episode's relative schedule. HDF5 `frames` always describes the
rendered scene, including after command replay into a different scene. Metadata
records the output field shapes and named controls separately from source metadata.
This remains a replay result, not a finalized training dataset exporter.

Files stream into unique attempt directories, close, then validate by fully decoding
videos and checking frame counts/timestamps. A completion record is published with
a same-filesystem hard link after artifact fsync; a concurrent valid completion
wins without overwrite. Filesystems must support hard links. Interrupted attempts
are never completion records; errors retain attempt files and a failure record
when storage permits. Logs identify work, attempt, progress, elapsed time and errors.
Corrupt accepted results fail explicitly instead of silently rerendering over them.
`read_result(path)` verifies artifact hashes; treat complete outputs as immutable.

Modules have one job: `spec` defines requests/identity, `replay` restores/captures,
`output` owns serialization/validation/publication. There is no queue, training
import or network operation inside the renderer. Failed work retries at episode
granularity; frame-level resume is deliberately absent.

See [DESIGN.md](DESIGN.md) for the distributed execution/staging sequence.

## Two playback modes

`--mode state` restores every recorded state and requires the original scene/assets.
`--mode commands` initializes from frame 0, then applies ctrl and mocap targets while
advancing physics to each recorded sample. The viewer and renderer share
`lucidxr.sim.playback`; video fps and display speed never set the physics timestep.

```sh
uv run --extra rendering python -m lucidxr.scripts.render_demo demo.npz \
  --output /data/renders --cameras wrist --mode commands \
  --scene pick_sphere --seed 9
```

An explicit target scene keeps its own reset state and object layout. Controls are
mapped by actuator and mocap-body names, with actuator transmission/gear/range
checks. Different robots require retargeting and are rejected; matching array sizes
are insufficient. Mocap coordinates are world-space and must describe the intended
workspace in the target scene. Incompatible physics timesteps fail explicitly
instead of rounding away time. Command replay produces new physics outcomes; it
is not a promise of identical trajectories across different scenes or engine versions.

Only the current recording format is supported. Collection, not a migration shim,
must supply simulation time and the named control contract.

Distributed workers use the same renderer through `infra.rendering`, which owns
scratch placement and worker allocation. `output.copy_result` owns the format-aware
publication protocol: transfer all verified artifacts, then atomically publish the
completion record. Core rendering accepts ordinary paths and does not import infra.
See [remote launch and recovery](../../infra/README.md) for cluster commands.

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

Each attempt owns one HDF5 plus one MP4 per camera. HDF5 stores original physical
fields, source elapsed times/frame indices, explicit camera names, video frame
mapping, K/C2W calibration and requested lossless depth/segmentation. RGB is H.264
CRF 18, yuv420p, no B frames, a one-second maximum GOP. It is lossy; it is not an
exact RGB archival format. Video playback fps is explicit and does not resample
states or establish a control rate. All arrays/video streams preserve source order.

PR #3 timestamps are server-receive times, not simulation/control timestamps.
Captured commands are preserved without inventing shifted training labels. This
is a replay result, not a finalized training dataset schema or dataset exporter.

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

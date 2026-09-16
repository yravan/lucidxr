# Demo workflows

These entry points take ordinary filesystem paths. They do not import `infra`,
resolve hostnames, launch cluster jobs or manage Dropbox. The optional personal
infra CLI supplies the recorder's output directory at the shell boundary.

## Record

```bash
uv sync --extra teleop
uv run python -m lucidxr.scripts.view_scene pick_block --describe
uv run --extra teleop python -m lucidxr.scripts.record_demo pick_block \
  --output ~/lucidxr-data/demos/pick_block
```

Or, after configuring [infra](../../infra/README.md):

```bash
uv run --extra teleop python -m lucidxr.scripts.record_demo pick_block \
  --output "$(uv run python -m infra path demos)/pick_block"
```

Open the printed server URL. The recorder retains the original browser-side
MuJoCo/Vuer interaction, using current Scene construction and a temporary bundle
of only its referenced assets. It never changes the process working directory or
serves your output folder. The server binds to localhost by default; a headset
needs a reachable HTTPS endpoint supplied with `--public-url`. Configure networking
outside this script; no tunnel or credentials are created automatically. Use
`--host` if the intended network setup needs another bind address.

Blue starts recording; blue again saves. Red discards unsaved frames. Green resets
the scene after saving or discarding. The simulator runs while recording is off.
A single client owns collection; reconnecting does not combine another client's
frames into the pending episode. Unsaved frames remain available for saving after
reconnect, and normal server shutdown attempts to save them. Forced termination
can lose unsaved frames. A write error retains the buffer for retry while running.
The default 30,000-frame limit automatically saves and stops recording.

Mocap interaction is provided by Vuer. For pinch control, supply named actuators
from `view_scene --describe` with `--right-actuator NAME` and/or
`--left-actuator NAME`. The mapping clamps to that actuator's native ctrl range;
it maps roughly 10 cm finger separation to the lower limit and 1.7 cm to the upper
limit while squeezing. No last-actuator assumption is used. Leave these options
out for hand assemblies or scenes whose controls are handled directly by Vuer.

`--seed` controls scene construction; `--scene-options '{"name": value}'` forwards
explicit scene options. `--fps` requests the browser's frame emission rate, not a
physics timestep. `--assets` selects a relocated asset tree. Browser MuJoCo and
native MuJoCo may differ in version/features; recordings identify their browser
source without claiming identical integration behavior.

Vuer remains an optional visualization dependency. Its upstream transitive
packages are confined to `teleop`; these scripts do not use params-proto,
ml-logger, jaynes or zaku directly.

## Playback and inspection

```bash
uv run python -m lucidxr.scripts.playback_demo /path/to/demo.npz --headless
uv run mjpython -m lucidxr.scripts.playback_demo /path/to/demo.npz --speed 1
uv run mjpython -m lucidxr.scripts.view_scene pick_block
```

On macOS, use `mjpython` for native viewer windows. On Linux, ordinary Python works
with a suitable display. Playback validates the recording and restores frames
without stepping physics or episode rules. Timing follows recorded server receive
intervals, scaled by `--speed`. `--headless` validates all frames without waiting or
opening graphics. `--assets` can point to the same asset content in a different
location. A changed scene XML or asset file fails the fingerprint check; use the
matching source/assets rather than silently changing the recorded scene.

## Recording format

Each accepted episode is one unique `.npz`, published atomically after writing and
flushing a temporary file on the same filesystem. Publication uses an exclusive
hard link, so it cannot overwrite an existing recording. Storage must support
hard links; a failure is reported and the episode stays buffered. Atomic local
publication does not guarantee Dropbox upload or remote backup completion.

The NPZ contains:

- `metadata`: JSON with format version, scene name/options/seed, reference MuJoCo
  version, source, field shapes and a SHA256 fingerprint of XML plus asset content.
- `elapsed`: increasing server receive timestamps, relative to the first frame.
- `qpos`, `qvel`, `act`, `ctrl`, `mocap_pos`, `mocap_quat`: float64 arrays with a
  leading frame dimension, including empty dimensions where appropriate.

There is no pickle, Python object deserialization, policy encoding or training
batch format. ctrl and mocap are commands present at each captured state; they are
not automatically shifted into action labels. Browser frame emission may skip
physics steps. A later training adapter must choose alignment/resampling explicitly.
Derived observations and camera images can be regenerated during playback instead
of being duplicated in every file. Runtime visual randomization is not captured
by this version; the recorder uses the unwrapped scene without randomizers.

`lucidxr.sim.demos` owns this format and `lucidxr.sim.teleop` owns browser collection.
Only record_demo, playback_demo and view_scene are ported. The old scratch render,
file-renaming, upload and asset-conversion scripts are intentionally left deprecated.

Validation covers file round trips, failed-save retention, scene mismatch rejection,
standalone bundle compilation, and a live Vuer WebSocket event-to-file-to-playback
smoke. A browser/headset was unavailable for interactive visual validation; hand
tracking, button interaction and browser-side physics remain to be checked there.
The adapter uses the installed Vuer 0.1.6 API and follows its
[MuJoCo interaction examples](https://github.com/vuer-ai/vuer/blob/main/docs/tutorials/mujoco_interactive_simulator.md).

Offline replay rendering: `python -m lucidxr.scripts.render_demo DEMO --output DIR
--cameras wrist`. Install the `rendering` extra. See
[rendering](../rendering/README.md) for paired HDF5/video output and completion records.

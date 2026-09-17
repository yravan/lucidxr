# Recording and rendering design

Rendering is implemented before training in three stacked PRs: local replay (#5),
Jaynes/MIT execution (#6), and scratch/publication recovery (#7). The current
product is a replay result: one HDF5 file and one MP4 per camera. Dataset export,
models, policies and dataloaders remain separate work.

## Ownership

| Module | Responsibility |
| --- | --- |
| `lucidxr.sim` | Scene construction, native controls, recordings, shared playback, camera capture |
| `lucidxr.rendering` | Render identity, plans, streaming output, format validation and completion records |
| `infra` | Personal paths, MIT resources, captured source, SSH/Slurm, scratch placement and recovery |
| `lucidxr.scripts` | Parse arguments and connect these boundaries once |

Core simulation and rendering accept paths without importing personal configuration.
Future training scripts can resolve dataset/checkpoint roots through the same infra
configuration; infra does not own action representations, model sizes or learning
rates. There are no credentials or implicit cluster paths in scene definitions.

## Recording and playback contract

New NPZ recordings contain named physical arrays, simulation timestamps, scene and
asset fingerprints, and named control metadata. The pinned Vuer client samples a
clock sensor before its final integration step; collection accounts for that phase
when saving the state timestamp. Browser engine and native reference versions are
recorded separately. See [collection details](../scripts/README.md#browser-clock).
Old recordings are unsupported.

State playback restores each recorded state in its original fingerprinted scene.
Command playback applies sample i's mocap/ctrl over the interval ending at i.
Same-scene playback starts from recorded state 0; an explicit target scene starts
from its own reset and maps compatible named controls. Mocap coordinates remain
world-space. Replay integrates an integer number of target physics steps per
recorded interval. Display speed and MP4 fps do not determine physics timing.

The viewer and renderer share this implementation. Rendered frames are paired with
the actual target states, controls and calibration. Command playback produces new
physics; it does not promise identical outcomes across different engine versions or hardware.

## Explicit work and publication

A work identity hashes the recording content, replay/camera settings, target scene
fingerprint, and simulator/renderer code and package versions. Paths locate files;
they never encode task, camera, split or variant semantics. A plan lists work IDs
and explicit input references and deduplicates identical requests.

Each worker processes a deterministic partition. An attempt owns its HDF5 writer,
video encoders and MuJoCo context; workers never append to one shared HDF5 file.
Outputs close and are validated by decoding videos and checking frame counts,
timestamps and metadata. Artifact hashes and relative references are published in
an immutable completion record. Competing attempts accept the first valid record.
A collection is published only after every requested result verifies successfully.

On MIT, each recording is copied and verified on node-local scratch. Closed local
results transfer to a new shared attempt and are verified before the shared
completion record appears. Failed transfers cannot advertise partial success.
Successful owned scratch is removed; failure diagnostics remain while the node
permits. Durable retry uses the captured bundle, never temporary scratch survival.

## Launch and recovery

Jaynes supplies code mounts, SSH and Slurm scripts. We freeze a Git tree, package it
with explicit inputs, verify the uploaded archive, and run uv from the captured
lockfile. No remote checkout or persistent scheduling service is needed. A bounded
set of GPU jobs processes the plan; the scheduler owns allocation and termination.
Worker errors propagate to Slurm and ordinary logs.

Local receipts retain tree/archive/script hashes, remote paths and accepted IDs.
A remote per-worker claim prevents duplicate submissions. `infra reconcile` can
recover saved IDs after a lost acknowledgement and establish which workers were
never submitted. A claim without an ID is ambiguous and requires inspection.
`infra resume` finishes a reconciled partial submission or retries a fully terminal
run using its original scripts. Verified completed work is skipped. See the
[operating instructions](../../infra/README.md#scratch-and-retry-recovery).

## Validation and current limits

Focused checks cover clock sampling, state/command playback, compatible scene
transfer, source identity, HDF5/video correspondence, interrupted publication,
lost submission acknowledgements, duplicate claims and Slurm failure propagation.
Real Engaging GPU runs exercise staging, EGL rendering, cancellation and retry;
[verification notes](VERIFICATION.md) record the tested boundaries.

The distributed backend is native MuJoCo/EGL. Existing gsplat and Lucid wrappers
are not exposed as distributed render backends. Visual randomization, finalized
dataset export, an asset cache and sustained GPU-utilization optimization remain
future work. Assets currently travel with each new source snapshot; resume reuses
that upload. Retry operates per episode, not per frame. Headset interaction still
needs hardware validation.

## Training follows

Build model, policy and dataloader code as separate stages after this workflow.
Training will consume explicit metadata and frame indices without interpreting
folder names. The deferred [policy research](https://github.com/yravan/lucidxr/pull/4)
covers diffusion, flow matching and a language-free MoT design; no training runtime
or W&B artifact store is added here.

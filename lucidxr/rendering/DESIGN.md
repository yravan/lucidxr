# Rendering before training

Status: the implementation follows three stacked slices: local replay (#5),
Jaynes/MIT execution (#6), and scratch/recovery. PR #4 retains deferred policy
research. The original plan below is retained with these scope decisions:

- HDF5 plus paired MP4 is the current replay format. Dataset export and the
  Parquet/history-window benchmark are deferred at the user's request.
- Native MuJoCo/EGL is exercised locally and on Engaging GPUs. The distributed
  path does not yet expose gsplat, Lucid generation or randomized visual variants.
- Jaynes submits a bounded set of independent Slurm workers, each handling a
  deterministic partition. There is no job array or second scheduling service.
- Resume reuses uploaded source/assets and inputs. Per-item input/output work uses
  node-local scratch; assets remain in the shared source snapshot. A separate
  asset cache and sustained GPU-utilization benchmarks remain future work.
- Job failures are visible through durable worker logs and Slurm state. Accepted
  completion records are authoritative; ambiguous submissions require inspection.

See [README.md](README.md) and [infra](../../infra/README.md) for the implemented
commands and storage contract. A/B/C below describe the original sequencing.

## Ownership

- `lucidxr.sim`: scenes, environments and reusable rendering/randomization wrappers.
- `lucidxr.rendering`: replay, camera products, episode/variant jobs, export schema,
  writers, validation and completed dataset manifests.
- `infra`: shared deployment setup, storage roots, scratch, MIT cluster resources,
  job submission and explicit staging. Build each operation with its first caller.
- `lucidxr.scripts`: thin launch entry points that resolve infra configuration once.
- `training`: later, models, policies, read-only window loading and optimization.

Rendering must work without the training package. Training will reuse the same
infra configuration for dataset roots, scratch and run/checkpoint locations.
Infrastructure owns deployment settings, not camera conventions, action schemas,
model dimensions or learning rates. Pass resolved settings explicitly; avoid
import-time configuration, per-frame path resolution and mutable global constants.
No hardcoded hosts, credentials or assumption that old CSAIL machines are reachable.

## PR A: one reliable local rendering/export path

Deliver one CLI that renders an existing demo into a validated, inspectable output.

- Reconstruct and fingerprint the scene/assets, compile once per episode/variant,
  restore recorded states without stepping physics, and capture named cameras.
- Reuse existing native, gsplat and Lucid-conditioning wrapper contracts. Start with
  an exercised native backend; validate optional GPU backends in the later MIT run.
  Lucid conditioning does not imply an implemented generative model.
- Preserve source IDs, frame indices, timestamps, calibration, render settings,
  backend versions and seeds. Appearance variants preserve the physical trajectory.
- Decide the export format here: compare Parquet + per-camera MP4 against the earlier
  HDF5 proposal using representative history-window reads, storage size and encode/
  decode cost. Prefer explicit typed tables to a pickled dataframe. Video requires
  exact frame mapping and deliberate keyframe spacing; depth/segmentation require
  lossless typed products. Implement one format, not a cache/backend framework.
- Keep raw demos immutable. Write into a temporary output, validate, then publish
  an immutable episode/variant result and a completion record.
- Resolve input/output roots through existing infra configuration at the CLI.
  Keep direct explicit paths available for local use and record resolved settings.

Acceptance: render/reload a short real demo, verify frame/calibration correspondence,
exercise a failed write, and confirm rerunning does not overwrite a valid result.
New recordings capture simulation time through a clock sensor and declare that
command i drives the interval ending at frame i. Viewer and renderer share state
and command playback. Training remains deferred; old recordings are unsupported.

## PR B: distributed rendering on MIT

Deliver an inspectable job manifest plus a worker command and MIT scheduler launcher.
Inspect the available scheduler, GPU environment and filesystem before implementing
its adapter. If the selected cluster exposes Slurm, use job arrays; do not build a
second scheduling service or a generic scheduler plugin registry.

- A work unit is a source episode plus visual variant, not an individual frame.
  Stable work IDs include input content hashes, settings and render version.
- Partition the manifest deterministically among workers. Each worker creates its
  own GPU/context resources after startup and reuses expensive backend/checkpoint
  state when compatible. Do not fork live GPU contexts or oversubscribe devices.
- Infra supplies resource requests, environment setup and submission; rendering
  owns the work specification and worker execution. Use the same worker locally.
- Produce per-work structured status/errors and ordinary stdout/stderr logs.
  Commands and manifests are saved and can be rerun without a service connection.
- Give each attempt a unique output location. A coordinator accepts one validated
  result per work ID; retries never race to append to a shared dataset file.
- Publish a dataset manifest only after the requested work set is complete and
  validated. Failed work remains explicit; do not silently train on partial output.

Acceptance: a small actual multi-worker MIT run, deterministic work assignment,
matching local/distributed results within the backend's documented tolerance,
visible failure reporting and targeted retry. Report unavailable CUDA/backend
validation explicitly instead of substituting a mock for a cluster result.

## PR C: staging, recovery and operational use

Deliver a repeatable cluster workflow that survives interruption and avoids repeated
large transfers. This is where infra grows beyond location resolution.

- Stage declared immutable inputs to node-local scratch, verify hashes, and reuse
  matching copies. Keep dataset/export semantics in rendering, transfer mechanics
  in infra. No downloading or staging from inside a render loop or DataLoader.
- Render locally, then transfer each complete result into a unique durable attempt
  directory and validate it there before accepting it. A local rename does not
  prove a cross-filesystem or remote transfer completed.
- Resume from accepted completion records; retry missing/failed work without
  rerendering accepted outputs. Detect stale settings via work fingerprints.
- Handle preemption and disk-full failures without advertising partial files as
  complete. Cleanup only owned scratch after verified publication; retain useful
  failed-attempt logs and diagnostics.
- Add only the storage path exercised by the first MIT workflow. Dropbox is optional
  explicit export/sync, not a concurrent job database; no W&B Artifacts.
- Measure frames/second, transfer time, storage size and GPU utilization so later
  changes address the actual bottleneck.

Acceptance: interrupt/resume a small run, inject a staging/publication failure,
verify no missing/duplicate accepted work, and consume the final manifest from a
second process using only the documented storage setup.

## Then training

Proceed in separate stages: model code, policy code, dataloader code, then their
first integrated trainer. Diffusion Policy first; flow matching shares its network;
language-free MoT follows with the same data contract. Preserve the research in
[policy design PR](https://github.com/yravan/lucidxr/pull/4), updating it to the actual export contract.
Do not create unused modules or train against guessed command timing in the meantime.

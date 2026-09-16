# Recording, preparation, rendering and loading

Status: proposed boundaries and data contract, not an implemented dataset pipeline.

## Why restart this part

The old `learning/episode_datasets.py` and `episode_datasets_new.py` combine remote
ML_Logger reads, scratch copies, video decoding, Zarr cache creation, cache pruning,
locks, action shifts, coordinate conversions and PyTorch sampling. `load_chunk`
selects commands starting at `1 + relative_idx`, making label timing an implicit
loader behavior. The render worker similarly mixes frame restoration, labels,
PNG/video/HDF5 output, logging and Zaku jobs for generative rendering.

Preserve the useful workflows, not those boundaries. The read path must not repair,
render, download or mutate a dataset as a side effect of fetching a batch.

## Three representations, each with a purpose

| Representation | Owner | Purpose |
| --- | --- | --- |
| Raw demo | `lucidxr.sim.demos` | Preserve captured physical state and provenance |
| Prepared episode | `training.data` | Explicit aligned labels, selected observations and images |
| Policy batch | `training.policy` contract | History/chunk tensors for loss or sampling |

Raw recordings remain immutable. Rebuilding rendered observations never edits the
source demo. Preparation records its version, options and source hashes. Training
reads a completed dataset manifest, not a directory that another process is still
populating. Policy action encoding and normalization do not change the raw data.

## Timing is the first implementation dependency

PR #3 records state and the commands present in each emitted browser frame, with
server receive timestamps. It does not record exactly which command was selected
from which pre-step observation, a simulator clock, or every physics/control step.
Receiving at 50 Hz is not proof of an exact 50 Hz control trajectory. Adding one to
an index cannot recover that information.

For authoritative behavior-cloning targets, collection needs an explicit transition:

```text
observation/state s[k] at simulator time t[k]
command u[k] chosen using information available through t[k]
apply u[k] for the declared control interval
next observation/state s[k+1] at t[k+1]
```

The first data implementation must establish this boundary in the collection path
and save simulator timestamps, control commands, sequence numbers and reset
boundaries. Prefer an explicit before-step/after-step event contract in the Vuer
integration; if the browser API cannot provide it, use native stepping driven by
Vuer control inputs. Inspect the actual browser event implementation before
choosing. This is a concrete follow-up to PR #3, not a promised field already
present in its recordings.

Existing frame-only recordings still support rendering and playback. A legacy
import may explicitly request a heuristic such as “next recorded command”, but
must preserve that choice, measured receive intervals and its approximate status
in the manifest. It must not silently label the output as synchronized transitions.
Default training preparation rejects ambiguous timing. Synthetic/native rollouts
with known transition ordering provide the initial integration fixture while the
browser contract is validated.

Choose a declared control period before preparing data. For authoritative logs,
select compatible control boundaries and preserve held commands. Do not interpolate
through resets, missing spans or discontinuous contact trajectories. Reject or
split excessive gaps using a recorded threshold. Images and state must refer to
the same selected boundary; selecting a future frame for a past observation is
not an acceptable resampling shortcut.

## Prepared storage: one HDF5 file per episode/visual variant

Use one format initially. HDF5 gives named, typed, sliceable and chunked arrays in
one file; it avoids both decompressing an entire NPZ for every window and creating
one filesystem entry per image/chunk. This is a design choice for current
filesystem-based workstation/cluster access, not a claim that HDF5 is universally
faster than Zarr or video storage. Benchmark the actual training read pattern
before changing the format.
[HDF5 dataset slicing and chunking](https://docs.h5py.org/en/stable/high/dataset.html)

```text
dataset/
  manifest.json
  episodes/
    <source-id>.<variant-id>.h5
```

For N control intervals, the episode contains:

| Entry | Shape | Meaning |
| --- | --- | --- |
| time | [N+1] | Simulator boundary timestamps |
| observation/state | [N+1, S] | Explicit measured robot features |
| observation/images/<camera> | [N+1, height, width, 3] | RGB uint8 at each boundary |
| command/ctrl | [N, nu] | Native actuator targets for the following interval |
| command/mocap_pos | [N, nmocap, 3] | World-space targets |
| command/mocap_quat | [N, nmocap, 4] | wxyz targets |
| calibration/<camera>/K,C2W | [N+1, ...] | Calibration for rendered images |
| source_frame | [N+1] | Mapping back to the source recording |

Store physical command fields, not a single unexplained 10D column. The same
ActionCodec encodes these fields for all policies and decodes sampled vectors at
inference. Optional render products are only written when the preparation job
actually requests them. Zero-mocap models do not require fabricated pose channels.

The file metadata and manifest bind scene/assets, source recording hash, control
period, observation/action specifications, preparation version and rendering
configuration. Visual variants also identify renderer/backend version, seed, and
any splat checkpoint/alignment content hashes. Relative file paths make the dataset
relocatable. A preparation fingerprint prevents accidental mixing of incompatible
files. A completed manifest is published only after its files validate.

One worker writes each new episode file to a temporary path, then publishes it
without replacing an existing completed episode. No concurrent appenders, SWMR,
MPI-HDF5, or loader-side cache construction. On reading, each DataLoader process
opens its own HDF5 handles lazily and keeps a small bounded handle cache; never
fork with open handles inherited from the parent.
[h5py process guidance](https://docs.h5py.org/en/stable/mpi.html)

Chunk images by a small number of adjacent frames and store uint8 on disk. Pick
chunk length/compression by measuring O-frame reads and CPU decompression cost.
Do not bake a giant all-episode memory cache into Dataset. Completed files may be
staged onto node-local scratch by infra once an actual cluster workflow needs it;
that is an explicit operation before DataLoader construction.

## Rendering stays with simulation

`lucidxr.sim.render_demo` should own frame restoration, CameraWrapper and optional
visual wrappers. A thin `lucidxr/scripts/prepare_dataset.py` composes it with the
prepared-episode writer. `training.data` owns the file schema, window sampling and
stats; its Dataset never imports MuJoCo, Vuer or gsplat.

For each source episode and visual variant:

1. Validate scene/assets and the alignment plan.
2. Compile one environment. Seed and sample appearance once for that variant.
3. Restore each selected boundary state; do not advance physics.
4. Capture the requested cameras/products and their actual calibration.
5. Write images, measured observations and commands with identical source indices.

Start with episode-constant visual randomization, not untracked per-frame texture
flicker. Rendering must preserve the physical trajectory and command labels.
Randomizing object poses, geometry or dynamics is not an appearance augmentation.
The existing randomization wrappers are reused rather than reimplemented in a
training transform. Native, splat and Lucid-conditioning outputs share the same
frame/calibration contract; their creation remains outside the training loop.

Lucid conditioning is not generative inference. A future image-generation stage
must consume its explicit conditioning/masks and publish a derived visual variant
with model/seed provenance. Do not revive a Zaku queue or assume a generator exists
merely because LucidWrapper exists.

GPU/offscreen contexts are created inside rendering workers, not inherited through
fork. Begin with a single-process preparer; add process-level episode parallelism
when preparation measurements justify it. Splat checkpoint loading is reused across
episodes handled by a worker. No rendering service or scheduler is needed to define
this API.

## Window sampling and splits

The manifest defines source groups and train/validation/test membership. Group
visual variants of the same physical trajectory together, and group episodes from
the same collection session where they are correlated. Split before creating
variants or fitting normalization. Never randomly split individual frames; that
would leak adjacent observations and re-rendered copies across evaluation splits.
PR #3 has no explicit collection-session ID, so the first preparer must require a
source grouping map rather than infer independence from unique filenames.

At anchor t, sample O observations ending at t and H command targets beginning at
t. History before the episode start repeats the first observation and sets
obs.valid=False. Targets after the final control interval repeat the final command
for numerical padding and set action_valid=False. A window never crosses an episode
boundary. H padding must not contribute to the target loss or normalization stats.

Choose an anchor on the source trajectory, then one visual variant for the entire
window. All cameras/history steps come from that variant. More renders of one
trajectory must not implicitly give it more training weight. A sampler can emit
(source, anchor, variant) indices, with a recorded epoch/seed; Dataset remains a
read-only function of that index. Start uniform over valid source-frame anchors
and state that choice; episode-uniform sampling would weight trajectories differently.

CPU workers read image/state windows and construct tensors. Transfer uint8 RGB to
the device once, then scale and augment. Sample image augmentation coherently across
history; crop geometry must be consistent wherever calibration/depth are consumed.
Validation uses deterministic preprocessing, no random crop/color jitter. Do not
reuse the old trainer's training augmentations for validation.

## Data gates before a training result is meaningful

- Known transition fixture: observation at k supervises command k, including reset
  boundaries, first/last windows, nonuniform timestamps and missing spans.
- Recorded/replayed physical state agrees; camera calibration and source frame IDs
  stay aligned through visual variants.
- Same source/session never enters both train and validation, regardless of variant.
- Train-only normalization and action-codec round trips agree in preparation and
  rollout; no privileged object state enters the selected proprioception vector.
- Repeated Dataset reads perform no network requests or file writes and do not leak
  open handles. Native and multi-worker reads return the same indexed window.

These checks target failure modes that can invalidate training while losses appear
to improve. They matter more than carrying over every legacy augmentation flag.

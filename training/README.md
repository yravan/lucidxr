# Training

The training package is independent of deployment configuration. Its core modules
accept tensors and paths; scripts resolve personal locations and MIT resources
through `infra`. No language inputs or pretrained language/vision weights are used.

Implementation is stacked after rendering PR #7, in four reviewable slices:
models, policies, data, then the trainer and MIT integration.

The completion criteria are working training and sampling for all three policies,
timing-correct data windows with group-isolated splits, measured loader throughput,
reproducible checkpoint resume, a decoded simulation rollout, and a real MIT GPU
run using the same training entry point. CPU checks do not establish GPU performance.

## Models

`ModelSpec` fixes camera order, observation history, action horizon and tensor sizes.
`UNet` and `MoT` have the same tensor interface:

```python
from training.models import ModelSpec, UNet

model = UNet(ModelSpec(state_dim=25, action_dim=10))
condition = model.condition(images, state, observation_valid)
prediction = model.predict(noisy_actions, time, condition, action_valid)
```

Images are uint8 `[B,O,V,3,H,W]`; state is float `[B,O,S]`; actions and predictions
are `[B,H,A]`. Masks are boolean, with True meaning valid. Time is continuous in
`[0,1]`; the policy objective defines its interpretation. No file, network, simulator
or scheduler operation occurs in these modules.

Both networks use a randomly initialized torchvision ResNet-18 with GroupNorm,
shared across cameras and history. The U-Net conditions temporal residual blocks
with FiLM, retaining explicit camera/history order in its global condition. MoT
projects visual cells and measured state into observation tokens with explicit
spatial, camera, history and modality identity. Its observation and action experts
have separate normalization, projections and feed-forward parameters. Action
queries attend jointly to observation and action K/V. Observation queries cannot
attend to actions; action tokens attend bidirectionally within their valid chunk.

MoT's action layers use time-conditioned adaptive RMSNorm. Its observation K/V
is computed once per decision and reused over all flow steps. The same cache keeps
its autograd graph during training. The final observation-layer output has no
consumer in an action-only objective, so it does not allocate unused query/output
or feed-forward parameters. `forward` supplies an independent joint-attention
reference for checking cache equivalence.

This is a compact, language-free MoT inspired by π0.5, not an implementation of
its full VLM, pretraining, knowledge-insulation losses or checkpoint format. Learned
positions and a shared ResNet trunk are deliberate differences. It uses no routing,
tokenizer, vocabulary, text input or weight download.

Install `uv sync --extra training` for model work; `uv run pytest -q training/tests`
checks forward/backward behavior, prefix gradients, mask isolation and cached/joint
attention agreement. CUDA performance and integrated training are verified in the
later runtime slice, not inferred from CPU model checks.

References reviewed at the same commits as the earlier design PR #4:

- [Diffusion Policy](https://diffusion-policy.cs.columbia.edu/) and its
  [conditional U-Net](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/model/diffusion/conditional_unet1d.py).
- [OpenPI flow objective/cache](https://github.com/Physical-Intelligence/openpi/blob/215abfb217dbac7d5f1273282331b9b1866c0479/src/openpi/models/pi0.py)
  and [expert attention](https://github.com/Physical-Intelligence/openpi/blob/215abfb217dbac7d5f1273282331b9b1866c0479/src/openpi/models/gemma.py).

## Policies

`ChunkPolicy(PolicySpec(kind, model))` supports `diffusion`, `flow` and `mot`.
Diffusion and flow use the same U-Net. Diffusion trains epsilon prediction with
a cosine DDPM schedule and samples with deterministic DDIM; flow and MoT regress
noise minus data along a straight interpolation and use backward Euler sampling
from t=1 (noise) to t=0 (data). The inference step count is explicit.

`policy.loss(batch)` returns a differentiable `loss`; `policy.sample(obs)` returns
physical encoded action chunks. The observation dictionary has `images`, `state`
and boolean `valid` entries. A training batch adds `actions` and `action_valid`;
padded targets do not contribute to the loss. Vision and the observation condition
are evaluated once per sampling call, independent of the denoising step count.

`ActionCodec` owns the policy representation: native actuator controls followed
by world position and two rotation-matrix columns for each named mocap body.
Decoding produces the simulator's native dictionary, bounds actuator controls to
model limits, and orthogonalizes rotations with finite, deterministic fallbacks.
Neither action chunks nor 6D rotations change the environment API.

The normalizer is part of the policy state dict. Its bounds must come only from
training data. Constant channels retain unit scale; action rotation channels keep
their known [-1,1] domain. Observations and generated actions are not clipped to
training extrema. The focused policy checks cover native rotation round trips,
the flow integration direction, tiny-batch learning by all three policies,
seeded sampling, and one vision evaluation per sampled chunk.

## Data

HDF5 and paired MP4 remain the render output. Training uses an explicit derived
cache: uint8, resized RGB plus float32 robot state and actions in read-only NumPy
maps. Preparation verifies completion records, artifact hashes, scene/assets,
control meaning, video counts and simulation timing. It decodes each video once;
workers never decode video, compile scenes, write files, or access the network.
This is a training accelerator, not a new dataset export format.

Write a JSON recipe with explicit source/session groups and splits:

```json
{
  "data": {
    "cameras": ["wrist"],
    "joints": ["gripper-float-floating-base", "gripper-right_driver_joint", "gripper-left_driver_joint"],
    "control_period": 0.02,
    "image_size": 128
  },
  "episodes": [
    {"result": "renders/results/RENDER_ID.json", "group": "collection-session-1", "split": "train"},
    {"result": "renders/results/OTHER_RENDER_ID.json", "group": "collection-session-2", "split": "validation"}
  ]
}
```

Paths resolve relative to the recipe. Group identity is supplied by the collector;
neither directory names nor frame-level random splitting infer it. All visual
variants of a source recording must have the same group and split. Select measured
robot joints explicitly: object state is never silently included. Joint names and
types, native controls, camera order and original render resolution become part of
the portable contract. Rollout must render at that resolution before applying the
same resize; rendering directly at a square resolution changes the camera geometry.

```sh
uv run --extra training python -m training.scripts.prepare recipe.json --output /data/cache/run-1
uv run --extra training python -m training.scripts.benchmark /data/cache/run-1 --workers 2
```

`--location NAME --infra-config FILE` can replace `--output` at the script boundary.
Core preparation/loaders accept paths and have no dependency on personal infra.
Use a new output destination when preparing a changed recipe. Only a completely
validated directory is published; a manifest binds array hashes to the data contract.
The caller verifies hashes once before training, not repeatedly in each worker.

An observation ending at frame t targets the command at source frame t+1. The
declared control period must match every simulation interval; display FPS is never
used for labels. Earlier history repeats the initial frame with an invalid mask;
future padding repeats the last target with an invalid mask. Statistics use only
real training observations and commands. Sampling is uniform over physical anchors,
then uniform over their visual variants, so extra renders do not change a source's
weight. Deterministic batch IDs use the consumed step, allowing resume despite
DataLoader prefetch. Each process has its own bounded read-only map cache.

Measured on the development Mac using the 1,500-frame MIT render, two-frame RGB
windows and 128×128 training images: random MP4 seeking/resizing averaged 5.07 ms
per window versus 0.008 ms from a warm NumPy map. Preparing RGB took 1.29 seconds;
storage grew from 1.34 MB MP4 to 73.7 MB decoded RGB. The complete loader, including
collation at batch size 32, reached 46.6k windows/s with zero workers and 65.8k with
two; median batch waits were 0.67 and 0.47 ms respectively. These are warm-cache
measurements on a small smoke recording, not cold shared-storage or GPU throughput.

## Training and resume

Copy `training/configs/default.toml`, choose the policy and resource sizes, then run:

```sh
uv run --extra training python -m training.scripts.train config.toml \
  --data /data/cache/run-1 --output /data/training/run-1 --wandb offline
uv run --extra training python -m training.scripts.train config.toml \
  --data /data/cache/run-1 --output /data/training/run-1 --resume --wandb offline
```

The same trainer handles all three policies. It uses AdamW, a warmup/cosine learning
rate, gradient clipping and an EMA whose decay warms up toward the configured
maximum. Camera/image/state/action dimensions come from the verified cache, not
duplicated config. `width` sizes both architectures; `depth` and `heads` configure
MoT. Unknown TOML keys fail instead of being ignored. CUDA uses fused AdamW and BF16
autocast when supported, otherwise FP32. Images remain uint8 through pinned-memory
transfer and are normalized on the device. CPU mode is for local functional checks.

Every run records resolved config, data/code identity and hardware in `run.json`.
`metrics.jsonl` always records loss, learning rate, gradient norm, batch wait,
throughput and validation loss when a held-out split exists. CUDA runs also report
peak allocated GPU memory. These are measured interval metrics, not benchmark
guarantees. `--wandb offline` stores scalar metrics for later sync; `online` uses
existing W&B authentication. W&B failure falls back to JSONL. Each resumed process
is a new W&B attempt grouped under the durable run ID, so prefetched or rolled-back
steps cannot silently replace checkpoint state. No datasets or checkpoints are
uploaded as W&B Artifacts, and no model/code watching is enabled.

`last.pt` is atomically replaced after a complete write. It contains policy and EMA
state dicts, optimizer state, normalization, RNG state, consumed step, representation
contract and identities. A failed write preserves the previous checkpoint. Resume
requires matching config, prepared data, implementation/dependency versions and
precision. The next batches and objective noise resume at the consumed step even
when workers had prefetched future batches. A file lock prevents concurrent writers.
There is no AMP scaler state for BF16 or FP32. Reproducibility is checked exactly on
CPU; identical results across different GPU hardware are not promised.

SIGINT, SIGTERM and SIGUSR1 request a checkpoint after the current update. The
trainer records `interrupted` or `complete` in `status.json`; successful process
exit alone does not imply all configured steps completed. Hard kills resume from
the last periodic checkpoint. A run with an incompatible identity fails clearly;
it does not quietly start over, alter its split, or overwrite an unrelated run.

## Policy rollout

```sh
uv run --extra training python -m training.scripts.rollout /data/training/run-1/last.pt \
  --scene pick_sphere --seed 9 --steps 100 --execute-steps 4 --video rollout.mp4
```

The controller loads EMA weights and the saved representation, verifies joint and
control semantics, and executes the first K actions of each predicted chunk. It
collects observations at every control interval, including while executing a chunk,
so history spacing matches training. Reset clears both history and pending actions.
Camera captures and resizing match preparation. Missing cameras, incompatible
controls/timing, nonfinite commands and unstable physics fail explicitly. Generated
positions are not silently workspace-clipped. Video captures are reused with the
environment's existing render cache and flushed even if rollout fails.

The CLI reports execution length, reward, termination, command norm and inference
latency. `success` is null because the base environment defines no task-success
criterion. Static/programmatic smoke data checks execution, not learned manipulation
quality; low denoising loss alone does not establish stable closed-loop behavior.

## MIT launch

```sh
uv sync --extra training --extra launch
uv run python -m training.scripts.launch config.toml --data /data/cache/run-1 \
  --cluster engaging --infra-config ~/.config/lucidxr/infra.toml --dry-run
# After inspecting the generated receipt/script, omit --dry-run to submit.
```

Infra owns the SSH alias, allocation, shared storage and scratch. The launcher
requires a CUDA config whose worker/thread counts fit the CPU allocation. It
transfers a cache separately from code, verifies hashes before publishing its
content-addressed location, and reuses that location on subsequent launches.
Only manifest-listed files transfer. The same Jaynes code snapshot, locked uv
environment, saved scripts and submission-recovery protocol serve rendering and
training. The receipt stores the actual entry point and arguments, including the
result path; no directory name is needed to interpret a run.

The cluster worker stages the cache onto node scratch and calls the ordinary
trainer. Insufficient scratch produces a logged fallback to verified shared files;
corruption is an error. The trainer performs the full integrity check before any
batch is consumed. Checkpoints and metrics stay on shared storage. Slurm sends a
warning 60 seconds before timeout; the batch shell is replaced by Python so the
signal reaches the checkpoint handler. Retry with `python -m infra resume RECEIPT`
after accounting confirms the prior jobs are terminal. Uncertain submissions must
first be reconciled with `python -m infra reconcile RECEIPT`.

Use [the verification record](VERIFICATION.md) to distinguish local checks from
cluster execution and policy quality. GPU verification requires an authenticated
Engaging SSH connection; a dry run only checks source capture and generated scripts.

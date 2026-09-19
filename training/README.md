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

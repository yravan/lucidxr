# Policy design

Status: proposed implementation contract. Research reviewed 2026-09-16.

## What the references establish

Diffusion Policy supports conditional temporal U-Nets and transformers, visual
conditioning and receding-horizon action execution. Its official image U-Net
implementation predicts Gaussian noise and uses a diffusion scheduler for sampling.
Our initial “standard DP” means this U-Net/DDPM formulation, not checkpoint
compatibility or an exact reproduction of every published benchmark configuration.
[Project and paper](https://diffusion-policy.cs.columbia.edu/)
[Official image policy](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/policy/diffusion_unet_image_policy.py)

Flow matching regresses a velocity field along a chosen conditional path; it is
an objective, not a prescribed policy architecture. We use independent Gaussian
noise/data pairs and a straight path. This does not require optimal-transport
assignment, reflow, distillation, or a generic differential-equation package.
[Flow Matching paper](https://arxiv.org/abs/2210.02747)
[Authors' guide](https://arxiv.org/abs/2412.06264)

π0.5 is a larger system incorporating language, pretrained vision-language
representations, heterogeneous training data and high-level reasoning. Removing
those parts changes the model being studied. We retain the useful observation /
action-expert structure and continuous flow head, with explicit deviations below.
[π0.5 paper](https://arxiv.org/html/2504.16054v1)
[Official release](https://www.pi.website/blog/pi05)

OpenPI's released pi05 configuration uses discretized robot state in the tokenized
prompt and adaptive RMS normalization for action-expert time conditioning. Simply
removing its prompt would also remove the intended state input. We instead project
continuous proprioception into observation tokens. No tokenizer, vocabulary,
language loss, language weights or generated subtask is present.
[Configuration](https://github.com/Physical-Intelligence/openpi/blob/215abfb217dbac7d5f1273282331b9b1866c0479/src/openpi/models/pi0_config.py)
[State tokenization](https://github.com/Physical-Intelligence/openpi/blob/215abfb217dbac7d5f1273282331b9b1866c0479/src/openpi/models/tokenizer.py)

## One public contract

All policies expose two operations:

```text
loss(batch, generator) -> {loss: scalar tensor, detached metrics...}
sample(observation, generator, num_steps) -> action_chunk [B, H, A]
```

`loss` is differentiable; `sample` is inference-only. Modules own neural parameters
and normalization buffers. The trainer owns optimizer, EMA, device placement,
logging and checkpoints. Models never create an environment, read a dataset,
resolve a path or contact a service.

The batch uses the same schema for all policies:

| Field | Shape/type | Meaning |
| --- | --- | --- |
| obs.images[name] | uint8 [B, O, 3, height, width] | Named RGB camera history |
| obs.state | float32 [B, O, S] | Selected, measured proprioception in physical units |
| obs.valid | bool [B, O] | Real versus repeated history at episode start |
| actions | float32 [B, H, A] | Encoded, unnormalized command targets |
| action_valid | bool [B, H] | Real versus padded future targets |

Camera names/order, state field order, action layout and control period are fixed
by the checkpoint's specification. No variable robot morphology or missing-camera
machinery in the first version. Reject incompatible episodes before training.
The initial modality is RGB plus proprioception. Existing depth/mask render
products remain available for later experiments without widening this interface now.

Prediction starts at the current control decision: targets are `a[t:t+H]`,
conditioned on observations through `t`. History is `o[t-O+1:t+1]`. Execute the
first K predicted commands, then observe and replan. No past action targets are
included in the public chunk. The upstream DP window convention includes an
observation-history offset when slicing actions; our adapter must deliberately
translate that convention rather than transplant its slice indices.

Start experiments with O=2, H=16, K=8, but treat these as explicit recipe choices,
not architecture constants or tuned values. K <= H. The execution layer discards
its remaining chunk on reset/termination. All comparisons use the same control
period, horizon, observation history, camera set, representation and normalization.

## Shared conditioning and representations

Use one vision implementation, initially a randomly initialized ResNet-18 with
GroupNorm, shared across cameras with explicit camera identity. It can return
spatial feature maps; DP/FM pool them into a global condition while MoT projects
spatial cells into tokens. Image history and camera identity must not collapse
into an unordered average. Different pooling/projections belong to each network,
not separate copies of the vision trunk implementation.

Starting all three with the same vision initialization makes comparison easier.
The user's restriction forbids language weights; it does not forbid pretrained
vision. A pretrained vision experiment can be a later explicit recipe. No silent
downloads or unused alternate backbones are introduced now. Shared camera weights
and our feature pooling are choices that differ from some official DP recipes.
[Official DP example configuration](https://github.com/real-stanford/diffusion_policy/blob/5ba07ac6661db573af695b419a7947ecb704690f/diffusion_policy/config/train_diffusion_unet_image_workspace.yaml)

`ActionCodec` is the single training/inference implementation of command layout.
Initial support is native actuator controls plus absolute world-space mocap poses:
positions and 6D rotations, converted back to normalized wxyz quaternions at the
simulator boundary. Resolve named controls/bodies in the simulation adapter, not
inside a network. A mocap body contributes 9 dimensions; actuator channels are
additional and are not assumed to be one gripper scalar. Joint-controlled models
can have only ctrl. “10D action” is therefore one layout, not a universal API.

Specify the 6D matrix-column convention and check encode/decode round trips.
Degenerate generated rotations need deterministic orthonormalization with a
well-defined fallback. Validate finite commands and actuator limits before sending
them to MujocoEnv. Delta poses, relative finger policies and quaternion outputs
are deferred until an actual experiment requires them. The simulator stays unchanged.

Proprioception is measured robot state, not the current command and not every
qpos in the scene. Use explicitly selected robot joints/sites; do not leak object
poses into an RGB policy by flattening all simulator state. The same observation
adapter runs during preparation and rollout.

Fit state/action normalization on training source episodes only. Save statistics
as policy buffers and in checkpoint metadata. Use per-coordinate affine scaling
to [-1,1] with a constant-channel rule; keep rotation-6D components on their known
[-1,1] scale. Loss operates in normalized space and inference returns decoded-scale
encoded actions. Do not clip held-out targets silently or update statistics while
validating. A single serialized transform must serve both training and inference.

## Objectives

Let a denote normalized clean actions and e standard Gaussian noise. All losses
reduce over **valid scalar action elements**, so padding does not change the loss
scale. Reject a batch with no valid targets.

Diffusion:

```text
k ~ Uniform({0,...,N-1})
x_k = sqrt(alpha_bar[k]) * a + sqrt(1-alpha_bar[k]) * e
loss = masked_mean((network(x_k, k, observation) - e)^2)
```

Use the maintained Diffusers DDPM scheduler rather than hand-writing reverse
variance formulas. Start with epsilon prediction and a cosine schedule; store
scheduler configuration with the checkpoint. DDPM is the correctness baseline;
DDIM is an explicit lower-step inference choice using the same trained schedule,
not a change of training target. Sampling needs noise even with deterministic
DDIM updates, so accept a generator / initial noise for reproducibility.
[DDPM API](https://huggingface.co/docs/diffusers/api/schedulers/ddpm)
[DDIM API](https://huggingface.co/docs/diffusers/api/schedulers/ddim)

Flow matching uses a single convention throughout this repository:

```text
t=0: data, t=1: noise
x_t = (1-t) * a + t * e
target_velocity = e - a
loss = masked_mean((network(x_t, t, observation) - target_velocity)^2)

x = e
for descending times from 1 to 0:
    x = x + dt * network(x, t, observation)   # dt is negative
```

The time embedding must accept continuous flow times without integer casts; the
objective supplies the documented diffusion-index or continuous-time convention.
Uniform t is the standard first baseline. OpenPI instead samples a scaled Beta
variable and integrates backward from noise with Euler steps. Keep that time
sampling as an explicit later MoT ablation; use the same uniform law for FM and
MoT initially so architecture comparison does not also change the objective.
A short fixed-step Euler loop is sufficient; require cached/uncached agreement
before optimizing it. Do not claim a straight conditional path implies a perfectly
straight learned marginal trajectory or guaranteed one-step inference.
[OpenPI objective and sampling](https://github.com/Physical-Intelligence/openpi/blob/215abfb217dbac7d5f1273282331b9b1866c0479/src/openpi/models/pi0.py)

## The language-free MoT

MoT means **separate transformer parameters by token stream**, not a sparsely
routed mixture-of-experts layer. Use an observation expert and an action expert
with compatible attention head dimensions. Each has its own normalization,
Q/K/V and output projections, and feed-forward block. At each depth, action
queries attend over observation and action keys/values in one attention operation.
A generic cross-attention decoder is not an equivalent implementation.
[OpenPI expert attention](https://github.com/Physical-Intelligence/openpi/blob/215abfb217dbac7d5f1273282331b9b1866c0479/src/openpi/models/gemma.py)

The stream mask is deliberately simple:

| Query stream → / Key stream ↓ | Observation | Noisy actions |
| --- | --- | --- |
| Observation queries | allowed | blocked |
| Action queries | allowed | allowed |

Action tokens attend bidirectionally within the chunk. They are noisy generative
variables, not autoregressively supplied ground-truth future commands. Observation
history never contains future observations. Padding masks also apply. Boolean-mask
semantics must be checked against the chosen PyTorch attention API.

Observation tokens contain visual cells and continuous proprioception with
camera, spatial, history-time and modality identity. Action tokens have horizon
positions and action input/output projections. Time conditions the action expert
through adaptive RMSNorm; it does not alter observation tokens. Attention
positions and masks must be identical between the training and cached inference
paths.

This yields a useful performance boundary: compute the observation expert's
per-layer K/V once per policy decision; reuse it for all flow integration steps.
Recompute action K/V each step. Discard the cache at the next observation. During
training, gradients must flow through those observation K/V into the observation
expert and vision trunk. Do not detach them or freeze a randomly initialized
prefix merely because pretrained OpenPI variants use knowledge insulation.

The full π0.5 recipe has objectives supporting its pretrained backbone; we are
not implementing those objectives. Both experts train end-to-end on action loss.
[Knowledge-insulation explanation](https://www.pi.website/research/knowledge_insulation)

Keep widths/layer counts configurable but begin compactly and measure parameter
count, activation memory and control latency. There is no justification for
copying a billion-parameter vocabulary-bearing VLM into a language-free baseline.
This design is not compatible with π0.5 checkpoints and makes no claim about its
open-world capabilities.

## How to keep the code small

One `ChunkPolicy` orchestrates normalization, conditioning, loss and sampling.
Two small objective implementations own noise/time sampling, targets and integration.
Two action-network implementations own U-Net versus MoT structure. Three named
recipe constructors expose the requested policies; they do not duplicate loops.

An action network supports `condition(observation)` and
`predict(noisy_actions, time, condition)`. For U-Net the condition is global
features; for MoT it is per-layer observation memory. Condition is transient,
never a checkpoint field or a global mutable cache. Training keeps its graph;
inference uses inference_mode. This interface is justified by both real networks,
not a plugin framework for hypothetical future models.

Reuse library schedulers, convolutions, ResNet and attention primitives. Do not
import the old ACT trainer, clone an entire research framework, or patch installed
Transformers files. If implementation code is adapted from a reference, retain its
license and provenance; the current PR contains design only.

# Training ownership and implementation sequence

Status: design for review. The paths below are planned modules, not empty packages
or claims that an implementation exists.

## Module ownership

```text
infra/                           # existing: personal filesystem roots
lucidxr/
  sim/
    demos.py                     # existing: raw recording format
    teleop/                      # existing: browser collection
    mujoco_env/                  # existing: native environment and render wrappers
    render_demo.py               # planned: restore/capture source frames
    policy_adapter.py            # planned: names -> native observations/commands
  scripts/
    record_demo.py               # existing
    playback_demo.py             # existing
    view_scene.py                # existing
    prepare_dataset.py           # planned: compose rendering and episode writing
    train.py                     # planned: parse config and call training loop
    evaluate_policy.py           # planned: checkpoint + environment + chunk execution
training/
  policy/
    policy.py                    # ChunkPolicy; three named recipe constructors
    diffusion.py                 # diffusion objective and scheduler adapter
    flow_matching.py             # flow objective and Euler sampler
    vision.py                    # one visual feature implementation
    unet.py                      # conditional temporal U-Net
    mot.py                       # observation/action experts and attention/cache
    actions.py                   # explicit ActionSpec and ActionCodec
    normalization.py             # fitted transforms shared with inference
  data/
    episodes.py                  # prepared HDF5 schema, reader and writer
    dataset.py                   # read-only history/chunk windows and sampling
    statistics.py                # training-split statistics
  train.py                       # shared training loop
  checkpoint.py                  # versioned save/load/resume payload
  config.py                      # typed configuration, no mutable globals
  configs/                       # three small, exercised recipes when implemented
  docs/                          # these design notes
```

Do not create this entire tree as stubs. Add each module with its first real caller.
Keep a helper beside the operation it serves; split it only when it has a separate
responsibility. The three recipe constructors are the policy implementations from
an API perspective; objective/network composition supplies their differences.
Avoid three copied trainers or a family of base classes with one implementation.

Allowed dependency direction:

- policy: torch/vision/scheduler primitives and its own specs; no sim, data or infra.
- data: episode files and shared policy representation specs; no rendering or infra.
- training loop: policy + data + optimizer/logging/checkpoint utilities; no simulator.
- simulation policy adapter: native sim plus the shared policy I/O representation.
- scripts: compose the required pieces and pass explicit paths/configuration.
- infra: supply locations now; add host staging or scheduling only with a caller.

The same root-level `training/` package contains deployable policy code, matching
the requested repository split. It is not a second environment or a vendored
upstream training framework. Add it to packaging only when Python modules exist.

## Dependencies

Use PyTorch, torchvision, Diffusers schedulers and h5py for the first working slice.
Use existing NumPy and TOML support. Keep them in an optional training dependency
set so sim-only and teleop-only installations remain lightweight. Add W&B when the
trainer's metric calls exist. Verify current package/Python 3.14 compatibility
and CUDA support on the actual MIT node when locking that implementation.

No openpi runtime dependency, JAX stack, language tokenizer, patched Transformers,
Hydra object registry, Lightning trainer, or new generic flow library is needed
for these three policies. This is not an argument against those tools generally;
the proposed code already has a smaller concrete execution path. The two most
substantial custom pieces will be the conditional U-Net and the MoT layer/cache;
“three policies” should not turn into three frameworks.

## One training loop

The first trainer is single-device PyTorch with explicit configuration:

1. Validate the completed dataset manifest and I/O specs.
2. Load training-only statistics and build the chosen policy recipe.
3. Construct read-only datasets, sampler and DataLoaders.
4. Apply device-side image preprocessing, compute loss, backpropagate, clip gradients,
   update AdamW and learning-rate schedule, then update EMA.
5. Periodically evaluate with eval mode, fixed validation noise/times and deterministic
   preprocessing. Restore train mode afterward.
6. Save a resumable checkpoint and metric records under the explicit run directory.

Use AMP where supported, with float32 loss reductions and normalization. Preserve
a CPU float32 path for small correctness checks. Do not assume all model/device
combinations support bfloat16 or compile efficiently. Make EMA update frequency
and decay explicit and evaluate the EMA model consistently across policies.

A normal dataclass/TOML configuration is enough. Each policy recipe supplies only
its differences; a resolved configuration is saved with the run. Unknown keys and
shape/layout mismatches are errors, not silently ignored options. No function
imports from arbitrary strings or inherited experiment-global state.

Core knobs are policy kind, observation/action specs, horizons, model size,
optimizer/schedule, batch size/workers, total updates, seed, validation/checkpoint
intervals and data/output paths. Add DDP, compile, multiple dataset mixtures or
large-model sharding only after a working single-device run and an observed need.
MIT job submission remains a separate infra concern; no scheduler SDK imports in
policy or data code.

## Checkpoints and logging

The filesystem is the source of truth. Write a temporary checkpoint and publish
it atomically. Its versioned payload includes policy/EMA state_dicts, normalizer
and I/O specs, optimizer/scheduler/AMP states, completed update count, sampling/RNG
state, resolved configuration, dataset-manifest hash and code version. Use tensors
and primitive containers, not pickled live policy/environment objects.

A resume validates dataset, architecture, control period and representation before
loading optimizer state. Loading model weights to start a new run is a distinct
operation. Save checkpoints at well-defined sampler boundaries; do not promise
bit-exact mid-epoch resume while discarding a DataLoader's prefetched index state.
For an exact initial resume contract, save sampler position at a completed batch
and reconstruct the remaining deterministic index sequence, discarding any old
prefetch queue. Random augmentation must be seeded by the saved step/sample identity
rather than unsaved worker RNG state.

W&B tracks run configuration and metrics, and optionally explicitly selected
rollout media. **No W&B Artifacts for datasets or checkpoints.** Keep local JSONL
metrics so a run remains inspectable without a W&B connection. Credentials come
from the user's runtime environment; no account/entity values are embedded in code.
Logging is a small helper invoked by the trainer, not a callback/plugin framework.
[W&B metric logging](https://docs.wandb.ai/models/track/log)

## Inference and evaluation

`evaluate_policy` loads the policy without constructing a trainer or a DataLoader.
The simulation adapter resolves named robot state/control channels once, maintains
observation history, encodes observations, requests an H-action chunk, decodes and
executes K commands, then replans. All decisions use the checkpoint's normalization,
representation and control period. Reset clears history/chunks and observation caches.

Report action errors in physical units where meaningful, rollout completion metrics
from actual task rules, and measured inference latency. Diffusion and flow training
losses are not directly comparable scores. The base MujocoEnv has no task success
criterion: do not label nontermination or zero reward as success. Attach an explicit
Episode rule when a task evaluation actually has one.

Compare DP/FM first with an identical U-Net, vision encoder and data recipe. Compare
MoT at documented parameter/memory/latency budgets; calling all variants “small” is
not evidence of a fair capacity comparison. Record denoising/integration step counts.
No pretrained-language benefit or π0.5 benchmark claims apply to this experiment.

## Performance commitments worth making now

- Decode/read only the window needed. No downloads, simulator contexts or cache
  construction in Dataset workers.
- Encode image history once per policy decision, not once per diffusion/flow step.
- Reuse MoT observation K/V during sampling, and test against uncached inference.
- Keep preprocessing shared and transfer uint8 RGB once. Avoid converting the whole
  dataset to float images or moving each camera independently in nested Python loops.
- Use PyTorch attention primitives and profile before adding custom kernels.
- Measure preparation throughput, batch wait time, examples/second, peak GPU memory
  and full control-decision latency separately. A shallow wrapper stack does not
  make expensive rendering or 100 denoising evaluations free.

## Bounded implementation sequence

This PR is the research/design slice. The following slices should add working
paths, not speculative scaffolding:

1. **Data semantics and one prepared episode.** Establish an authoritative transition
   recording contract, pure action/observation transforms and an offline preparer.
   Render one pick_block episode, reload a window and verify alignment. Support
   legacy approximations only with explicit provenance. No full trainer yet.
2. **Diffusion Policy end to end.** Add the vision encoder, conditional U-Net,
   scheduler adapter and one trainer. Overfit a tiny known-alignment dataset,
   save/resume, and run decoded actions in the environment. This forces every
   initial abstraction to have a real caller.
3. **Flow Matching on the same network.** Add the velocity objective and Euler
   sampling loop. Reuse the existing loader, transforms, trainer and evaluator.
   Test the time/sign convention against a known vector field.
4. **Language-free MoT.** Add separate expert parameters, the block mask and adaptive
   time conditioning. Verify no observation dependency on noisy action tokens,
   gradients into both experts, padding behavior, and cached/uncached equivalence.
   Use the existing flow loss and sampling loop without copying either.
5. **MIT run and measured improvements.** Run the three recipes with comparable
   data/control settings, then add only the staging/launch/distribution operations
   that the actual run needs. Keep GPU execution results distinct from CPU tests.

Meaningful tests are a small number of contracts: codec round trip, window alignment
and split isolation, scheduler/flow sign sanity, finite loss/gradients for each
policy, tiny-batch overfit, checkpoint continuation, MoT gradient/mask/cache behavior,
and one decoded rollout smoke. Do not turn this into a comprehensive benchmark
suite before there is a real training run.

## Research provenance

Primary references were inspected directly. OpenPI was reviewed at
`215abfb217dbac7d5f1273282331b9b1866c0479`; official Diffusion Policy at
`5ba07ac6661db573af695b419a7947ecb704690f`. Links in POLICIES.md pin code to those
commits. No upstream source code or weights are copied in this design PR.

The repository audit covered the old ACT policy/trainer, both episode dataset
variants and render_worker. Its important findings are the hidden +1 action shift,
I/O and cache mutation inside Dataset, mixed rendering/queue/storage responsibilities,
and train-time augmentation reused in validation. These findings motivate the new
boundaries; they are not claims that old datasets have already been converted.

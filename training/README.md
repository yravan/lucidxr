# Training

The training package is independent of deployment configuration. Its core modules
accept tensors and paths; scripts resolve personal locations and MIT resources
through `infra`. No language inputs or pretrained language/vision weights are used.

Implementation is stacked after rendering PR #7, in four reviewable slices:
models, policies, data, then the trainer and MIT integration. This first slice adds
working neural networks; later slices supply objectives and their actual callers.

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

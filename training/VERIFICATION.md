# Training verification — 2026-09-18

The implementation goal remains active until the MIT GPU checks pass. The local
results below establish functional behavior; they do not establish production
throughput or manipulation success.

## Completed locally

- Python 3.14.7, PyTorch 2.14.0, torchvision 0.29.0, Diffusers 0.40.0,
  W&B 0.30.0 and MuJoCo 3.13.0, installed through the locked uv extras.
- `pytest -q`: 50 passed. A subsequent native adapter check also passed: selected
  robot state excludes object joints, native commands round-trip, and both
  `pick_block` and `pick_sphere` advance through small motions with different
  compiled state layouts. The final focused training suite contains 17 checks.
- All three policies learn a fixed batch, sample reproducibly with an explicit
  generator, and evaluate vision once per decision. MoT cached attention matches
  the independent joint-attention reference and preserves prefix/vision gradients.
- Preparation verified the actual six-frame browser recording and 1,500-frame
  native recording rendered on MIT. Training-only extrema were checked directly
  against the prepared arrays. Label alignment, padding, split isolation,
  corruption detection and two-worker sampling/resume are covered.
- Interrupted/resumed training reproduced uninterrupted CPU policy weights, EMA,
  optimizer state and noise RNG exactly. A deliberately failed checkpoint write
  preserved the previous checkpoint. A real USR1 stopped the MoT smoke run at a
  complete batch boundary and saved step 521.
- W&B offline logging ran successfully with ordinary scalar metrics and no
  Artifacts. JSONL and local checkpoint files remain authoritative.
- Native EMA MoT rollout completed 100 control steps / 2.0 simulation seconds in
  `pick_sphere`, with a decodable 640×360 MP4. Median inference was 6.87 ms for this
  tiny CPU configuration (32-pixel images, width 32, depth 2, 16 flow steps). This
  is an execution check using a nearly stationary diagnostic recording, not task
  success or a representative production benchmark.
- The wheel builds and contains the training modules/default TOML, excluding tests
  and deprecated code. Existing simulator imports retain their five core dependencies.
- Remote-launch dry runs capture code, input/config identity, entry point, arguments
  and dependency extras. Local execution of the actual transfer verifier rejects
  a corrupted upload before publication. Scratch tests verify listed-file staging
  and the explicit shared-storage fallback. A generated-shell process test proves
  USR1 reaches Python's batch PID and preserves nonzero worker exit status.

## Performance measurement boundary

The 1,500-frame render measured 5.07 ms per random MP4 two-frame window versus
0.008 ms from a warm decoded map. RGB preparation took 1.29 seconds and increased
storage from 1.34 MB to 73.7 MB at 128×128. Full loader throughput at batch size 32
was 46.6k windows/s with zero workers and 65.8k with two. These small, warm-cache
Mac measurements do not establish cold shared-filesystem or CUDA-feed throughput.

## Policy-quality limitations

The native diagnostic recording contains almost constant commands. Diffusion and
flow losses decreased substantially, but their closed-loop smoke policies could
leave the training distribution and trigger MuJoCo's instability check. Those
failures are retained as failures; the controller does not hide them by clamping
workspace poses or reporting success.

Three additional programmatic moving-control trajectories completed recording,
rendering and preparation with separate collection groups. An 800-step flow run
reached approximately 0.173 training loss and 0.195 held-out loss, but its longer
closed-loop rollout still became unstable. These small artificial fixtures are
useful for plumbing checks and insufficient evidence of a useful manipulation
policy. Meaningful task quality requires representative demonstrations and an
explicit episode success criterion; the current CLI reports `success: null`.

## Outstanding MIT check

Engaging is reachable, but SSH currently rejects public-key/keyboard-interactive
authentication and there is no active ControlMaster socket. The training runtime
PR stays draft until an authenticated session allows real CUDA training, checkpoint
resume and loader/compute measurements on MIT. No GPU result is inferred from the
successful rendering runs in earlier PRs or from generated Slurm scripts.

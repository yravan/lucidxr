# Training verification — 2026-09-18

Local and MIT GPU checks establish functional training, sampling and checkpoint
recovery. Measurements below describe the stated diagnostic workload; they do not
establish production throughput or manipulation success.

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
- The resume regression also sends a real USR1 during validation between periodic
  checkpoints. It exposed and fixed an exit that could return without a checkpoint;
  the interrupted update now saves and resumes exactly. Completed-run resume repairs
  a missing status file from the authoritative checkpoint.
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
closed-loop rollout still became unstable. That fixture used 300 settling steps
while the initial rollout CLI used an immediate reset, so those results also
include an initialization mismatch. The CLI now exposes `--settle-steps` to match
the collector's existing environment setting. The later 5,000-step GPU flow
checkpoint completed 100 native control steps with matching warmup, as detailed
below. These small artificial fixtures are
useful for plumbing checks and insufficient evidence of a useful manipulation
policy. Meaningful task quality requires representative demonstrations and an
explicit episode success criterion; the current CLI reports `success: null`.

## MIT GPU execution

Engaging jobs `23078359` and `23078427` completed on `node3302`, NVIDIA L40S
(46,068 MiB, driver 590.48.01), with Python 3.14.7 and PyTorch 2.14.0+cu130.
The normal launcher captured commit `a9204b1`'s tree
`1835d92f6c93f1dbe5e3692e720c24301b3ee841`, verified the source archive, installed
the locked extras with uv, and staged the verified cache onto node scratch.
The second verification allocation reused this captured source.

All three policies completed 500 updates with CUDA BF16 autocast and fused AdamW.
The common configuration was batch 16, two observations, one 128×128 wrist camera,
horizon 16, width 128, two loader workers and two CPU threads. MoT used depth 4
and four heads. The cache contained three moving-control diagnostic trajectories,
with separate training/validation collection groups (fingerprint
`1ee26a7e74ae169a7003dd64e3dd607e90b352f7d31e70e545a6d3b860bdb8c1`).

| Policy | Windows/s | Update ms | Batch wait ms | FP32 sampling ms |
| --- | ---: | ---: | ---: | ---: |
| Diffusion | 823 | 19.43 | 0.52 | 26.86 |
| Flow matching | 769 | 20.80 | 0.55 | 22.44 |
| MoT | 690 | 23.20 | 0.55 | 20.06 |

Training numbers are medians of ten-update intervals from step 50 onward; they
exclude launch/setup, checkpoint writes and validation. Sampling uses the saved
500-step EMA, batch one and 16 inference steps, with two warmup calls and ten
timed calls synchronized on CUDA. All repeated seeded outputs were identical and
finite. BF16 sampling also passed, but was slower here (33.92 / 29.35 / 25.83 ms
respectively); the rollout controller retains FP32 inference.

The complete loader with collation and pinned memory reached 6,514 windows/s
(median wait 2.44 ms, p95 3.30 ms; batch 16, two workers, 200 measured batches
after five warmup batches). This is a small, warm node-local cache, not a test of
large datasets on a cold shared filesystem. Local JSONL, offline W&B metrics,
shared-storage checkpoints and complete status records were produced.

A separate 50-update GPU reference matched a USR1-interrupted run resumed from
step 20 exactly: policy weights, EMA, optimizer state, objective RNG and CUDA RNG.
This comparison explicitly enabled deterministic PyTorch algorithms and
`CUBLAS_WORKSPACE_CONFIG=:4096:8` on the same GPU; it does not promise bitwise
agreement across GPU types or nondeterministic kernel choices.

A separate scheduler test sent `scancel --signal=USR1 --batch 23078896` during
a 5,000-update run. The trainer saved step 1,979 and marked the run `interrupted`.
`python -m infra resume RECEIPT` confirmed terminal accounting and resubmitted the
unchanged captured script as job `23079073`. On a different node (`node4104`
instead of `node1634`), it loaded step 1,979, continued to 5,000 and published
`complete`. Both allocations exited 0; the explicit run status distinguished the
cooperative stop from actual completion. Receipt run ID:
`a2bd02bf40fc4abea020304ec751e34e`.

The scheduler check reused an existing archive as a transport basis with Jaynes'
uncompressed tar option; normal full-archive checksum verification still preceded
submission. The first GPU run used the default compressed upload. Resubmission
itself required no source/cache upload, code checkout or changed launch script.

Finally, job `23079259` exercised the updated rollout CLI with the resumed
5,000-step EMA, `pick_sphere`, seed 9, `--settle-steps 300`, CUDA inference and
four executed actions per chunk. It completed 100 native control steps / 2.0
simulation seconds without unstable physics. The MP4 decoded to exactly 100
128×72 frames, and median inference was 23.90 ms on that allocation. The result
correctly reports `success: null`; no task-success criterion was added or inferred.

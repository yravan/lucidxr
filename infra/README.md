# Personal infrastructure

This directory owns personal storage configuration and remote job launching.
Simulation and recording formats do not import it. Scripts resolve ordinary paths
here and use Jaynes to capture code, transfer it and submit work to MIT Slurm.
Model, policy and dataloader implementations belong outside infra.

Training uses the same captured-source launcher and recovery receipts as rendering.
See [training setup](../training/README.md#mit-launch). `infra/training.py` handles
verified cache transfer and node-local staging; it does not implement a dataset,
policy, optimizer or training loop. Personal `training_cache` and `training_runs`
locations can be added alongside `demos`, as shown in `example.toml`.

Copy `infra/example.toml` to `~/.config/lucidxr/infra.toml` and edit the demos path:

```toml
[locations]
demos = "~/lucidxr-data/demos"
```

Use `uv run python -m infra path demos` to print it. `--config PATH` or
`LUCIDXR_INFRA_CONFIG` chooses another configuration file. Resolution does not
create, connect, upload or mount anything. Missing configuration is an error;
there is no fallback to an unexpected save location.

The configured root can be a local Dropbox sync directory, an already-mounted
filesystem, or a cluster path when running there. Use the actual path visible to
that process. An SSH hostname is not a filesystem path; use the cluster profile below for
remote job submission. Dropbox
sync completion and remote durability are not guaranteed by a local file write.

The boundary is deliberately narrow: infra supplies a root; the application owns
its recording format and file naming. Later checkpoint and dataset code can use
other configured roots without moving policy/model/dataloader code into infra.
Keep personal configurations outside Git and do not embed host paths or tokens in
scene definitions, scripts, or recording metadata.

## Remote rendering with Jaynes

Install `uv sync --extra rendering --extra launch`, configure `[clusters.engaging]`
using `example.toml`, and authenticate once with `ssh engaging`. Then launch:

```sh
uv run python -m lucidxr.scripts.launch_render /path/to/demo.npz \
  --cluster engaging --cameras wrist --mode commands
```

`--infra-config PATH` selects another profile file. `--dry-run` freezes the code
and writes generated scripts without contacting the cluster. New files require
`git add`; tracked working-tree edits are included without changing your real Git
index, branch or HEAD. Personal config and `.env` are not captured unless tracked.

Jaynes SSHCode creates and uploads a tar of the frozen source and explicit inputs.
Its Slurm runner serializes a call to the normal worker CLI. Each worker uses a
job-local uv environment from the captured lockfile, with matched Python/cloudpickle
versions. No manually maintained remote checkout, Docker, ml-logger, params-proto,
Zaku or persistent launcher server is required. SSH uses your normal host alias
and authenticated connection. GNU rsync is required by SSHCode's progress option.

`concurrency` bounds the number of GPU worker jobs. Each processes a fixed partition
of recordings, reports each failure and exits nonzero if any assigned item failed.
Completed content IDs are verified and skipped on repetition. The last successful
worker publishes a collection record only after verifying the whole requested set.

The command prints a local `launch.json` receipt. It records code-tree and archive
hashes, resolved profile, remote paths, confirmed Slurm IDs and submission state.
Generated scripts remain beside it. Remote `worker-N.submission` files record
accepted job IDs, and `worker-N-JOBID.log` holds ordinary stdout/stderr. After a lost
connection, inspect those records before submitting again. `infra.launch.status`
queries Slurm accounting using the receipt. Rendering progress/completion lives in
render records, rather than being inferred from scheduler state or directory names.

See [JAYNES.md](JAYNES.md) for the source review and small compatibility correction.

The local renderer and remote launcher accept the same `--mode`, `--scene`, `--seed`
and `--scene-options` arguments. These choices and the target scene fingerprint
are captured in each work identity. Command replay can therefore be distributed
without changing its physics or pairing images with the original scene's states.

## Scratch and retry recovery

Cluster workers copy each recording into an owned workspace beneath `SLURM_TMPDIR`
(or the node's temporary directory), verify its content hash, and write videos and
HDF5 there. Closed, validated artifacts are copied to a new shared attempt and
verified again before publishing its completion record. A partial transfer never
becomes a completed item. Successful scratch workspaces are removed; failures are
logged and retained while the cluster permits. Node-local scratch is temporary and
may disappear after an allocation ends. Durable recovery always starts from the
captured source and input bundle, not from leftover scratch files.

```sh
uv run python -m infra status ~/.cache/lucidxr/launches/RUN_ID/launch.json
uv run python -m infra reconcile ~/.cache/lucidxr/launches/RUN_ID/launch.json
uv run python -m infra resume ~/.cache/lucidxr/launches/RUN_ID/launch.json
```

Resume uses the original frozen code and saved worker commands without uploading
again. It verifies script hashes and, for a fully submitted run, checks that every
previous job is terminal. Missing accounting information blocks retry. An atomic
shared claim prevents two clients from retrying the same generation. Submission
history and remote receipts are retained. Accepted outputs are checksum-verified
and skipped; missing outputs are rendered again. Corrupt accepted output is an
explicit error requiring inspection, never silently overwritten.

If a connection drops during submission, run `reconcile` first. It verifies the
source bundle's ready marker, recovers accepted job IDs from remote receipts, and
identifies workers that have never been claimed. It submits nothing. `resume` can
then finish that partial submission while previously accepted workers continue.
Every submission has its own atomic claim, so concurrent clients cannot submit the
same worker twice. These commands require launch receipt version 2.

A claim without a saved job ID remains ambiguous: Slurm may have accepted the job
before the connection failed. Reconciliation stops instead of guessing. Inspect
`submission_directory` (or `remote_run`), its `worker-N.submission` files, worker
logs and Slurm accounting. Do not remove a claim until every accepted job has been
accounted for. Status and recovery commands require the `launch` extra;
storage-path lookup does not import Jaynes.

Assets are still included in each new frozen source archive. The current archive
is about 229 MB compressed; uploads cost considerably more than tiny smoke renders.
Resume reuses that upload. A separate asset cache can be added when repeated new
launches make it necessary; there is no additional asset-sync service yet.

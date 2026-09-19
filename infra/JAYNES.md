# Jaynes integration review

Reviewed the installed PyPI `jaynes==0.9.14` code, the upstream README, SSH/Slurm
notes, Sphinx usage docs, and starter-kit SSH, batch, chained and multi-job examples.
Upstream checkout inspected: `f42fa078424f48ad7a2945cb9e3ffd676682dc1f` (its VERSION
says 0.9.12); shipped PyPI code is the authority for the pinned adapter behavior.
Older docs mix in ml-logger setup; it is not a dependency of the installed release.

## What to reuse

- SSHCode builds a tar and uploads via system SSH/rsync. It can use normal SSH
  aliases and ControlMaster reuse; no password-bearing application config is needed.
- Runner separates login-node `setup` from allocated-worker `startup`. uv setup
  belongs in startup; it must not run rendering on the login node.
- Slurm supports `interactive=False` (sbatch), CPU/GPU/time/account/memory flags,
  custom entry commands and arbitrary remaining Slurm options.
- `add` queues independent runners; `chain` adds calls within a runner and its
  default separator permits concurrent execution. Neither is a persistent queue.
- `entry` decodes cloudpickle and invokes the function; no training-framework API
  or logging server is required. Keep payload arguments small and version-matched.
- `listen` is a client waiting loop. It does not confirm Slurm completion or artifact
  validity. `n_seq_jobs` repeats submissions with singleton dependencies; it is not
  an artifact-aware retry policy. Use unique worker job names to avoid accidental
  serialization through singleton.

## Small corrections at our boundary

The batch template executes its worker with `& wait`. A local experiment with a
failing entry command returned zero; foreground execution returned nonzero.
`BatchSlurm` changes only that template fragment and adds strict shell behavior.
It checks the expected fragment so a future upstream change cannot silently bypass
review. Test the generated shell, not just the template string.

The shared launcher uses `exec` for the final Python entry command. This preserves
the worker's exit status and PID: training requests Slurm's `B:USR1@60` warning,
which targets the batch process. Python must replace that shell to receive it.
A focused process test sends USR1 to the batch PID and verifies the worker handler
and nonzero exit status. The meaning of `B:` follows the
[Slurm sbatch signal documentation](https://slurm.schedmd.com/sbatch.html#OPT_signal).

SSH's blocking API returns stdout/stderr but no return code. Our adapter appends an
unpredictable success marker under strict shell execution and requires it. Each
submission persists its output remotely before returning, so an interrupted client
can reconcile accepted job IDs. Submit workers serially; background batching would
make partial submission errors harder to attribute. Slurm still runs them in parallel.

Mount upload helpers can print subprocess failures instead of propagating them.
Verify the archive SHA256 remotely before unpacking or submitting. Do not mistake
successful transport for successful rendering; workers separately validate outputs.
Keep strict host verification explicit in SSH options. Archive paths are restricted
to simple characters because upstream shell templates interpolate them. Shell braces
in worker startup are escaped for Jaynes's formatting pass.

The high-level `Jaynes.config` API stores process-global cached config/mounts. Our
one-shot CLI composes its mount/runner/SSH building blocks directly and saves the
resolved configuration, instead of relying on discovery of a parent `.jaynes.yml`.
The mount constructor's config root is restored immediately after construction.
No global launch state enters simulator or training imports.

## References

- [Jaynes overview](https://github.com/geyang/jaynes)
- [Slurm starter guide](https://github.com/geyang/jaynes-starter-kit/tree/master/04_slurm_configuration)
- [SSH and two-factor reuse example](https://github.com/geyang/savio-starter-kit)
- [Runner implementation](https://github.com/geyang/jaynes/blob/f42fa078424f48ad7a2945cb9e3ffd676682dc1f/jaynes/runners.py)
- [SSH implementation](https://github.com/geyang/jaynes/blob/f42fa078424f48ad7a2945cb9e3ffd676682dc1f/jaynes/launchers/ssh_launch.py)

NeMo Run and SkyPilot were also researched; NeMo executed successful and failing
CPU smoke jobs on Engaging. It was not retained: its broader dependency footprint
and experiment abstractions were unnecessary for this workflow. The renderer stays
independent of launch machinery; the adapter is not a replacement scheduler.

# Personal infrastructure

This directory owns machine-specific storage configuration. Simulation and demo
files do not import it. It currently does one thing: resolve a configured name to
an ordinary filesystem path. There are no cluster schedulers, transfer services,
model registries, training abstractions, credentials or unused backend classes.

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
that process. An SSH hostname is not a filesystem path; remote access, syncing and
cluster job submission will be added only when a real workflow needs them. Dropbox
sync completion and remote durability are not guaranteed by a local file write.

The boundary is deliberately narrow: infra supplies a root; the application owns
its recording format and file naming. Later checkpoint and dataset code can use
other configured roots without moving policy/model/dataloader code into infra.
Keep personal configurations outside Git and do not embed host paths or tokens in
scene definitions, scripts, or recording metadata.

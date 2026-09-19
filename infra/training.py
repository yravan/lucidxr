"""Content-addressed cache transfer and node-local staging for ordinary training CLIs."""

import json
import logging
import os
import shlex
import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from .launch import launch_jobs, remote

logger = logging.getLogger(__name__)


def stage_cache(cluster, cache):
    """Transfer the closed cache separately from source snapshots; reuse its content ID."""
    from training.data.manifest import load_manifest

    cache = Path(cache).resolve()
    manifest = load_manifest(cache, verify=True)
    destination = Path(cluster.root) / "training-cache" / manifest["fingerprint"]
    ready = remote(
        cluster, f"if test -f {shlex.quote(str(destination / 'manifest.json'))}; then echo ready; fi"
    )
    if "ready" in ready.splitlines():
        logger.info("Reuse remote cache=%s; worker will verify all bytes before training", destination)
        return destination, manifest["fingerprint"]
    upload = destination.parent / f".upload-{uuid4().hex}"
    remote(cluster, shlex.join(["mkdir", "-p", str(upload)]))
    logger.info("Transfer cache=%s host=%s destination=%s", cache, cluster.host, upload)
    with tempfile.NamedTemporaryFile() as inventory:
        inventory.write(b"\0".join(name.encode() for name in ("manifest.json", *manifest["files"])) + b"\0")
        inventory.flush()
        subprocess.run(
            [
                "rsync",
                "-az",
                "--from0",
                f"--files-from={inventory.name}",
                "--protect-args",
                "--partial",
                "-e",
                "ssh -o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=yes",
                "--",
                f"{cache}/",
                f"{cluster.user}@{cluster.host}:{upload}/",
            ],
            check=True,
        )
    # This remote verifier uses only stdlib and works before the job's uv environment exists.
    script = """
import hashlib, json, os, shutil, sys
from pathlib import Path
source, target, expected = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
value = json.loads((source / 'manifest.json').read_text())
identity = value.pop('fingerprint')
actual = hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
if identity != expected or actual != expected:
    raise SystemExit('Training cache manifest identity mismatch')
for name, info in value['files'].items():
    path = (source / name).resolve()
    if source.resolve() not in path.parents or path.stat().st_size != info['bytes']:
        raise SystemExit('Invalid training cache path/size')
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
    if digest.hexdigest() != info['sha256']:
        raise SystemExit('Training cache checksum mismatch')
if target.exists():
    if json.loads((target / 'manifest.json').read_text())['fingerprint'] != expected:
        raise SystemExit('Existing cache identity mismatch')
    shutil.rmtree(source)
else:
    os.rename(source, target)
print(target)
"""
    remote(
        cluster, shlex.join(["python3", "-c", script, str(upload), str(destination), manifest["fingerprint"]])
    )
    return destination, manifest["fingerprint"]


def launch_training(cluster, repo, config, cache, *, dryrun=False, wandb_mode="offline", project="lucidxr"):
    from training.config import read_config
    from training.data.manifest import load_manifest
    from training.scripts.remote_train import main as worker

    resolved = read_config(config)
    if resolved.device != "cuda":
        raise ValueError("MIT GPU launch requires device='cuda'")
    if resolved.cpu_threads > cluster.cpus or resolved.workers > cluster.cpus:
        raise ValueError("Training CPU threads and loader workers must fit the cluster CPU allocation")
    manifest = load_manifest(cache, verify=dryrun)
    resolved.policy_spec(manifest)
    remote_cache = Path(cluster.root) / "training-cache" / manifest["fingerprint"]
    if not dryrun:
        remote_cache, _ = stage_cache(cluster, cache)
    with tempfile.TemporaryDirectory(prefix="lucidxr-training-launch-") as temporary:
        payload = Path(temporary)
        shutil.copyfile(config, payload / "config.toml")
        (payload / "job.json").write_text(
            json.dumps(
                {
                    "cache": str(remote_cache),
                    "fingerprint": manifest["fingerprint"],
                    "wandb": wandb_mode,
                    "project": project,
                },
                indent=2,
            )
        )

        def arguments(index, workers, destination):
            return [
                "training_inputs/job.json",
                "--output",
                str(Path(cluster.root) / "training" / destination.name),
            ]

        return launch_jobs(
            cluster,
            repo,
            payload,
            1,
            worker=worker,
            arguments=arguments,
            extras=("training", "launch"),
            input_directory="training_inputs",
            marker="job.json",
            sbatch_args=("signal=B:USR1@60",),
            dryrun=dryrun,
        )


@contextmanager
def training_cache(source, expected):
    """Prefer local scratch; a verified shared cache remains usable when scratch is full."""
    from training.data.manifest import load_manifest

    source = Path(source)
    manifest = load_manifest(source)
    if manifest["fingerprint"] != expected:
        raise ValueError("Remote training cache differs from the captured job")
    scratch = Path(os.environ.get("SLURM_TMPDIR", tempfile.gettempdir()))
    scratch.mkdir(parents=True, exist_ok=True)
    required = sum(item["bytes"] for item in manifest["files"].values())
    if shutil.disk_usage(scratch).free < required * 1.1 + 64 * 1024**2:
        logger.warning("Insufficient node scratch; loading verified shared cache=%s", source)
        yield source  # The trainer verifies hashes in either case.
        return
    with tempfile.TemporaryDirectory(dir=scratch, prefix="lucidxr-training-") as temporary:
        target = Path(temporary) / "cache"
        logger.info("Stage training cache bytes=%d destination=%s", required, target)
        target.mkdir()
        for name in (*manifest["files"], "manifest.json"):
            destination = target / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / name, destination)
        yield target

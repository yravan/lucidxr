"""Use Jaynes code mounts and Slurm runners with explicit, inspectable launch records."""

import hashlib
import json
import logging
import re
import shlex
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path
from uuid import uuid4

from .files import atomic_json
from .snapshot import code_tree

logger = logging.getLogger(__name__)


def remote(cluster, script):
    """Jaynes pipe-mode SSH with a completion marker, since its API omits exit codes."""
    from jaynes.launchers.ssh_launch import ssh

    marker = f"LUCIDXR_OK_{uuid4().hex}"
    stdout, stderr = ssh(
        "set -euo pipefail\n" + script + f'\nprintf "\\n{marker}\\n"\n',
        ip=cluster.host,
        username=cluster.user,
        block=True,
        cleanup=False,
        options="-o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=yes",
    )
    output = stdout.decode()
    if marker not in output.splitlines():
        raise RuntimeError(f"Remote command did not complete:\n{output}\n{stderr.decode()}")
    return output.replace(marker, "").strip()


def launch_render(cluster, repo, payload, count, *, dryrun=False):
    import jaynes
    from jaynes.mounts import SSHCode

    from lucidxr.scripts.render_worker import main as worker

    from .jaynes import BatchSlurm

    repo, payload = Path(repo).resolve(), Path(payload).resolve()
    # Jaynes mount/runner templates interpolate paths into shell commands.
    for path in (str(repo), str(payload), cluster.root, cluster.uv):
        if not re.fullmatch(r"[A-Za-z0-9_./-]+", path):
            raise ValueError("Launch paths must contain only letters, digits, _, -, / and .")
    tree = code_tree(repo)
    run_id = uuid4().hex
    local = Path.home() / ".cache/lucidxr/launches" / run_id
    local.mkdir(parents=True)
    destination = Path(cluster.root) / "runs" / run_id
    code = destination / "code"
    remote_tar = destination / "snapshot.tar.gz"
    workers = min(count, cluster.concurrency)
    record = {
        "version": 1,
        "run_id": run_id,
        "git_tree": tree,
        "cluster": cluster.to_dict(),
        "remote_run": str(destination),
        "workers": workers,
        "jobs": [],
        "state": "preparing",
    }
    receipt = local / "launch.json"

    def save():
        atomic_json(receipt, record)

    save()
    # Materialize the frozen Git tree so SSHCode packages only reviewed tracked files.
    with tempfile.TemporaryDirectory(prefix="lucidxr-code-") as temporary:
        directory = Path(temporary)
        archive = directory / "git.tar"
        subprocess.run(
            ["git", "-C", str(repo), "archive", "--format=tar", f"--output={archive}", tree], check=True
        )
        source = directory / "code"
        source.mkdir()
        with tarfile.open(archive) as tar:
            tar.extractall(source, filter="data")
        shutil.copytree(payload, source / "render_inputs")
        (source / "render_inputs/launch.json").write_text(json.dumps(record, indent=2))
        previous_root = jaynes.RUN.config_root
        try:
            jaynes.RUN.config_root = str(source)
            mount = SSHCode(
                local_path=str(source),
                local_tar=str(local / "snapshot.tar.gz"),
                host_path=str(code),
                remote_tar=str(remote_tar),
                pypath=True,
            )
        finally:
            jaynes.RUN.config_root = previous_root
        scripts = []
        for index in range(workers):
            startup = "; ".join(
                [
                    f"cd {code}",
                    "export MUJOCO_GL=egl PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 UV_LINK_MODE=copy",
                    f"export OMP_NUM_THREADS={cluster.cpus}",
                    'export UV_PROJECT_ENVIRONMENT="${SLURM_TMPDIR:-/tmp}/lucidxr-venv-${SLURM_JOB_ID}"',
                    shlex.join(
                        [
                            cluster.uv,
                            "sync",
                            "--frozen",
                            "--extra",
                            "rendering",
                            "--extra",
                            "launch",
                            "--no-dev",
                            "--python",
                            "3.14",
                            "--no-install-project",
                        ]
                    ),
                ]
            )
            runner = BatchSlurm(
                mounts=[mount],
                work_dir=str(code),
                startup=startup.replace("{", "{{").replace("}", "}}"),
                entry_script='"$UV_PROJECT_ENVIRONMENT/bin/python" -u -m jaynes.entry',
                partition=cluster.partition,
                account=cluster.account,
                name=f"lxr-{run_id}-{index}",
                n_cpu=cluster.cpus,
                n_gpu=1,
                mem=f"{cluster.memory_gb}G",
                time_limit=str(cluster.minutes),
                output=str(destination / f"worker-{index}-%j.log"),
                args=["parsable"],
            )
            runner.build(
                worker,
                argv=[
                    "render_inputs/plan.json",
                    "--output",
                    str(Path(cluster.root) / "renders"),
                    "--workers",
                    str(workers),
                    "--worker-index",
                    str(index),
                ],
            )
            script = "set -euo pipefail\n" + runner.run_script
            scripts.append(script)
            (local / f"worker-{index}.sh").write_text(script)
        record["script_sha256"] = [hashlib.sha256(s.encode()).hexdigest() for s in scripts]
        if dryrun:
            record["state"] = "prepared"
            save()
            logger.info("Prepared snapshot tree=%s; launch scripts=%s", tree, local)
            print(receipt)
            return receipt
        try:
            logger.info("Upload snapshot tree=%s host=%s run=%s", tree, cluster.host, run_id)
            mount.upload(username=cluster.user, ip=cluster.host)
            with Path(mount.local_tar).open("rb") as stream:
                checksum = hashlib.file_digest(stream, "sha256").hexdigest()
            record["archive_sha256"] = checksum
            # Verify even when an upstream upload error was printed instead of raised.
            check = f'printf "%s  %s\\n" {checksum} {remote_tar} | sha256sum -c -\n'
            remote(cluster, check + mount.host_setup)
            record["state"] = "submitting"
            save()
            for index, script in enumerate(scripts):
                job = submit(cluster, script, destination / f"worker-{index}.submission")
                record["jobs"].append(job)
                save()
                logger.info("Worker submitted index=%d job=%s", index, job)
            record["state"] = "submitted"
            save()
        except BaseException as exc:
            record["state"], record["error"] = "incomplete", str(exc)
            save()
            logger.exception(
                "Launch incomplete. Inspect remote submission records before retrying: %s", destination
            )
            raise
    print(receipt)
    return receipt


def status(receipt):
    from .cluster import Cluster

    record = json.loads(Path(receipt).read_text())
    profile = Cluster(**record["cluster"])
    jobs = ",".join(record["jobs"])
    if not jobs:
        raise ValueError(f"No confirmed jobs; inspect {record['remote_run']}/worker-*.submission")
    return remote(
        profile, shlex.join(["sacct", "-j", jobs, "-P", "--format=JobID,State,ExitCode,Elapsed,NodeList"])
    )


def submit(cluster, script, submission):
    """Save Slurm's response remotely before acknowledging a submitted worker."""
    stdout = remote(cluster, "{\n" + script + "\n} | tee " + shlex.quote(str(submission)))
    ids = [line.split(";")[0] for line in stdout.splitlines() if re.fullmatch(r"\d+(;[^\s]+)?", line)]
    if len(ids) != 1:
        raise RuntimeError(f"Ambiguous submission; inspect {submission}: {stdout}")
    return ids[0]

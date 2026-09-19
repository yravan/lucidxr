"""Reconcile submissions and retry work using the exact captured source and scripts."""

import hashlib
import json
import logging
import re
import shlex
from pathlib import Path

from .cluster import Cluster
from .files import atomic_json
from .launch import remote, submit

logger = logging.getLogger(__name__)
TERMINAL = {
    "COMPLETED",
    "FAILED",
    "CANCELLED",
    "TIMEOUT",
    "NODE_FAIL",
    "OUT_OF_MEMORY",
    "PREEMPTED",
    "BOOT_FAIL",
    "DEADLINE",
    "REVOKED",
}


def require_terminal(profile, jobs):
    """Missing accounting rows and unknown states are uncertainty, not permission to retry."""
    if not jobs or any(not re.fullmatch(r"\d+", job) for job in jobs):
        raise ValueError("Receipt must contain confirmed numeric Slurm job IDs")
    ids = ",".join(jobs)
    queued = remote(profile, shlex.join(["squeue", "-h", "-u", profile.user, "-o", "%A"]))
    active = set(queued.splitlines()) & set(jobs)
    if active:
        raise ValueError(f"Previous jobs are still queued/running: {active}")
    output = remote(profile, shlex.join(["sacct", "-n", "-X", "-j", ids, "-P", "-o", "JobIDRaw,State"]))
    states = {}
    for line in output.splitlines():
        fields = line.strip().split("|")
        if len(fields) >= 2 and fields[0] in jobs and fields[1].strip():
            states[fields[0]] = fields[1].split()[0]
    if set(states) != set(jobs) or any(state not in TERMINAL for state in states.values()):
        raise ValueError(f"Cannot establish terminal state for every previous job: {states}")


def resume(receipt):
    receipt = Path(receipt).resolve()
    record = json.loads(receipt.read_text())
    if record["state"] not in ("submitted", "partial"):
        raise ValueError("Submission is uncertain; run infra reconcile before resuming")
    count = len(record["jobs"])
    if not 0 <= count <= record["workers"] or (record["state"] == "submitted" and count != record["workers"]):
        raise ValueError("Receipt job count disagrees with submission state")
    hashes = record.get("script_sha256", [])
    if len(hashes) != record["workers"]:
        raise ValueError("This receipt predates saved-script verification; launch a new run")
    scripts = [(receipt.parent / f"worker-{i}.sh").read_text() for i in range(record["workers"])]
    if [hashlib.sha256(s.encode()).hexdigest() for s in scripts] != hashes:
        raise ValueError("Saved worker scripts changed; refusing to change a captured run")
    if record["version"] != 2:
        raise ValueError("This launch predates safe submission recovery; start a new launch")
    profile = Cluster(**record["cluster"])
    if record["state"] == "partial":
        destination = Path(record.get("submission_directory", record["remote_run"]))
    else:
        require_terminal(profile, record["jobs"])
        generation = hashlib.sha256(",".join(record["jobs"]).encode()).hexdigest()[:24]
        destination = Path(record["remote_run"]) / f"resume-{generation}"
        # Prevent two clients (including copied receipts) from retrying the same jobs.
        remote(profile, f"mkdir {shlex.quote(str(destination))}")
        record.setdefault("history", []).append(
            {
                "jobs": record["jobs"],
                "submission_directory": record.get("submission_directory", record["remote_run"]),
            }
        )
        record.update(jobs=[], submission_directory=str(destination))
    record["state"] = "submitting"
    atomic_json(receipt, record)
    try:
        for index in range(len(record["jobs"]), record["workers"]):
            job = submit(profile, scripts[index], destination / f"worker-{index}.submission")
            record["jobs"].append(job)
            atomic_json(receipt, record)
            logger.info("Retry submitted worker=%d job=%s", index, job)
        record["state"] = "submitted"
        record.pop("error", None)
        atomic_json(receipt, record)
    except BaseException as exc:
        record.update(state="incomplete", error=str(exc))
        atomic_json(receipt, record)
        logger.exception("Retry uncertain; inspect %s before any further submission", destination)
        raise
    return receipt


def reconcile(receipt):
    """Recover accepted IDs and provably unsubmitted workers without launching anything."""
    receipt = Path(receipt).resolve()
    record = json.loads(receipt.read_text())
    if record["state"] not in ("submitting", "incomplete", "partial", "submitted"):
        raise ValueError("This launch has not reached submission")
    if record["version"] != 2:
        raise ValueError("This launch predates safe submission recovery; start a new launch")
    profile = Cluster(**record["cluster"])
    destination = record.get("submission_directory", record["remote_run"])
    script = """
import json, sys
from pathlib import Path
folder, code, count = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3])
if (code.parent / 'snapshot.sha256').read_text().strip() != sys.argv[4]:
    raise SystemExit('Source snapshot has not been verified')
if not (code / sys.argv[5]).is_file():
    raise SystemExit('Verified source/input bundle is unavailable; start a new launch')
rows = []
for index in range(count):
    path = folder / f'worker-{index}.submission'
    rows.append({'claimed': Path(str(path) + '.claim').is_dir(),
                 'output': path.read_text() if path.is_file() else None})
print(json.dumps(rows))
"""
    rows = json.loads(
        remote(
            profile,
            shlex.join(
                [
                    "python3",
                    "-c",
                    script,
                    destination,
                    str(Path(record["remote_run"]) / "code"),
                    str(record["workers"]),
                    record["archive_sha256"],
                    record.get("input_marker", "render_inputs/plan.json"),
                ]
            ),
        )
    )
    jobs = []
    missing = False
    if len(rows) != record["workers"]:
        raise ValueError("Remote submission records have an unexpected worker count")
    for index, row in enumerate(rows):
        ids = [
            line.split(";")[0]
            for line in (row["output"] or "").splitlines()
            if re.fullmatch(r"\d+(;[^\s]+)?", line)
        ]
        if len(ids) == 1 and not missing:
            jobs.append(ids[0])
        elif row["claimed"] or row["output"] is not None:
            raise ValueError(f"Worker {index} submission remains ambiguous; inspect {destination}")
        else:
            missing = True
    if jobs[: len(record["jobs"])] != record["jobs"] or len(set(jobs)) != len(jobs):
        raise ValueError("Remote submission records disagree with the local receipt")
    record.update(jobs=jobs, state="submitted" if len(jobs) == record["workers"] else "partial")
    record.pop("error", None)
    atomic_json(receipt, record)
    logger.info(
        "Reconciled accepted=%d pending=%d receipt=%s", len(jobs), record["workers"] - len(jobs), receipt
    )
    return receipt

"""Retry a completed allocation set using its exact saved source and worker scripts."""

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
    if record["state"] != "submitted" or len(record["jobs"]) != record["workers"]:
        raise ValueError("Submission is incomplete or uncertain; inspect remote submission records first")
    hashes = record.get("script_sha256", [])
    if len(hashes) != record["workers"]:
        raise ValueError("This receipt predates saved-script verification; launch a new run")
    scripts = [(receipt.parent / f"worker-{i}.sh").read_text() for i in range(record["workers"])]
    if [hashlib.sha256(s.encode()).hexdigest() for s in scripts] != hashes:
        raise ValueError("Saved worker scripts changed; refusing to change a captured run")
    profile = Cluster(**record["cluster"])
    require_terminal(profile, record["jobs"])
    generation = hashlib.sha256(",".join(record["jobs"]).encode()).hexdigest()[:24]
    destination = Path(record["remote_run"]) / f"resume-{generation}"
    # This permanent claim prevents two clients (including copied receipts) from retrying the same jobs.
    remote(profile, f"mkdir {shlex.quote(str(destination))}")
    record.setdefault("history", []).append(
        {"jobs": record["jobs"], "submission_directory": str(destination)}
    )
    record.update(jobs=[], state="submitting", submission_directory=str(destination))
    atomic_json(receipt, record)
    try:
        for index, script in enumerate(scripts):
            job = submit(profile, script, destination / f"worker-{index}.submission")
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

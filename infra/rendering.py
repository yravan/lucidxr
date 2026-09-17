"""Place distributed render work on scratch and publish results to shared storage."""

import logging
import shutil
import tempfile
from pathlib import Path

from .files import stage_input

logger = logging.getLogger(__name__)


def run_staged(manifest, item, output, scratch):
    from lucidxr.rendering.output import copy_result, read_result
    from lucidxr.rendering.replay import render_demo
    from lucidxr.rendering.spec import RenderSpec

    output, scratch = Path(output), Path(scratch)
    record = output / "results" / f"{item['work_id']}.json"
    if record.exists():
        read_result(record, expected_id=item["work_id"])
        logger.info("Already complete work=%s record=%s", item["work_id"], record)
        return record
    scratch.mkdir(parents=True, exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix=f"lucidxr-{item['work_id'][:8]}-", dir=scratch))
    logger.info("Stage work=%s scratch=%s destination=%s", item["work_id"], workspace, output)
    try:
        source = stage_input(
            Path(manifest).resolve().parent / item["source"],
            workspace / "source.npz",
            item["request"]["source_sha256"],
        )
        local_record = render_demo(
            source,
            workspace / "output",
            RenderSpec(**item["request"]["spec"]),
            expected_request=item["request"],
        )
        record = copy_result(local_record, output)
    except BaseException:
        logger.exception("Work failed; scratch retained while node permits: %s", workspace)
        raise
    try:
        shutil.rmtree(workspace)
    except OSError:
        logger.warning("Published result but could not remove scratch: %s", workspace, exc_info=True)
    logger.info("Published work=%s record=%s", item["work_id"], record)
    return record


def run_worker(manifest, worker_index, workers, output, scratch):
    """Process a fixed partition; a failed item does not discard later independent work."""
    from lucidxr.rendering.jobs import collect, load_plan

    items = load_plan(manifest)["items"]
    if not 0 <= worker_index < workers <= len(items):
        raise ValueError("Invalid worker partition")
    failed = []
    for index in range(worker_index, len(items), workers):
        try:
            run_staged(manifest, items[index], output, scratch)
        except Exception:
            logger.exception("Work failed index=%d work=%s", index, items[index]["work_id"])
            failed.append(items[index]["work_id"])
    if failed:
        raise RuntimeError(f"{len(failed)} render requests failed: {failed}")
    try:
        collect(manifest, output)
    except FileNotFoundError:
        logger.info("Worker complete; waiting for the rest of the work set")

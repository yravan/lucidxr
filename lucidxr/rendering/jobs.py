"""Explicit job manifests and the same replay worker on a laptop or Slurm node."""

import json
import logging
from pathlib import Path

from .output import publish_json, read_result
from .replay import render_demo
from .spec import RenderSpec, digest, request

logger = logging.getLogger(__name__)


def plan(sources, spec):
    items, inputs = {}, {}
    for source in sources:
        source = Path(source).expanduser().resolve()
        identity = request(source, spec)
        work_id = digest(identity)
        relative = f"inputs/{identity['source_sha256']}.npz"
        inputs[relative] = source
        items[work_id] = {"work_id": work_id, "source": relative, "request": identity}
    if not items:
        raise ValueError("Provide at least one recording")
    return {"version": 1, "items": list(items.values())}, inputs


def load_plan(path):
    value = json.loads(Path(path).read_text())
    if value["version"] != 1 or not value["items"]:
        raise ValueError("Unsupported or empty render plan")
    ids = []
    for item in value["items"]:
        if digest(item["request"]) != item["work_id"]:
            raise ValueError("Work identity mismatch")
        source = Path(item["source"])
        if source.is_absolute() or ".." in source.parts:
            raise ValueError("Plan source must be inside its bundle")
        RenderSpec(**item["request"]["spec"])
        ids.append(item["work_id"])
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate work IDs")
    return value


def run_item(manifest, index, output):
    manifest = Path(manifest).resolve()
    item = load_plan(manifest)["items"][index]
    logger.info("Worker item=%d work=%s", index, item["work_id"])
    return render_demo(
        manifest.parent / item["source"],
        output,
        RenderSpec(**item["request"]["spec"]),
        expected_request=item["request"],
    )


def collect(manifest, output):
    """Only an explicitly complete work set gets a collection record."""
    manifest, output = Path(manifest), Path(output)
    jobs = load_plan(manifest)
    results = []
    for item in jobs["items"]:
        record = output / "results" / f"{item['work_id']}.json"
        read_result(record, expected_id=item["work_id"])
        results.append(str(record.relative_to(output)))
    identity = digest([item["work_id"] for item in jobs["items"]])
    path = output / f"collection-{identity}.json"
    publish_json(
        path, {"version": 1, "work_ids": [item["work_id"] for item in jobs["items"]], "results": results}
    )
    logger.info("Collection complete items=%d record=%s", len(results), path)
    return path

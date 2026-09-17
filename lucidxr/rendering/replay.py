"""Render shared state or command playback through existing camera views."""

import logging
import os
import time
from pathlib import Path
from uuid import uuid4

from lucidxr.sim.demos import Demo
from lucidxr.sim.mujoco_env import MujocoEnv
from lucidxr.sim.mujoco_env.wrappers.camera_view import Camera, CameraView
from lucidxr.sim.playback import replay_frames

from .output import OutputWriter, publish_json, read_result, validate_attempt
from .spec import FORMAT_VERSION, digest, request

logger = logging.getLogger(__name__)


def render_demo(source, output, spec, *, assets=None, expected_request=None):
    """Return a verified completion record; interrupted attempts are never accepted."""
    source, output = Path(source).expanduser().resolve(), Path(output).expanduser().resolve()
    identity = request(source, spec, assets=assets)
    if expected_request is not None and digest(identity) != digest(expected_request):
        raise ValueError("Source, code or dependencies changed since planning")
    work_id = digest(identity)
    record = output / "results" / f"{work_id}.json"
    if record.exists():
        read_result(record, expected_id=work_id)
        logger.info("Already complete work=%s record=%s", work_id, record)
        return record
    demo = Demo(source)
    scene = spec.replay.make_scene(demo, assets=assets)
    attempt = output / "attempts" / uuid4().hex
    attempt.mkdir(parents=True)
    started = time.monotonic()
    logger.info("Render started work=%s source=%s attempt=%s", work_id, source, attempt)
    try:
        with MujocoEnv(scene) as env:
            env.reset()
            views = [
                CameraView(
                    env.model,
                    Camera(
                        name, width=spec.width, height=spec.height, products=spec.products, key=f"camera_{i}"
                    ),
                )
                for i, name in enumerate(spec.cameras)
            ]
            with OutputWriter(attempt, demo, spec, identity, env) as writer:
                for index in replay_frames(env, demo, spec.replay):
                    with env.rendering.batch():
                        writer.append(
                            [view.capture(env.rendering) for view in views], env.frame(), env.data.time
                        )
                    if (index + 1) % 100 == 0:
                        logger.info(
                            "Render progress work=%s frames=%d/%d", work_id, index + 1, len(demo.elapsed)
                        )
        artifacts = validate_attempt(attempt, identity, len(demo.elapsed))
        for artifact in artifacts:
            target = attempt / artifact["path"]
            with target.open("rb") as stream:
                os.fsync(stream.fileno())
            artifact["path"] = os.path.relpath(target, record.parent)
        result = {
            "format_version": FORMAT_VERSION,
            "work_id": work_id,
            "request": identity,
            "recording": demo.metadata,
            "frame_count": len(demo.elapsed),
            "duration_seconds": time.monotonic() - started,
            "artifacts": artifacts,
        }
        publish_json(record, result)
        read_result(record, expected_id=work_id)
        logger.info(
            "Render complete work=%s frames=%d seconds=%.2f record=%s",
            work_id,
            len(demo.elapsed),
            time.monotonic() - started,
            record,
        )
        return record
    except BaseException as exc:
        logger.exception("Render failed work=%s attempt=%s", work_id, attempt)
        try:
            publish_json(
                attempt / "failure.json",
                {"work_id": work_id, "error": str(exc), "error_type": type(exc).__name__},
            )
        except OSError:
            logger.exception("Could not persist failure record; retain process logs")
        raise

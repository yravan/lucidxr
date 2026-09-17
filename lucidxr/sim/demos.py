"""Versioned simulator recordings. Filesystem paths in, named state arrays out.

This is a recording/replay format, not a policy dataset or a training dataloader.
"""

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import mujoco
import numpy as np
from lxml import etree

from .mujoco_env.env import FRAME_FIELDS
from .scenes import make_scene

FORMAT_VERSION = 1


def scene_fingerprint(scene):
    """Hash normalized MJCF and referenced asset bytes, independent of asset root."""
    root = etree.fromstring(scene.to_xml().encode())
    compiler = root.find("compiler")
    for name in ("assetdir", "meshdir", "texturedir"):
        compiler.set(name, "ASSETS")
    digest = hashlib.sha256()
    files = {}
    for element in root.iter():
        name = element.get("file")
        if name is None:
            continue
        path = (scene.assets / name).resolve()
        if not path.is_relative_to(scene.assets.resolve()):
            raise ValueError(f"Recording assets must be inside the scene asset root: {name}")
        relative = path.relative_to(scene.assets.resolve()).as_posix()
        element.set("file", relative)
        files[relative] = path
    digest.update(etree.tostring(root, method="c14n"))
    for name, path in sorted(files.items()):
        digest.update(name.encode())
        with path.open("rb") as stream:
            digest.update(hashlib.file_digest(stream, "sha256").digest())
    return digest.hexdigest()


class DemoRecorder:
    """Validate incoming physical frames and save bounded episodes without pickle.

    elapsed is server receive time relative to the first frame, not simulation
    time. ctrl/mocap are commands at each captured state, not a shifted policy
    action/observation pair. A browser may emit frames less often than physics steps.
    """

    def __init__(self, env, scene_name, *, max_frames=30000, source="vuer-browser"):
        if type(max_frames) is not int or max_frames < 1:
            raise ValueError("max_frames must be positive")
        self.max_frames = max_frames
        self.shapes = {name: getattr(env.data, name).shape for name in FRAME_FIELDS}
        self.metadata = {
            "format_version": FORMAT_VERSION,
            "scene": scene_name,
            "scene_seed": env.scene.seed,
            "scene_options": dict(env.scene.options),
            "scene_fingerprint": scene_fingerprint(env.scene),
            "reference_mujoco_version": mujoco.__version__,
            "source": source,
            "timing": "server-receive-seconds",
            "fields": {name: list(shape) for name, shape in self.shapes.items()},
        }
        json.dumps(self.metadata, allow_nan=False)
        self.frames = []
        self.timestamps = []

    def append(self, frame, timestamp):
        if len(self.frames) >= self.max_frames:
            raise ValueError("Episode frame limit reached; save or discard before recording more")
        if not np.isfinite(timestamp) or (self.timestamps and timestamp <= self.timestamps[-1]):
            raise ValueError("Frame timestamps must be finite and strictly increasing")
        values = {}
        for name, shape in self.shapes.items():
            value = frame.get(name, [])
            array = np.asarray(value, dtype=np.float64)
            # Vuer serializes model arrays flat; also accept native-shaped frames.
            if array.size != np.prod(shape) or not np.isfinite(array).all():
                raise ValueError(f"Invalid {name}: expected {shape}")
            array = array.reshape(shape).copy()
            if name == "mocap_quat" and np.any(np.linalg.norm(array, axis=-1) < 1e-8):
                raise ValueError("Mocap quaternions must be nonzero")
            values[name] = array
        self.frames.append(values)
        self.timestamps.append(float(timestamp))

    def clear(self):
        self.frames.clear()
        self.timestamps.clear()

    def save(self, directory):
        """Commit one NPZ atomically without replacing an existing demo; retain on failure."""
        if not self.frames:
            return None
        directory = Path(directory).expanduser()
        directory.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc)
        path = directory / f"{now:%Y%m%dT%H%M%S}-{uuid4().hex}.npz"
        metadata = {**self.metadata, "created_at": now.isoformat(), "frame_count": len(self.frames)}
        arrays = {name: np.stack([frame[name] for frame in self.frames]) for name in FRAME_FIELDS}
        arrays["elapsed"] = np.asarray(self.timestamps) - self.timestamps[0]
        arrays["metadata"] = np.array(json.dumps(metadata, allow_nan=False))
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                dir=directory, prefix=".recording-", suffix=".tmp", delete=False
            ) as stream:
                temp_path = Path(stream.name)
                np.savez_compressed(stream, **arrays)
                stream.flush()
                os.fsync(stream.fileno())
            # Same-filesystem hard link publishes the completed file without overwrite.
            os.link(temp_path, path)
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
        self.clear()
        return path


class Demo:
    """Load and validate one state recording; no network or infrastructure dependency."""

    def __init__(self, path):
        with np.load(Path(path).expanduser(), allow_pickle=False) as data:
            self.metadata = json.loads(str(data["metadata"].item()))
            if self.metadata.get("format_version") != FORMAT_VERSION:
                raise ValueError("Unsupported recording format version")
            self.frames = {name: data[name].copy() for name in FRAME_FIELDS}
            self.elapsed = data["elapsed"].copy()
        count = self.metadata["frame_count"]
        if type(count) is not int or count < 1 or self.elapsed.shape != (count,):
            raise ValueError("Invalid frame count")
        if not np.isfinite(self.elapsed).all() or self.elapsed[0] != 0 or np.any(np.diff(self.elapsed) <= 0):
            raise ValueError("Invalid recording timestamps")
        for name, values in self.frames.items():
            shape = (count, *self.metadata["fields"][name])
            if values.dtype != np.float64 or values.shape != shape or not np.isfinite(values).all():
                raise ValueError(f"Invalid recorded {name}")

    def scene(self, *, assets=None):
        scene = make_scene(
            self.metadata["scene"],
            assets=assets,
            seed=self.metadata["scene_seed"],
            **self.metadata["scene_options"],
        )
        if scene_fingerprint(scene) != self.metadata["scene_fingerprint"]:
            raise ValueError("Scene XML or assets differ from the recording; use the matching code/assets")
        return scene

    def frame(self, index):
        return {name: values[index].copy() for name, values in self.frames.items()}

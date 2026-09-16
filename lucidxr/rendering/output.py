"""Streaming paired video/arrays and verified, immutable completion records."""

import json
import os
import tempfile
from contextlib import ExitStack
from fractions import Fraction
from pathlib import Path

import av
import h5py
import numpy as np

from .spec import FORMAT_VERSION, digest, file_hash


def publish_json(path, value):
    """Publish without overwrite on a shared filesystem; existing records win."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(json.dumps(value, sort_keys=True, indent=2, allow_nan=False).encode())
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, path)
            return True
        except FileExistsError:
            return False
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


class OutputWriter:
    """Own all writers in one attempt; no shared HDF5 appenders or per-frame files."""

    def __init__(self, directory, demo, spec, identity):
        self.directory, self.demo, self.spec, self.identity = Path(directory), demo, spec, identity
        self.stack = ExitStack()
        self.count = 0
        self.videos = []

    def __enter__(self):
        try:
            self.h5 = self.stack.enter_context(h5py.File(self.directory / "frames.h5", "x"))
            self.h5.attrs["metadata"] = json.dumps(
                {
                    "format_version": FORMAT_VERSION,
                    "request": self.identity,
                    "recording": self.demo.metadata,
                    "timing": "one-video-frame-per-source-frame; source elapsed is authoritative",
                    "camera_convention": "OpenCV: x right, y down, z forward; C2W",
                    "commands": "captured command fields, not inferred behavior-cloning targets",
                },
                sort_keys=True,
            )
            count = len(self.demo.elapsed)
            self.h5.create_dataset("elapsed", data=self.demo.elapsed)
            self.h5.create_dataset("source_frame", data=np.arange(count, dtype=np.int64))
            for name, array in self.demo.frames.items():
                self.h5.create_dataset(f"frames/{name}", data=array)
            for index, name in enumerate(self.spec.cameras):
                key = f"camera_{index}"
                group = self.h5.create_group(key)
                filename = f"{key}.mp4"
                group.attrs.update(name=name, video=filename, fps=self.spec.fps)
                group.create_dataset("video_frame", data=np.arange(count, dtype=np.int64))
                group.create_dataset("K", (count, 3, 3), dtype="f8")
                group.create_dataset("C2W", (count, 4, 4), dtype="f8")
                for product in set(self.spec.products) - {"rgb"}:
                    group.create_dataset(
                        product,
                        (count, self.spec.height, self.spec.width),
                        dtype="f4" if product == "depth" else "i4",
                        chunks=(1, self.spec.height, self.spec.width),
                        compression="lzf",
                    )
                container = self.stack.enter_context(av.open(str(self.directory / filename), "w"))
                stream = container.add_stream("libx264", rate=self.spec.fps)
                stream.width, stream.height, stream.pix_fmt = self.spec.width, self.spec.height, "yuv420p"
                stream.codec_context.thread_count = 1
                stream.codec_context.gop_size = self.spec.fps
                stream.codec_context.max_b_frames = 0
                stream.options = {"crf": "18", "preset": "fast"}
                self.videos.append((container, stream))
            return self
        except BaseException:
            self.stack.close()
            raise

    def append(self, captures):
        if len(captures) != len(self.spec.cameras) or self.count >= len(self.demo.elapsed):
            raise ValueError("Camera/frame count mismatch")
        for index, (capture, (container, stream)) in enumerate(zip(captures, self.videos, strict=True)):
            key = f"camera_{index}"
            rgb = capture[f"{key}/rgb"]
            if rgb.shape != (self.spec.height, self.spec.width, 3) or rgb.dtype != np.uint8:
                raise ValueError("Invalid RGB frame")
            frame = av.VideoFrame.from_ndarray(rgb, format="rgb24")
            frame.pts, frame.time_base = self.count, Fraction(1, self.spec.fps)
            for packet in stream.encode(frame):
                container.mux(packet)
            for product in ("K", "C2W", *[p for p in self.spec.products if p != "rgb"]):
                self.h5[f"{key}/{product}"][self.count] = capture[f"{key}/{product}"]
        self.count += 1

    def __exit__(self, exc_type, exc, tb):
        try:
            if exc_type is None:
                if self.count != len(self.demo.elapsed):
                    raise ValueError("Incomplete render")
                for container, stream in self.videos:
                    for packet in stream.encode():
                        container.mux(packet)
        finally:
            self.stack.close()


def validate_attempt(directory, identity, frame_count):
    """Decode before publication; reject truncated video and mismatched array frames."""
    directory = Path(directory)
    spec = identity["spec"]
    artifacts = []
    with h5py.File(directory / "frames.h5", "r") as h5:
        if digest(json.loads(h5.attrs["metadata"])["request"]) != digest(identity):
            raise ValueError("HDF5 request mismatch")
        if h5["elapsed"].shape != (frame_count,):
            raise ValueError("HDF5 frame count mismatch")
        for index, name in enumerate(spec["cameras"]):
            key = f"camera_{index}"
            if h5[key].attrs["name"] != name:
                raise ValueError("Camera metadata mismatch")
            video = directory / str(h5[key].attrs["video"])
            if video.parent != directory:
                raise ValueError("Video must be beside its HDF5 file")
            count = 0
            with av.open(str(video)) as container:
                for count, frame in enumerate(container.decode(video=0), start=1):
                    if (frame.width, frame.height) != (spec["width"], spec["height"]):
                        raise ValueError("Video dimensions mismatch")
                    if (
                        frame.pts is None
                        or abs(float(frame.pts * frame.time_base) - (count - 1) / spec["fps"]) > 1e-6
                    ):
                        raise ValueError("Video timestamp mismatch")
            if count != frame_count:
                raise ValueError("Video frame count mismatch")
            artifacts.append(video)
    artifacts.append(directory / "frames.h5")
    return [{"path": p.name, "sha256": file_hash(p), "bytes": p.stat().st_size} for p in artifacts]


def read_result(path, *, expected_id=None):
    """A completion record is the entry point; paths alone carry no semantics."""
    path = Path(path).resolve()
    result = json.loads(path.read_text())
    if result["format_version"] != FORMAT_VERSION or digest(result["request"]) != result["work_id"]:
        raise ValueError("Invalid completion record")
    if expected_id is not None and result["work_id"] != expected_id:
        raise ValueError("Completion record belongs to another request")
    for artifact in result["artifacts"]:
        target = (path.parent / artifact["path"]).resolve()
        if not target.is_relative_to(path.parent.parent) or not target.is_file():
            raise ValueError("Missing artifact or path outside output root")
        if target.stat().st_size != artifact["bytes"] or file_hash(target) != artifact["sha256"]:
            raise ValueError(f"Artifact is corrupt: {target}")
    return result

"""Verify closed render results, then decode once into an immutable derived cache."""

import json
import logging
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

import av
import h5py
import numpy as np

from lucidxr.rendering.output import read_result
from lucidxr.sim.demos import scene_fingerprint
from lucidxr.sim.playback import control_layout
from lucidxr.sim.scenes import make_scene
from training.simulation import SimulationAdapter

from .images import resize_rgb
from .manifest import file_hash, fingerprint, load_manifest

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DataSpec:
    cameras: tuple[str, ...]
    joints: tuple[str, ...]
    control_period: float
    image_size: int = 128

    def __post_init__(self):
        for key in ("cameras", "joints"):
            values = tuple(getattr(self, key))
            object.__setattr__(self, key, values)
            if (
                not values
                or len(set(values)) != len(values)
                or any(not isinstance(v, str) or not v for v in values)
            ):
                raise ValueError(f"Provide unique nonempty {key}")
        if not np.isfinite(self.control_period) or self.control_period <= 0:
            raise ValueError("Control period must be positive simulation seconds")
        if type(self.image_size) is not int or self.image_size < 32 or self.image_size % 32:
            raise ValueError("Image size must be a multiple of 32")


@dataclass(frozen=True)
class EpisodeInput:
    result: str
    group: str
    split: str

    def __post_init__(self):
        if not self.group or self.split not in ("train", "validation"):
            raise ValueError("Each recording needs an explicit collection group and train/validation split")


def prepare(recipe, destination):
    """Recipe paths resolve relative to its JSON file; destination must not exist."""
    recipe, destination = Path(recipe).resolve(), Path(destination).resolve()
    value = json.loads(recipe.read_text())
    if set(value) != {"data", "episodes"}:
        raise ValueError("Recipe requires exactly data and episodes")
    spec = DataSpec(**value["data"])
    entries = [EpisodeInput(**item) for item in value["episodes"]]
    if not entries or not any(e.split == "train" for e in entries):
        raise ValueError("Provide at least one training episode")
    if destination.exists():
        raise FileExistsError(f"Use a new cache destination: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    manifest = {"version": 1, "data": asdict(spec), "episodes": [], "files": {}}
    contract, statistics, sources, groups, work_ids = None, {}, {}, {}, set()
    with tempfile.TemporaryDirectory(dir=destination.parent, prefix=".preparing-") as temporary:
        root = Path(temporary) / "cache"
        root.mkdir()
        for entry in entries:
            path = (recipe.parent / entry.result).resolve()
            result = read_result(path)
            source, work_id = result["request"]["source_sha256"], result["work_id"]
            if work_id in work_ids:
                raise ValueError("Duplicate render result in recipe")
            work_ids.add(work_id)
            pair = (entry.group, entry.split)
            if (
                sources.setdefault(source, pair) != pair
                or groups.setdefault(entry.group, entry.split) != entry.split
            ):
                raise ValueError("Source recordings and collection groups cannot cross splits")
            files = {Path(a["path"]).name: path.parent / a["path"] for a in result["artifacts"]}
            if len(files) != len(result["artifacts"]) or "frames.h5" not in files:
                raise ValueError("Expected distinct video/array artifacts")
            target = root / work_id
            target.mkdir()
            logger.info(
                "Prepare work=%s source=%s split=%s frames=%d",
                work_id,
                source,
                entry.split,
                result["frame_count"],
            )
            current, state, actions, count = _episode(files, target, spec, result, contract)
            contract = current if contract is None else contract
            if current != contract:
                raise ValueError("Robot, controls, cameras or render geometry differ between episodes")
            if entry.split == "train":
                for name, array in (("state", state[:-1]), ("action", actions)):
                    low, high = array.min(axis=0), array.max(axis=0)
                    statistics[f"{name}_min"] = np.minimum(statistics.get(f"{name}_min", low), low)
                    statistics[f"{name}_max"] = np.maximum(statistics.get(f"{name}_max", high), high)
            manifest["episodes"].append(
                {"id": work_id, "source": source, "group": entry.group, "split": entry.split, "frames": count}
            )
            for file in sorted(target.iterdir()):
                manifest["files"][file.relative_to(root).as_posix()] = {
                    "bytes": file.stat().st_size,
                    "sha256": file_hash(file),
                }
        manifest.update(
            contract=contract, statistics={key: value.tolist() for key, value in statistics.items()}
        )
        manifest["fingerprint"] = fingerprint(manifest)
        (root / "manifest.json").write_text(json.dumps(manifest, indent=2, allow_nan=False))
        load_manifest(root, verify=True)
        # Flush complete artifacts before publishing the directory on the same filesystem.
        for file in root.rglob("*"):
            if file.is_file():
                with file.open("rb") as stream:
                    os.fsync(stream.fileno())
        if destination.exists():
            raise FileExistsError(destination)
        root.rename(destination)
    logger.info("Prepared cache=%s fingerprint=%s", destination, manifest["fingerprint"])
    return destination


def _episode(files, target, spec, result, contract):
    request = result["request"]
    render, recording = request["spec"], result["recording"]
    replay = render["replay"]
    explicit = replay["scene"] is not None
    scene = make_scene(
        replay["scene"] if explicit else recording["scene"],
        seed=replay["seed"] if explicit else recording["scene_seed"],
        **(replay["options"] if explicit else recording["scene_options"]),
    )
    expected = request["target_scene_fingerprint"] if explicit else recording["scene_fingerprint"]
    if scene_fingerprint(scene) != expected:
        raise ValueError("Scene/assets changed; prepare with the code matching the render")
    model = scene.compile()
    adapter = SimulationAdapter(
        model,
        spec.joints,
        controls=None if contract is None else contract["controls"],
        state_schema=None if contract is None else contract["state_schema"],
    )
    current = {
        "controls": adapter.codec.controls,
        "state_schema": adapter.state_schema,
        "state_dim": adapter.state_dim,
        "action_dim": adapter.codec.dimension,
        "rotation_indices": adapter.codec.rotation_indices,
        "width": render["width"],
        "height": render["height"],
    }
    count = result["frame_count"]
    if count < 2 or recording["command_alignment"] != "interval-ending-at-frame":
        raise ValueError("Training needs at least one observation/next-command pair")
    with h5py.File(files["frames.h5"], "r") as h5:
        metadata = json.loads(h5.attrs["metadata"])
        if metadata["request"] != request or metadata["controls"] != control_layout(model):
            raise ValueError("Rendered metadata does not match the compiled model")
        times = h5["simulation_time"][:]
        if (
            times.shape != (count,)
            or not np.isfinite(times).all()
            or not np.allclose(np.diff(times), spec.control_period, rtol=0, atol=1e-7)
            or not np.allclose(times - times[0], h5["elapsed"][:], rtol=0, atol=1e-7)
        ):
            raise ValueError("Recording is not uniformly sampled at the declared control period")
        frames = {key: h5[f"frames/{key}"][:] for key in ("qpos", "qvel", "ctrl", "mocap_pos", "mocap_quat")}
        shapes = {
            "qpos": (model.nq,),
            "qvel": (model.nv,),
            "ctrl": (model.nu,),
            "mocap_pos": (model.nmocap, 3),
            "mocap_quat": (model.nmocap, 4),
        }
        for name, shape in shapes.items():
            if frames[name].shape != (count, *shape) or not np.isfinite(frames[name]).all():
                raise ValueError(f"Invalid rendered state: {name}")
        state, actions = adapter.state(frames), adapter.action(frames)[1:]
        # Action row t is the command applied AFTER observation t, ending at t+1.
        np.save(target / "state.npy", state, allow_pickle=False)
        np.save(target / "actions.npy", actions, allow_pickle=False)
        images = np.lib.format.open_memmap(
            target / "images.npy",
            mode="w+",
            dtype="u1",
            shape=(count, len(spec.cameras), 3, spec.image_size, spec.image_size),
        )
        for camera_index, camera in enumerate(spec.cameras):
            if camera not in render["cameras"]:
                raise ValueError(f"Missing camera: {camera}")
            group = h5[f"camera_{render['cameras'].index(camera)}"]
            if group.attrs["name"] != camera or not np.array_equal(group["video_frame"][:], np.arange(count)):
                raise ValueError("Camera frame alignment mismatch")
            video = files[str(group.attrs["video"])]
            decoded = 0
            with av.open(str(video)) as container:
                container.streams.video[0].codec_context.thread_count = 1
                for index, frame in enumerate(container.decode(video=0)):
                    if (
                        index >= count
                        or (frame.width, frame.height) != (render["width"], render["height"])
                        or frame.pts is None
                        or abs(float(frame.pts * frame.time_base) - index / render["fps"]) > 1e-6
                    ):
                        raise ValueError("Video dimensions, count or timestamps mismatch")
                    images[index, camera_index] = resize_rgb(frame, spec.image_size)
                    decoded += 1
            if decoded != count:
                raise ValueError("Incomplete video")
        images.flush()
        del images
    return current, state, actions, count

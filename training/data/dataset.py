"""Read-only windows; no decoding, cache writes, simulator or network operations."""

import os
from collections import OrderedDict
from pathlib import Path

import numpy as np
from torch.utils.data import Dataset, Sampler

from .manifest import load_manifest


class Windows(Dataset):
    def __init__(self, directory, split, *, observation_steps, horizon, open_episodes=8):
        self.root = Path(directory)
        self.manifest = load_manifest(self.root)
        self.episodes = [e for e in self.manifest["episodes"] if e["split"] == split]
        if not self.episodes or min(observation_steps, horizon, open_episodes) < 1:
            raise ValueError("Windows need episodes and positive history/horizon/cache sizes")
        self.observation_steps, self.horizon, self.open_episodes = observation_steps, horizon, open_episodes
        self.sources = {}
        for index, episode in enumerate(self.episodes):
            self.sources.setdefault(episode["source"], []).append(index)
        self.sources = list(self.sources.values())
        for variants in self.sources:
            if len({self.episodes[i]["frames"] for i in variants}) != 1:
                raise ValueError("Render variants disagree on physical trajectory length")
        self.ends = np.cumsum([self.episodes[v[0]]["frames"] - 1 for v in self.sources])
        self._arrays = OrderedDict()
        self._pid = os.getpid()

    def __len__(self):
        # More visual variants do not increase a physical trajectory's weight.
        return int(self.ends[-1])

    def __getstate__(self):
        return {**self.__dict__, "_arrays": OrderedDict()}

    def _open(self, episode):
        if self._pid != os.getpid():
            self._arrays.clear()
            self._pid = os.getpid()
        key = episode["id"]
        if key not in self._arrays:
            arrays = {
                name: np.load(self.root / key / f"{name}.npy", mmap_mode="r", allow_pickle=False)
                for name in ("images", "state", "actions")
            }
            n, data, contract = episode["frames"], self.manifest["data"], self.manifest["contract"]
            shapes = {
                "images": (n, len(data["cameras"]), 3, data["image_size"], data["image_size"]),
                "state": (n, contract["state_dim"]),
                "actions": (n - 1, contract["action_dim"]),
            }
            for name, array in arrays.items():
                if array.shape != shapes[name] or array.dtype != (
                    np.uint8 if name == "images" else np.float32
                ):
                    raise ValueError(f"Invalid cache array: {key}/{name}")
            self._arrays[key] = arrays
            if len(self._arrays) > self.open_episodes:
                # Returned windows are copies, so eviction cannot invalidate a batch.
                self._arrays.popitem(last=False)
        self._arrays.move_to_end(key)
        return self._arrays[key]

    def __getitem__(self, key):
        # Samplers supply a variant choice, keeping worker state out of sampling.
        index, variant = key if isinstance(key, tuple) else (key, 0)
        if not 0 <= index < len(self):
            raise IndexError(index)
        source = int(np.searchsorted(self.ends, index, side="right"))
        anchor = index - (int(self.ends[source - 1]) if source else 0)
        choices = self.sources[source]
        episode = self.episodes[choices[variant % len(choices)]]
        arrays = self._open(episode)
        history = np.arange(anchor - self.observation_steps + 1, anchor + 1)
        future = np.arange(anchor, anchor + self.horizon)
        history_valid, action_valid = history >= 0, future < episode["frames"] - 1
        history = np.maximum(history, 0)
        future = np.minimum(future, episode["frames"] - 2)
        return {
            "obs": {
                "images": arrays["images"][history],
                "state": arrays["state"][history],
                "valid": history_valid,
            },
            "actions": arrays["actions"][future],
            "action_valid": action_valid,
        }


class Batches(Sampler):
    """Independent deterministic batches keyed by consumed step, immune to prefetch.

    Sample physical anchors uniformly with replacement, then a visual variant
    uniformly. Resume at the completed optimizer-step count, never worker RNG state.
    """

    def __init__(self, dataset, batch_size, steps, *, start=0, seed=0):
        if batch_size < 1 or not 0 <= start <= steps:
            raise ValueError("Invalid batch size or training interval")
        self.dataset, self.batch_size, self.steps, self.start, self.seed = (
            dataset,
            batch_size,
            steps,
            start,
            seed,
        )

    def __len__(self):
        return self.steps - self.start

    def __iter__(self):
        for step in range(self.start, self.steps):
            rng = np.random.default_rng(np.random.SeedSequence([self.seed, step]))
            indices = rng.integers(len(self.dataset), size=self.batch_size)
            sources = np.searchsorted(self.dataset.ends, indices, side="right")
            yield [
                (int(index), int(rng.integers(len(self.dataset.sources[source]))))
                for index, source in zip(indices, sources, strict=True)
            ]

"""Timing, padding, split isolation and deterministic multi-worker reads."""

import json

import numpy as np
import pytest

torch = pytest.importorskip("torch")
from torch.utils.data import DataLoader  # noqa: E402

from training.data.dataset import Batches, Windows  # noqa: E402
from training.data.manifest import file_hash, fingerprint, load_manifest  # noqa: E402


@pytest.fixture
def cache(tmp_path):
    manifest = {
        "version": 1,
        "episodes": [],
        "files": {},
        "data": {"cameras": ["wrist"], "image_size": 32},
        "contract": {"state_dim": 1, "action_dim": 1},
    }
    for index, source in enumerate(("a", "a", "b")):
        name = str(index)
        (tmp_path / name).mkdir()
        arrays = {
            "state": np.arange(5, dtype=np.float32)[:, None],
            "actions": np.arange(1, 5, dtype=np.float32)[:, None],
            "images": np.full((5, 1, 3, 32, 32), index, dtype=np.uint8),
        }
        for key, array in arrays.items():
            path = tmp_path / name / f"{key}.npy"
            np.save(path, array)
            manifest["files"][f"{name}/{key}.npy"] = {"bytes": path.stat().st_size, "sha256": file_hash(path)}
        manifest["episodes"].append(
            {"id": name, "source": source, "group": source, "split": "train", "frames": 5}
        )
    manifest["fingerprint"] = fingerprint(manifest)
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    return tmp_path


def test_alignment_padding_and_variants(cache):
    data = Windows(cache, "train", observation_steps=3, horizon=3, open_episodes=1)
    assert len(data) == 8  # Two physical trajectories, although there are three renders.
    first, last = data[(0, 1)], data[3]
    np.testing.assert_array_equal(first["obs"]["valid"], [False, False, True])
    np.testing.assert_array_equal(first["actions"][:, 0], [1, 2, 3])
    np.testing.assert_array_equal(last["obs"]["state"][:, 0], [1, 2, 3])
    np.testing.assert_array_equal(last["actions"][:, 0], [4, 4, 4])
    np.testing.assert_array_equal(last["action_valid"], [True, False, False])
    assert first["obs"]["images"].mean() == 1
    first["obs"]["images"][:] = 99
    assert data[(0, 1)]["obs"]["images"].mean() == 1
    assert len(data._arrays) == 1


def test_group_leakage_fails(cache):
    value = json.loads((cache / "manifest.json").read_text())
    value["episodes"][1]["split"] = "validation"
    value.pop("fingerprint")
    value["fingerprint"] = fingerprint(value)
    (cache / "manifest.json").write_text(json.dumps(value))
    with pytest.raises(ValueError, match="crosses|variants"):
        load_manifest(cache)


def test_same_size_corruption_fails_verification(cache):
    path = cache / "0/state.npy"
    original = bytearray(path.read_bytes())
    original[-1] ^= 1
    path.write_bytes(original)
    with pytest.raises(ValueError, match="Corrupt"):
        load_manifest(cache, verify=True)


def test_resume_batches_match_with_two_workers(cache):
    torch.set_num_threads(2)
    data = Windows(cache, "train", observation_steps=2, horizon=3)
    full = list(Batches(data, 2, 8, seed=17))
    assert list(Batches(data, 2, 8, start=3, seed=17)) == full[3:]
    single = list(DataLoader(data, batch_sampler=Batches(data, 2, 4, seed=17), num_workers=0))
    multiple = list(DataLoader(data, batch_sampler=Batches(data, 2, 4, seed=17), num_workers=2))
    for left, right in zip(single, multiple, strict=True):
        torch.testing.assert_close(left["actions"], right["actions"])
        torch.testing.assert_close(left["obs"]["images"], right["obs"]["images"])

"""Real optimizer/EMA/checkpoint resume must reproduce an uninterrupted run."""

import json
from dataclasses import replace

import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("diffusers")

from training.checkpoint import load_checkpoint  # noqa: E402
from training.config import TrainConfig  # noqa: E402
from training.data.manifest import fingerprint  # noqa: E402
from training.tests.test_data import cache  # noqa: E402, F401
from training.trainer import train  # noqa: E402


def test_checkpoint_resume_reproduces_training_and_ema(cache, tmp_path):  # noqa: F811
    manifest = json.loads((cache / "manifest.json").read_text())
    manifest["contract"]["rotation_indices"] = []
    manifest["statistics"] = {
        "state_min": [0.0],
        "state_max": [3.0],
        "action_min": [1.0],
        "action_max": [4.0],
    }
    manifest["episodes"][2]["split"] = "validation"
    manifest.pop("fingerprint")
    manifest["fingerprint"] = fingerprint(manifest)
    (cache / "manifest.json").write_text(json.dumps(manifest))
    config = TrainConfig(
        steps=6,
        warmup_steps=1,
        observation_steps=2,
        horizon=3,
        width=32,
        depth=1,
        batch_size=2,
        workers=0,
        cpu_threads=2,
        checkpoint_every=3,
        validation_every=3,
        validation_batches=2,
        log_every=3,
        device="cpu",
    )
    full = train(cache, tmp_path / "full", config)
    partial = train(cache, tmp_path / "resumed", config, stop_after=3)
    assert load_checkpoint(partial)["step"] == 3
    assert json.loads((partial.parent / "status.json").read_text())["state"] == "interrupted"
    resumed = train(cache, tmp_path / "resumed", config, resume=True)
    a, b = load_checkpoint(full), load_checkpoint(resumed)
    for group in ("policy", "ema"):
        for name in a[group]:
            torch.testing.assert_close(a[group][name], b[group][name], rtol=0, atol=0)
    for parameter in a["optimizer"]["state"]:
        for name, value in a["optimizer"]["state"][parameter].items():
            torch.testing.assert_close(value, b["optimizer"]["state"][parameter][name], rtol=0, atol=0)
    assert a["step"] == b["step"] == 6
    torch.testing.assert_close(a["noise_rng"], b["noise_rng"])
    with pytest.raises(ValueError, match="same config"):
        train(cache, tmp_path / "resumed", replace(config, batch_size=3), resume=True)
    with pytest.raises(FileExistsError, match="resume explicitly"):
        train(cache, tmp_path / "resumed", config)


def test_interrupted_checkpoint_write_retains_previous_state(tmp_path, monkeypatch):
    from training.checkpoint import atomic_save

    path = tmp_path / "last.pt"
    atomic_save(path, {"version": 1, "step": 5}, tensor=True)

    def interrupted(value, stream):
        stream.write(b"incomplete")
        raise OSError("injected interrupted checkpoint write")

    monkeypatch.setattr(torch, "save", interrupted)
    with pytest.raises(OSError, match="interrupted"):
        atomic_save(path, {"version": 1, "step": 6}, tensor=True)
    assert load_checkpoint(path)["step"] == 5
    assert list(tmp_path.iterdir()) == [path]

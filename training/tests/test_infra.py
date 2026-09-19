"""Cache staging and real worker signal delivery without a cluster allocation."""

import json
import os
import shlex
import signal
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest

pytest.importorskip("torch")
pytest.importorskip("jaynes")

from infra.jaynes import BatchSlurm  # noqa: E402
from infra.training import training_cache  # noqa: E402
from training.data.manifest import load_manifest  # noqa: E402
from training.tests.test_data import cache  # noqa: E402, F401


def test_training_scratch_excludes_unlisted_files_and_falls_back(cache, tmp_path, monkeypatch):  # noqa: F811
    manifest = load_manifest(cache)
    (cache / "unlisted.txt").write_text("not part of the dataset")
    scratch = tmp_path / "scratch"
    monkeypatch.setenv("SLURM_TMPDIR", str(scratch))
    with training_cache(cache, manifest["fingerprint"]) as local:
        assert local != cache and not (local / "unlisted.txt").exists()
        assert load_manifest(local, verify=True)["fingerprint"] == manifest["fingerprint"]
    assert not local.exists()
    monkeypatch.setattr("infra.training.shutil.disk_usage", lambda _: SimpleNamespace(free=0))
    with training_cache(cache, manifest["fingerprint"]) as local:
        assert local == cache
    with pytest.raises(ValueError, match="captured job"):
        with training_cache(cache, "wrong"):
            pass


def test_exec_worker_receives_batch_signal_and_preserves_exit_status(tmp_path):
    worker = tmp_path / "worker.py"
    ready = tmp_path / "ready.json"
    worker.write_text(
        "import json, os, signal, sys\nfrom pathlib import Path\n"
        "signal.signal(signal.SIGUSR1, lambda *args: sys.exit(7))\n"
        f"Path({str(ready)!r}).write_text(json.dumps(os.getpid()))\n"
        "signal.pause()\n"
    )
    runner = BatchSlurm(
        work_dir=str(tmp_path), entry_script="exec " + shlex.join([sys.executable, str(worker)]), n_cpu=1
    )
    runner.build(lambda: None)
    script = runner.run_script.split("<<<'", 1)[1][:-1]
    with subprocess.Popen(["bash", "-c", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
        try:
            deadline = time.monotonic() + 10
            while not ready.exists() and process.poll() is None and time.monotonic() < deadline:
                time.sleep(0.01)
            assert ready.exists()
            assert json.loads(ready.read_text()) == process.pid
            os.kill(process.pid, signal.SIGUSR1)
            assert process.wait(timeout=10) == 7
        finally:
            if process.poll() is None:
                process.kill()


def test_cache_transfer_verifier_runs_before_publication(cache, tmp_path, monkeypatch):  # noqa: F811
    from infra.training import stage_cache

    profile = SimpleNamespace(root=str(tmp_path / "remote"), user="test", host="engaging")
    original_run = subprocess.run
    corrupt = False

    def local_run(command, **kwargs):
        if command[0] == "rsync":
            command = list(command)
            index = command.index("-e")
            del command[index : index + 2]
            command[-1] = command[-1].split(":", 1)[1]
            result = original_run(command, **kwargs)
            if corrupt:
                from pathlib import Path

                file = Path(command[-1]) / "0/state.npy"
                content = bytearray(file.read_bytes())
                content[-1] ^= 1
                file.write_bytes(content)
            return result
        return original_run(command, **kwargs)

    monkeypatch.setattr("infra.training.subprocess.run", local_run)
    monkeypatch.setattr(
        "infra.training.remote",
        lambda profile, script: subprocess.check_output(["bash", "-c", script], text=True),
    )
    target, identity = stage_cache(profile, cache)
    assert load_manifest(target, verify=True)["fingerprint"] == identity
    assert stage_cache(profile, cache)[0] == target
    profile.root = str(tmp_path / "failed-remote")
    corrupt = True
    with pytest.raises(subprocess.CalledProcessError):
        stage_cache(profile, cache)
    assert not (tmp_path / "failed-remote/training-cache" / identity).exists()

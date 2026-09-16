"""Focused transfer-failure and retry contracts."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from infra.files import stage_input
from infra.recovery import require_terminal
from infra.rendering import run_staged
from lucidxr.rendering.jobs import plan
from lucidxr.rendering.output import read_result
from lucidxr.rendering.spec import RenderSpec
from lucidxr.tests.test_rendering import recording


def test_failed_transfer_retains_scratch_and_retry_publishes_once(tmp_path, monkeypatch):
    source = recording(tmp_path)
    value, inputs = plan([source], RenderSpec(("wrist",), 32, 24))
    bundle = tmp_path / "bundle"
    for relative, original in inputs.items():
        target = bundle / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(original.read_bytes())
    manifest = bundle / "plan.json"
    manifest.write_text(json.dumps(value))
    item = value["items"][0]
    output, scratch = tmp_path / "shared", tmp_path / "scratch"
    import shutil

    original_copy = shutil.copyfile

    def interrupt_video(source, destination, *args, **kwargs):
        if Path(destination).suffix == ".mp4":
            Path(destination).write_bytes(b"partial")
            raise OSError("injected interrupted transfer")
        return original_copy(source, destination, *args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr("lucidxr.rendering.output.shutil.copyfile", interrupt_video)
        with pytest.raises(OSError, match="interrupted"):
            run_staged(manifest, item, output, scratch)
    assert not list(output.glob("results/*.json"))
    retained = list(scratch.iterdir())
    assert len(retained) == 1
    record = run_staged(manifest, item, output, scratch)
    read_result(record, expected_id=item["work_id"])
    assert list(scratch.iterdir()) == retained  # only failed work is retained
    attempts = sorted(output.glob("attempts/*"))
    assert run_staged(manifest, item, output, scratch) == record
    assert sorted(output.glob("attempts/*")) == attempts


def test_input_copy_checks_content(tmp_path):
    source = tmp_path / "source"
    source.write_bytes(b"changed")
    with pytest.raises(ValueError, match="checksum"):
        stage_input(source, tmp_path / "staged", "0" * 64)


def test_retry_requires_no_active_jobs_and_complete_accounting(monkeypatch):
    profile = SimpleNamespace(user="test")

    def replies(*values):
        pending = iter(values)
        monkeypatch.setattr("infra.recovery.remote", lambda *args: next(pending))

    replies("123")
    with pytest.raises(ValueError, match="still queued"):
        require_terminal(profile, ["123"])
    replies("", "123|COMPLETED|\n")
    with pytest.raises(ValueError, match="every previous job"):
        require_terminal(profile, ["123", "124"])
    replies("", "123|COMPLETED|\n124|FAILED|\n")
    require_terminal(profile, ["123", "124"])

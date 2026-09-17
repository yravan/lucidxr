"""Manifest identity and code snapshot contracts without contacting a scheduler."""

import subprocess
from pathlib import Path

import pytest

from infra.snapshot import code_tree
from lucidxr.rendering.jobs import collect, plan
from lucidxr.rendering.spec import RenderSpec


def test_snapshot_preserves_index_and_includes_working_edits(tmp_path):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(tmp_path), *args])

    git("init", "-q")
    git("config", "user.name", "Test")
    git("config", "user.email", "test@example.invalid")
    file = tmp_path / "model.py"
    file.write_text("original")
    git("add", ".")
    git("commit", "-qm", "initial")
    original_index = (tmp_path / ".git/index").read_bytes()
    file.write_text("working change")
    (tmp_path / "untracked.secret").write_text("not included")
    tree = code_tree(tmp_path)
    assert git("show", f"{tree}:model.py") == b"working change"
    assert b"untracked.secret" not in git("ls-tree", "--name-only", tree)
    assert (tmp_path / ".git/index").read_bytes() == original_index
    assert tree == code_tree(tmp_path)


def test_plan_deduplicates_by_content_and_rejects_incomplete_collection(tmp_path):
    first, second = tmp_path / "one.npz", tmp_path / "renamed.npz"
    first.write_bytes(b"same content")
    second.write_bytes(first.read_bytes())
    value, inputs = plan([first, second], RenderSpec(("wrist",), 32, 24))
    assert len(value["items"]) == len(inputs) == 1
    import json

    manifest = tmp_path / "plan.json"
    manifest.write_text(json.dumps(value))
    with pytest.raises(FileNotFoundError):
        collect(manifest, tmp_path / "output")
    assert not list(Path(tmp_path).rglob("collection-*.json"))


def test_jaynes_batch_propagates_worker_failure():
    from infra.jaynes import BatchSlurm

    runner = BatchSlurm(work_dir="/tmp", entry_script="exit 7", n_cpu=1)
    runner.build(lambda: None)
    script = runner.run_script.split("<<<'", 1)[1][:-1]
    result = subprocess.run(["bash", "-c", script], capture_output=True)
    assert result.returncode == 7

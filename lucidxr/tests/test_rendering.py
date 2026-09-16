"""Small real-render checks for identity, pairing and failure publication."""

import json
import shutil

import h5py
import numpy as np
import pytest

from lucidxr.rendering.output import read_result
from lucidxr.rendering.replay import render_demo
from lucidxr.rendering.spec import RenderSpec, digest, request
from lucidxr.sim.demos import Demo, DemoRecorder
from lucidxr.sim.mujoco_env import MujocoEnv
from lucidxr.sim.scenes import make_scene


def recording(tmp_path):
    with MujocoEnv(make_scene("pick_block")) as env:
        env.reset()
        recorder = DemoRecorder(env, "pick_block", source="test")
        for elapsed in (1.0, 1.02, 1.055):
            recorder.append(env.frame(), elapsed)
            env.step(env.current_action())
        return recorder.save(tmp_path / "source")


def test_render_pairing_relocation_and_corruption(tmp_path):
    source = recording(tmp_path)
    spec = RenderSpec(("wrist",), 32, 24, 50, ("rgb", "depth", "segmentation"))
    record = render_demo(source, tmp_path / "output", spec)
    result = read_result(record)
    assert result["work_id"] == digest(request(source, spec))
    assert render_demo(source, tmp_path / "output", spec) == record
    assert len(list((tmp_path / "output" / "attempts").iterdir())) == 1
    artifact = next(x for x in result["artifacts"] if x["path"].endswith(".h5"))
    with h5py.File(record.parent / artifact["path"]) as h5:
        demo = Demo(source)
        np.testing.assert_array_equal(h5["elapsed"], demo.elapsed)
        np.testing.assert_array_equal(h5["frames/qpos"], demo.frames["qpos"])
        np.testing.assert_array_equal(h5["camera_0/video_frame"], [0, 1, 2])
        assert h5["camera_0/depth"].dtype == np.float32
        assert h5["camera_0/segmentation"].dtype == np.int32
        assert h5["camera_0/C2W"].shape == (3, 4, 4)
    shutil.move(tmp_path / "output", tmp_path / "unrelated-name")
    relocated = tmp_path / "unrelated-name" / "results" / record.name
    assert read_result(relocated)["work_id"] == result["work_id"]
    (relocated.parent / result["artifacts"][0]["path"]).write_bytes(b"broken")
    with pytest.raises(ValueError, match="corrupt"):
        read_result(relocated)


def test_failed_video_is_not_published_and_can_retry(tmp_path, monkeypatch):
    source = recording(tmp_path)
    spec = RenderSpec(("wrist",), 32, 24)
    with monkeypatch.context() as patch:

        def fail(*args):
            raise OSError("injected video write failure")

        patch.setattr("lucidxr.rendering.replay.OutputWriter.append", fail)
        with pytest.raises(OSError, match="injected"):
            render_demo(source, tmp_path / "output", spec)
    assert not list((tmp_path / "output").glob("results/*.json"))
    (failure,) = (tmp_path / "output").glob("attempts/*/failure.json")
    assert json.loads(failure.read_text())["error_type"] == "OSError"
    read_result(render_demo(source, tmp_path / "output", spec))
    with pytest.raises(ValueError, match="changed"):
        render_demo(source, tmp_path / "output", spec, expected_request={})

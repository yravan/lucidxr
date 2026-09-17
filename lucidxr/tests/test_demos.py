"""Small recording/storage contracts, independent of Vuer and infrastructure hosts."""

import numpy as np
import pytest

from infra import location
from lucidxr.scripts.playback_demo import playback
from lucidxr.sim.demos import Demo, DemoRecorder
from lucidxr.sim.mujoco_env import MujocoEnv
from lucidxr.sim.scenes import make_scene
from lucidxr.sim.teleop.bundle import export_bundle


def test_recording_roundtrip_and_failed_save_retains_frames(tmp_path, monkeypatch):
    env = MujocoEnv(make_scene("pick_block"))
    try:
        env.reset()
        recorder = DemoRecorder(env, "pick_block", source="test")
        first = env.frame()
        recorder.append(first, 1)
        env.step(env.current_action())
        recorder.append(env.frame(), 1.02)
        last = env.frame()
        with monkeypatch.context() as patch:
            patch.setattr("os.link", lambda *args: (_ for _ in ()).throw(OSError("test disk error")))
            with pytest.raises(OSError, match="disk error"):
                recorder.save(tmp_path)
        assert len(recorder.frames) == 2
        assert not list(tmp_path.iterdir())
        path = recorder.save(tmp_path)
        assert not recorder.frames
        demo = Demo(path)
        assert demo.scene().to_xml() == env.scene.to_xml()
        playback(env, demo, headless=True)
        for name, value in last.items():
            assert np.allclose(getattr(env.data, name), value)
        recorder.append(first, 2)
        second = recorder.save(tmp_path)
        assert second != path and path.exists()
        demo.metadata["scene_seed"] = 54
        demo.metadata["scene_fingerprint"] = "bad"
        with pytest.raises(ValueError, match="differ"):
            demo.scene()
    finally:
        env.close()


def test_storage_location_and_portable_browser_bundle(tmp_path):
    config = tmp_path / "infra.toml"
    config.write_text('[locations]\ndemos = "~/some-demo-folder"\n')
    assert location("demos", config=config).is_absolute()
    with pytest.raises(ValueError, match="Unknown location"):
        location("unused", config=config)
    config.write_text('[locations]\ndemos = "relative"\n')
    with pytest.raises(ValueError, match="absolute"):
        location("demos", config=config)
    scene = make_scene("pick_block")
    files = export_bundle(scene, tmp_path / "bundle")
    import mujoco

    model = mujoco.MjModel.from_xml_path(str(tmp_path / "bundle" / "scene.xml"))
    assert model.nq > 0
    assert len(files) == len(list((tmp_path / "bundle").iterdir()))
    xml = (tmp_path / "bundle" / "scene.xml").read_text()
    assert str(scene.assets) not in xml

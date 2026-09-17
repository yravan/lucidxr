"""Exercise clock capture, physics replay, scene transfer and rendered state pairing."""

import h5py
import mujoco
import numpy as np
import pytest

from lucidxr.rendering.output import read_result
from lucidxr.rendering.replay import render_demo
from lucidxr.rendering.spec import RenderSpec
from lucidxr.sim.demos import Demo, DemoRecorder
from lucidxr.sim.mujoco_env import MujocoEnv
from lucidxr.sim.playback import ReplaySpec, replay_frames
from lucidxr.sim.scenes import make_scene
from lucidxr.sim.teleop.bundle import CLOCK_SENSOR, export_bundle
from lucidxr.sim.teleop.vuer import frame_time


def command_demo(directory):
    with MujocoEnv(make_scene("pick_block")) as env:
        env.reset()
        recorder = DemoRecorder(env, "pick_block", source="native-test")
        recorder.append(env.frame(), env.data.time)
        for count in (10, 15, 5, 10):
            action = env.current_action()
            action["mocap_pos"][:, 0] += 0.002
            action["ctrl"][:] = 0.3
            env.advance(action, steps=count)
            recorder.append(env.frame(), env.data.time)
        return recorder.save(directory)


def test_browser_bundle_clock_does_not_change_physics(tmp_path):
    scene = make_scene("pick_block")
    original = scene.compile()
    export_bundle(scene, tmp_path, recording=True)
    browser = mujoco.MjModel.from_xml_path(str(tmp_path / "scene.xml"))
    clock = browser.sensor(CLOCK_SENSOR).adr[0]
    assert clock == original.nsensordata
    assert (browser.nq, browser.nv, browser.nu) == (original.nq, original.nv, original.nu)
    a, b = mujoco.MjData(original), mujoco.MjData(browser)
    for _ in range(12):
        mujoco.mj_step(original, a)
        mujoco.mj_step(browser, b)
        # Match the pinned browser loop: emit after mj_step, without mj_forward.
        assert b.sensordata[clock] == pytest.approx(b.time - browser.opt.timestep)
        assert frame_time({"sensordata": b.sensordata}, original) == pytest.approx(b.time)
        np.testing.assert_allclose(a.qpos, b.qpos, atol=1e-12)


def test_commands_reproduce_motion_and_transfer_by_control_names(tmp_path):
    demo = Demo(command_demo(tmp_path))
    with MujocoEnv(demo.scene()) as env:
        env.reset()
        for index in replay_frames(env, demo, ReplaySpec("commands")):
            np.testing.assert_allclose(env.data.qpos, demo.frames["qpos"][index], atol=1e-9)
            assert env.data.time == pytest.approx(demo.times[index])
    target = ReplaySpec("commands", "pick_sphere", seed=9)
    with MujocoEnv(target.make_scene(demo)) as env:
        env.reset()
        initial = env.data.qpos.copy()
        assert initial.shape != demo.frames["qpos"][0].shape
        frames = replay_frames(env, demo, target)
        assert next(frames) == 0
        np.testing.assert_array_equal(env.data.qpos, initial)
        list(frames)
        assert not np.array_equal(env.data.qpos, initial)
        np.testing.assert_array_equal(env.data.ctrl, demo.frames["ctrl"][-1])
        demo.metadata["controls"]["actuators"][0]["name"] = "missing"
        with pytest.raises(ValueError, match="Incompatible actuators"):
            list(replay_frames(env, demo, target))


def test_command_render_stores_target_states_and_rejects_fractional_steps(tmp_path):
    source = command_demo(tmp_path / "source")
    demo = Demo(source)
    playback = ReplaySpec("commands", "pick_sphere", seed=4)
    spec = RenderSpec(("wrist",), 32, 24, replay=playback)
    record = render_demo(source, tmp_path / "output", spec)
    result = read_result(record)
    h5path = next(x for x in result["artifacts"] if x["path"].endswith(".h5"))["path"]
    with h5py.File(record.parent / h5path) as h5, MujocoEnv(playback.make_scene(demo)) as env:
        env.reset()
        for index in replay_frames(env, demo, playback):
            np.testing.assert_allclose(h5["frames/qpos"][index], env.data.qpos, atol=1e-12)
            assert h5["simulation_time"][index] == pytest.approx(env.data.time)
        demo.elapsed[1] += env.model.opt.timestep / 2
        with pytest.raises(ValueError, match="integer multiples"):
            list(replay_frames(env, demo, playback))

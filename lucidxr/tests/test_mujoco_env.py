"""Small runtime checks focused on data/control contracts, not task benchmarks."""

import numpy as np
import pytest
from gymnasium.utils.env_checker import check_env

from lucidxr.sim.mujoco_env import Episode, MocapControl, MujocoEnv
from lucidxr.sim.mujoco_env.wrappers import Camera, CameraWrapper, DomainRandomization, VisualRandomization
from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema import Mjcf, Raw


class MiniScene(Scene):
    def build(self):
        # A fingertip appears BEFORE its wrist and there are no actuators.
        return Mjcf(
            Raw("""
          <body name="finger" mocap="true" pos=".2 0 .3"><geom name="finger" size=".03"/></body>
          <body name="wrist" mocap="true" pos="0 0 .3"><geom name="wrist" size=".03"/></body>
          <body name="ball" pos="0 0 .6"><freejoint/><geom name="ball" size=".04"/></body>
          <camera name="view" pos="0 0 2"/>
          <light name="light" pos="0 0 2"/>
          <geom type="plane" size="2 2 .1"/>
        """)
        )


def test_gym_and_relative_control_roundtrip():
    env = MujocoEnv(MiniScene(), control=MocapControl(relative_to={"finger": "wrist"}))
    try:
        check_env(env, skip_render_check=True)
        env.reset(seed=7)
        action = env.current_action()
        original = env.frame()
        env.step(action)
        assert np.allclose(env.data.mocap_pos, original["mocap_pos"])
        assert np.allclose(env.current_action(), action)
        env.restore_frame({"qvel": np.ones(env.model.nv)})
        assert np.array_equal(env.data.qvel, np.ones(env.model.nv))
        before = env.frame()
        with pytest.raises(ValueError):
            env.restore_frame({"qvel": np.zeros(env.model.nv), "ctrl": np.ones(1)})
        assert np.array_equal(env.data.qvel, before["qvel"])
        state = env.snapshot()
        env.step(env.current_action())
        expected = env.snapshot()
        env.restore_snapshot(state)
        env.step(env.current_action())
        assert np.array_equal(env.snapshot(), expected)
    finally:
        env.close()


def test_episode_reads_do_not_advance_bookkeeping():
    class Counter(Episode):
        def reset(self, env):
            self.steps = 0

        def after_step(self, env):
            self.steps += 1

        def evaluate(self, env):
            return float(self.steps), self.steps >= 2, {"success": self.steps >= 2}

    env = MujocoEnv(MiniScene(), episode=Counter())
    try:
        env.reset()
        assert env.step(np.empty(0))[1:4] == (1.0, False, False)
        env.restore_frame(env.frame())
        env.observe()
        assert env.episode.evaluate(env)[0] == 1
        assert env.step(np.empty(0))[1:4] == (2.0, True, False)
        env.reset()
        assert env.episode.steps == 0
    finally:
        env.close()


def test_camera_products_and_seeded_randomization():
    base = MujocoEnv(MiniScene())
    randomizer = DomainRandomization(base, VisualRandomization(camera_position=0.02))
    env = CameraWrapper(
        randomizer,
        [
            Camera(
                "view",
                width=64,
                height=48,
                products=(
                    "rgb",
                    "depth",
                    "rgbd",
                    "segmentation",
                    "semantic",
                    "overlay",
                    "inverse_depth",
                    "masked_inverse_depth",
                ),
                masks={"ball": ("ball",)},
                semantic={"ball": 300},
            )
        ],
    )
    try:
        original = base.model.cam_pos.copy()
        obs, _ = env.reset(seed=21)
        sampled = base.model.cam_pos.copy()
        assert env.observation_space.contains(obs)
        assert np.any(obs["view/semantic"] == 300)
        assert np.any(obs["view/mask/ball"])
        assert np.allclose(env.observe()["view/rgb"], obs["view/rgb"], atol=1)
        # macOS OpenGL can differ by one intensity unit after a render-mode switch.
        assert np.array_equal(base.model.cam_pos, sampled)
        again, _ = env.reset(seed=21)
        assert np.array_equal(sampled, base.model.cam_pos)
        assert np.allclose(obs["view/rgb"], again["view/rgb"], atol=1)
        hidden = base.rendering.image("view", 64, 48, mode="segmentation", hide=[base.model.geom("ball").id])
        assert not np.any(hidden == base.model.geom("ball").id)
        randomizer.restore()
        assert np.array_equal(original, base.model.cam_pos)
    finally:
        env.close()

"""Conditioning/compositing contracts, without a GPU or external checkpoints."""

import numpy as np
import pytest

from lucidxr.sim.mujoco_env import MujocoEnv
from lucidxr.sim.mujoco_env.splat import SplatAlignment
from lucidxr.sim.mujoco_env.wrappers import Camera, GsplatParams, GsplatWrapper, LucidParams, LucidWrapper
from lucidxr.sim.mujoco_env.wrappers.lucid import midas_depth
from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema import Mjcf, Raw


class ConditioningScene(Scene):
    def build(self):
        return Mjcf(
            Raw("""
          <camera name="view" pos="0 0 3"/>
          <light pos="0 0 4"/>
          <geom name="floor" type="plane" size="2 2 .1"/>
          <body name="robot" pos="0 0 .4"><geom name="hand" type="box" size=".3 .3 .3" rgba="1 0 0 1"/></body>
        """)
        )


class RecordingRenderer:
    calls = 0

    def render(self, K, C2W, width, height):
        self.calls += 1
        self.K, self.pose = K.copy(), C2W.copy()
        self.rgb = np.full((height, width, 3), 42, np.uint8)
        return dict(
            rgb=self.rgb,
            depth=np.ones((height, width), np.float32),
            alpha=np.ones((height, width), np.float32),
        )


def test_lucid_and_splat_composition_and_live_calibration():
    base = MujocoEnv(ConditioningScene())
    lucid = LucidWrapper(
        base,
        LucidParams(
            Camera("view", width=64, height=48, semantic={"floor": 4}, masks={"robot": ("robot",)}),
            preserve_bodies=("robot",),
        ),
    )
    renderer = RecordingRenderer()
    env = GsplatWrapper(
        lucid,
        renderer,
        GsplatParams(
            "view",
            width=64,
            height=48,
            alignment=SplatAlignment(scale=2),
            foreground_rgb="view/lucid/rgb",
            preserve_mask="view/lucid/preserve_mask",
        ),
    )
    try:
        obs, _ = env.reset(seed=4)
        assert env.observation_space.contains(obs)
        mask = obs["view/lucid/preserve_mask"]
        assert mask.any() and not mask.all()
        assert not obs["view/lucid/mask/robot"].any()  # robot absent from conditioning
        assert np.array_equal(obs["splat/rgb"][mask], obs["view/lucid/rgb"][mask])
        assert np.all(obs["splat/rgb"][~mask] == 42)
        assert np.all(renderer.rgb == 42)  # no mutation of renderer storage
        assert np.all(obs["splat/depth"] == 2)
        assert np.allclose(renderer.pose[:3, :3].T @ renderer.pose[:3, :3], np.eye(3))
        assert np.allclose(renderer.pose[:3, 3], (0, 0, 1.5))
        focal = renderer.K[0, 0]
        base.model.cam_fovy[0] = 70
        base.refresh_model()
        again = env.observe()
        assert renderer.K[0, 0] != focal
        assert env.observation_space.contains(again)
        assert env.observation_space.contains(env.step(base.current_action())[0])
        assert np.all(obs["view/lucid/masked_midas_depth"] == 0)
        semantic = obs["view/lucid/semantic_rgb"]
        assert np.any(np.all(semantic == (80, 50, 50), axis=-1))  # ADE floor
    finally:
        env.close()


def test_alignment_and_depth_edge_cases(tmp_path):
    path = tmp_path / "collision_tf.json"
    path.write_text('{"mesh_scale":2,"mesh_pos":[1,2,3],"mesh_euler":[0,0,0]}')
    alignment = SplatAlignment.from_json(path)
    rotation, origin = alignment.camera_transform()
    assert np.array_equal(rotation, np.eye(3))
    assert np.array_equal(origin, [1, 2, 3])
    for depth in (np.zeros((2, 2), np.float32), np.full((2, 2), np.inf, np.float32)):
        assert np.all(midas_depth(depth, 2) == 0)
    with pytest.raises(ValueError):
        SplatAlignment(scale=0)


def test_splat_shared_renderer_one_call_per_observation():
    base = MujocoEnv(ConditioningScene())
    renderer = RecordingRenderer()
    env = base
    for i in range(100):
        env = GsplatWrapper(env, renderer, GsplatParams("view", width=8, height=8, key=f"splat{i}"))
    try:
        obs, _ = env.reset()
        assert renderer.calls == 1
        obs["splat0/rgb"][...] = 0
        assert np.all(obs["splat99/rgb"] == 42)
        env.step(base.current_action())
        assert renderer.calls == 2
    finally:
        env.close()

"""Focused contracts for parameter-driven randomization and texture roles."""

import struct
import zlib

import numpy as np
import pytest

from lucidxr.sim.mujoco_env import MujocoEnv
from lucidxr.sim.mujoco_env.wrappers import (
    CameraRandomization,
    CameraRandomizationParams,
    LightingRandomization,
    LightingRandomizationParams,
    MaterialRandomization,
    MaterialRandomizationParams,
    PositionRandomization,
    RotationRandomization,
    TextureRandomization,
    TextureRandomizationParams,
    Uniform,
)
from lucidxr.sim.scenes.base import Scene
from lucidxr.sim.xml_schema import Mjcf, Raw


class AppearanceScene(Scene):
    def build(self):
        textures = [
            ("rgb", "2d", 3),
            ("rgba", "2d", 4),
            ("cube", "cube", 3),
            ("sky", "skybox", 3),
            ("normal", "2d", 3),
            ("roughness", "2d", 1),
            ("opacity", "2d", 1),
            ("orm", "2d", 3),
            ("emissive", "2d", 4),
            ("shared", "2d", 3),
        ]
        assets = "<asset>"
        for name, kind, channels in textures:
            if channels == 3:
                assets += (
                    f'<texture name="{name}" type="{kind}" builtin="checker" width="8" height="8" '
                    f'nchannel="3" rgb1=".3 .4 .5" rgb2=".6 .5 .4"/>'
                )
            else:
                assets += f'<texture name="{name}" type="{kind}" file="{self.assets}/{channels}.png" nchannel="{channels}"/>'
        assets += '<material name="mat" texture="rgb"/>'
        for name, _, _ in textures:
            if name in {"rgb", "sky"}:
                continue
            role = "rgb" if name in {"cube", "shared"} else name
            assets += f'<material name="mat_{name}"><layer role="{role}" texture="{name}"/></material>'
        assets += '<material name="conflict"><layer role="normal" texture="shared"/></material></asset>'
        world = '<geom type="plane" size="2 2 .1" material="mat"/>'
        world += '<camera name="view" pos="0 0 2"/>'
        world += '<camera name="calibrated" pos="0 0 2" sensorsize=".036 .024" focal=".025 .025" resolution="64 48"/>'
        world += "".join(f'<light name="l{i}" pos="{i} 0 2"/>' for i in range(3))
        return Mjcf(Raw(world), preamble=assets)


def appearance_scene(path):
    # Tiny file-backed scalar/RGBA maps with known fourth channels.
    for channels, png_type in ((1, 0), (4, 6)):
        data = bytes([90] * (8 * channels))
        raw = b"".join(b"\x00" + data for _ in range(8))

        def chunk(kind, payload):
            return (
                struct.pack(">I", len(payload))
                + kind
                + payload
                + struct.pack(">I", zlib.crc32(kind + payload))
            )

        content = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 8, 8, 8, png_type, 0, 0, 0))
        content += chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")
        (path / f"{channels}.png").write_bytes(content)
    return AppearanceScene(assets=path)


def pixels(model, name):
    index = model.texture(name).id
    start = model.tex_adr[index]
    shape = (model.tex_height[index], model.tex_width[index], model.tex_nchannel[index])
    return model.tex_data[start : start + np.prod(shape)].reshape(shape)


@pytest.mark.parametrize("mode", ("tint", "flat", "checker", "gradient", "noise"))
def test_texture_types_roles_channels_and_reproducibility(mode, tmp_path):
    base = MujocoEnv(appearance_scene(tmp_path))
    original = base.model.tex_data.copy()
    env = TextureRandomization(base, TextureRandomizationParams(modes=(mode,)))
    try:
        assert {base.model.texture(i).name for i in env.texture_ids} == {"rgb", "rgba", "cube", "emissive"}
        env.reset(seed=8)
        first = base.model.tex_data.copy()
        assert not np.array_equal(first, original)
        # Non-color roles, conflicting shared roles, and opt-in skybox remain unchanged.
        for name in ("normal", "roughness", "opacity", "orm", "shared", "sky"):
            index = base.model.texture(name).id
            start, size = base.model.tex_adr[index], pixels(base.model, name).size
            assert np.array_equal(pixels(base.model, name).ravel(), original[start : start + size])
        for name in ("rgba", "emissive"):
            index = base.model.texture(name).id
            start, size = base.model.tex_adr[index], pixels(base.model, name).size
            assert np.array_equal(
                pixels(base.model, name)[..., 3].ravel(), original[start : start + size].reshape(-1, 4)[:, 3]
            )
        env.reset(seed=8)
        assert np.array_equal(base.model.tex_data, first)
        env.restore()
        assert np.array_equal(base.model.tex_data, original)
        with pytest.raises(ValueError, match="supported color"):
            TextureRandomization(base, TextureRandomizationParams(names=("normal",)))
        sky = TextureRandomization(
            base, TextureRandomizationParams(names=("sky",), kinds=("skybox",), modes=(mode,))
        )
        sky.randomize()
        assert not np.array_equal(base.model.tex_data, original)
        sky.restore()
    finally:
        env.close()


def test_light_pose_count_and_periodic_sampling(tmp_path):
    base = MujocoEnv(appearance_scene(tmp_path))
    params = LightingRandomizationParams(
        names=("l0", "l1"),
        active_count=(1, 1),
        shadow_probability=0.0,
        position=PositionRandomization(bounds=((-1.0, -1.0, 1.0), (1.0, 1.0, 3.0))),
        rotation=RotationRandomization(0.5),
        cutoff=Uniform(20, 40),
        every_n_steps=2,
    )
    env = LightingRandomization(base, params)
    original = base.model.light_pos.copy()
    try:
        env.reset(seed=4)
        assert base.model.light_active[:2].sum() == 1
        assert not base.model.light_castshadow[:2].any()
        assert np.allclose(np.linalg.norm(base.model.light_dir[:2], axis=1), 1)
        assert np.array_equal(base.model.light_pos[2], original[2])
        initial = base.model.light_pos.copy()
        env.observe()
        assert np.array_equal(base.model.light_pos, initial)
        env.step(base.current_action())
        first = base.model.light_pos.copy()
        assert not np.array_equal(first, initial)
        env.step(base.current_action())
        assert np.array_equal(base.model.light_pos, first)
        env.step(base.current_action())
        assert not np.array_equal(base.model.light_pos, first)
        env.restore()
        assert np.array_equal(base.model.light_pos, original)
        with pytest.raises(ValueError, match="pool"):
            LightingRandomization(base, LightingRandomizationParams(active_count=(4, 4)))
    finally:
        env.close()


def test_intrinsic_camera_material_and_live_texture_upload(tmp_path):
    base = MujocoEnv(appearance_scene(tmp_path))
    camera = CameraRandomization(
        base,
        CameraRandomizationParams(
            names=("calibrated",),
            focal_scale=Uniform(1.1, 1.1),
            principal_offset=0.02,
            rotation=RotationRandomization(0),
        ),
    )
    original = base.model.cam_intrinsic.copy()
    camera.reset(seed=4)
    assert np.allclose(base.model.cam_intrinsic[1, :2], original[1, :2] * 1.1)
    camera.restore()
    material = MaterialRandomization(
        base,
        MaterialRandomizationParams(
            names=("mat",), roughness=Uniform(0.2, 0.2), specular=Uniform(0.8, 0.8), texrepeat=Uniform(2, 2)
        ),
    )
    material.randomize()
    assert np.allclose(base.model.mat_roughness[0], 0.2)
    material.restore()
    texture = TextureRandomization(base, TextureRandomizationParams(names=("rgb",), modes=("flat",)))
    try:
        before = base.rendering.image("view", 64, 48)
        small_before = base.rendering.image("view", 32, 24)
        renderer = base.rendering._renderers[(64, 48)]
        texture.randomize()
        after = base.rendering.image("view", 64, 48)
        assert base.rendering._renderers[(64, 48)] is renderer
        assert not np.array_equal(before, after)
        assert not np.array_equal(small_before, base.rendering.image("view", 32, 24))
        texture.restore()
        assert np.allclose(base.rendering.image("view", 64, 48), before, atol=1)
    finally:
        texture.close()

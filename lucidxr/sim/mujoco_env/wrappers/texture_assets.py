"""Select compiled color assets without touching PBR maps or shared data twice."""

from dataclasses import dataclass

import mujoco
import numpy as np

KINDS = {
    "2d": mujoco.mjtTexture.mjTEXTURE_2D,
    "cube": mujoco.mjtTexture.mjTEXTURE_CUBE,
    "skybox": mujoco.mjtTexture.mjTEXTURE_SKYBOX,
}
COLOR_ROLES = {
    int(mujoco.mjtTextureRole.mjTEXROLE_RGB),
    int(mujoco.mjtTextureRole.mjTEXROLE_RGBA),
    int(mujoco.mjtTextureRole.mjTEXROLE_EMISSIVE),
}


@dataclass
class TextureAsset:
    id: int
    pixels: np.ndarray
    baseline: np.ndarray
    face_height: int

    def restore(self):
        self.pixels[..., :3] = self.baseline


def select_textures(model, names, kinds):
    ids = range(model.ntex) if names is None else sorted({model.texture(name).id for name in names})
    allowed = {int(KINDS[kind]) for kind in kinds}
    assets = []
    for index in ids:
        kind, channels = int(model.tex_type[index]), int(model.tex_nchannel[index])
        roles = set(np.nonzero(model.mat_texid == index)[1].tolist())
        is_color = bool(roles) and roles <= COLOR_ROLES
        is_background = not roles and (
            kind == mujoco.mjtTexture.mjTEXTURE_SKYBOX or np.any(model.light_texid == index)
        )
        if kind not in allowed or channels not in (3, 4) or not (is_color or is_background):
            if names is not None:
                raise ValueError(
                    f"Texture {model.texture(index).name!r} is excluded by kind or "
                    "is not exclusively a supported color texture"
                )
            continue
        start = int(model.tex_adr[index])
        height, width = int(model.tex_height[index]), int(model.tex_width[index])
        pixels = model.tex_data[start : start + height * width * channels].reshape(height, width, channels)
        face_height = height if kind == mujoco.mjtTexture.mjTEXTURE_2D else width
        assets.append(TextureAsset(index, pixels, pixels[..., :3].copy(), face_height))
    return tuple(assets)

"""Multi-view image products with declared observation spaces."""

from dataclasses import dataclass, field
from typing import Mapping

import numpy as np
from gymnasium import spaces

from .observations import ObservationWrapper


@dataclass(frozen=True)
class Camera:
    """One named camera's requested products. Depth is metric float32.

    hide_bodies removes complete body subtrees from images. masks maps output
    names to body names; overlay keeps the union of these masks over white.
    semantic maps exact geom names to nonnegative class IDs; unmatched pixels -1.
    """

    name: str
    width: int = 640
    height: int = 360
    products: tuple[str, ...] = ("rgb",)
    calibration: bool = True
    key: str | None = None
    hide_bodies: tuple[str, ...] = ()
    masks: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    semantic: Mapping[str, int] = field(default_factory=dict)
    near: float = 0.1
    far: float = 5.0


def body_geoms(model, names):
    """Resolve exact body names and all descendants; fail on misspelled names."""
    roots = {model.body(name).id for name in names}
    selected = set(roots)
    for body in range(1, model.nbody):
        if int(model.body_parentid[body]) in selected:
            selected.add(body)
    return np.flatnonzero(np.isin(model.geom_bodyid, list(selected)))


def depth_image(depth, near, far, *, inverse=False):
    """Normalize into [0,1], invalid/background depth zero in inverse mode."""
    if not 0 < near < far:
        raise ValueError("Require 0 < near < far")
    clipped = np.clip(depth, near, far)
    if inverse:
        result = (1 / clipped - 1 / far) / (1 / near - 1 / far)
    else:
        result = (clipped - near) / (far - near)
    return np.nan_to_num(result).astype(np.float32)


class CameraWrapper(ObservationWrapper):
    """Combine RGB/depth/segmentation/masks without nested per-product wrappers.

    Products: rgb, depth, rgbd, segmentation, semantic, overlay, inverse_depth,
    masked_inverse_depth. Masks and calibration are added when configured.
    """

    def __init__(self, env, cameras):
        super().__init__(env)
        if not isinstance(env.observation_space, spaces.Dict):
            raise TypeError("CameraWrapper requires a Dict observation space")
        self.cameras = tuple(cameras)
        entries = dict(env.observation_space.spaces)
        self._resolved = {}
        supported = {
            "rgb",
            "depth",
            "rgbd",
            "segmentation",
            "semantic",
            "overlay",
            "inverse_depth",
            "masked_inverse_depth",
        }
        for camera in self.cameras:
            key = camera.key or camera.name
            if key in self._resolved:
                raise ValueError(f"Duplicate camera output key {key}")
            self.unwrapped.model.camera(camera.name)
            if min(camera.width, camera.height) <= 0 or not 0 < camera.near < camera.far:
                raise ValueError("Invalid camera dimensions or depth bounds")
            if set(camera.products) - supported:
                raise ValueError(f"Unknown camera products: {set(camera.products) - supported}")
            if {"overlay", "masked_inverse_depth"} & set(camera.products) and not camera.masks:
                raise ValueError("overlay and masked_inverse_depth require masks")
            model = self.unwrapped.model
            masks = {name: body_geoms(model, bodies) for name, bodies in camera.masks.items()}
            semantics = {model.geom(name).id: label for name, label in camera.semantic.items()}
            if any(not isinstance(x, int) or not 0 <= x < np.iinfo(np.int32).max for x in semantics.values()):
                raise ValueError("Semantic class IDs must be nonnegative int32 integers")
            self._resolved[camera.key or camera.name] = (
                body_geoms(model, camera.hide_bodies),
                masks,
                semantics,
            )
            h, w = camera.height, camera.width
            definitions = {
                "rgb": spaces.Box(0, 255, (h, w, 3), dtype=np.uint8),
                "overlay": spaces.Box(0, 255, (h, w, 3), dtype=np.uint8),
                "depth": spaces.Box(0, np.inf, (h, w), dtype=np.float32),
                "rgbd": spaces.Box(0, np.inf, (h, w, 4), dtype=np.float32),
                "segmentation": spaces.Box(-1, max(model.ngeom - 1, 0), (h, w), dtype=np.int32),
                "semantic": spaces.Box(-1, max(semantics.values(), default=0), (h, w), dtype=np.int32),
                "inverse_depth": spaces.Box(0, 1, (h, w), dtype=np.float32),
                "masked_inverse_depth": spaces.Box(0, 1, (h, w), dtype=np.float32),
            }
            products = {key: definitions[key] for key in camera.products}
            products.update({f"mask/{name}": spaces.Box(0, 1, (h, w), dtype=np.bool_) for name in masks})
            if camera.calibration:
                products.update(
                    {
                        "K": spaces.Box(-np.inf, np.inf, (3, 3), dtype=np.float64),
                        "C2W": spaces.Box(-np.inf, np.inf, (4, 4), dtype=np.float64),
                    }
                )
            for name, spec in products.items():
                key = f"{camera.key or camera.name}/{name}"
                if key in entries:
                    raise ValueError(f"Duplicate observation key: {key}")
                entries[key] = spec
        self.observation_space = spaces.Dict(entries)

    def observation(self, observation):
        output = dict(observation)
        rendering = self.unwrapped.rendering
        for camera in self.cameras:
            hide, masks, semantics = self._resolved[camera.key or camera.name]
            products = set(camera.products)
            cache = {}

            def image(mode):
                if mode not in cache:
                    cache[mode] = rendering.image(
                        camera.name, camera.width, camera.height, mode=mode, hide=hide
                    )
                return cache[mode]

            values = {}
            if products & {"rgb", "rgbd", "overlay"}:
                rgb = image("rgb")
                if "rgb" in products:
                    values["rgb"] = rgb
            if products & {"depth", "rgbd", "inverse_depth", "masked_inverse_depth"}:
                depth = image("depth")
                if "depth" in products:
                    values["depth"] = depth
                if "rgbd" in products:
                    values["rgbd"] = np.concatenate((rgb.astype(np.float32), depth[..., None]), axis=-1)
            if products & {"segmentation", "semantic"} or masks:
                segmentation = image("segmentation")
                if "segmentation" in products:
                    values["segmentation"] = segmentation
                if "semantic" in products:
                    labels = np.full(segmentation.shape, -1, dtype=np.int32)
                    for geom, label in semantics.items():
                        labels[segmentation == geom] = label
                    values["semantic"] = labels
            for name, geoms in masks.items():
                values[f"mask/{name}"] = np.isin(segmentation, geoms)
            if products & {"overlay", "masked_inverse_depth"}:
                mask = np.logical_or.reduce([values[f"mask/{name}"] for name in masks])
                if "overlay" in products:
                    values["overlay"] = np.where(mask[..., None], rgb, np.uint8(255))
            if products & {"inverse_depth", "masked_inverse_depth"}:
                inverse = depth_image(depth, camera.near, camera.far, inverse=True)
                if "inverse_depth" in products:
                    values["inverse_depth"] = inverse
                if "masked_inverse_depth" in products:
                    values["masked_inverse_depth"] = np.where(mask, inverse, np.float32(0))
            if camera.calibration:
                values["K"], values["C2W"] = rendering.calibration(camera.name, camera.width, camera.height)
            output.update({f"{camera.key or camera.name}/{name}": value for name, value in values.items()})
        return output

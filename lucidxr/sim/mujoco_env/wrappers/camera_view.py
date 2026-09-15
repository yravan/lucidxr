"""Multi-view image products with declared observation spaces."""

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Mapping

import numpy as np
from gymnasium import spaces


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


class CameraView:
    """Bind a camera configuration to model IDs and declare/capture its products."""

    PRODUCTS = frozenset(
        {
            "rgb",
            "depth",
            "rgbd",
            "segmentation",
            "semantic",
            "overlay",
            "inverse_depth",
            "masked_inverse_depth",
        }
    )

    def __init__(self, model, camera):
        self.camera = camera = deepcopy(camera)
        self.key = camera.key or camera.name
        self.camera_id = model.camera(camera.name).id
        self.products = frozenset(camera.products)
        if min(camera.width, camera.height) <= 0 or not 0 < camera.near < camera.far:
            raise ValueError("Invalid camera dimensions or depth bounds")
        if set(camera.products) - self.PRODUCTS:
            raise ValueError(f"Unknown camera products: {set(camera.products) - self.PRODUCTS}")
        if {"overlay", "masked_inverse_depth"} & set(camera.products) and not camera.masks:
            raise ValueError("overlay and masked_inverse_depth require masks")
        masks = {name: body_geoms(model, bodies) for name, bodies in camera.masks.items()}
        semantics = {model.geom(name).id: label for name, label in camera.semantic.items()}
        if any(not isinstance(x, int) or not 0 <= x < np.iinfo(np.int32).max for x in semantics.values()):
            raise ValueError("Semantic class IDs must be nonnegative int32 integers")
        self.hidden = body_geoms(model, camera.hide_bodies)
        self.masks = {}
        for name, ids in masks.items():
            lookup = np.zeros(model.ngeom + 1, dtype=np.bool_)
            lookup[ids + 1] = True
            self.masks[name] = lookup
        self.labels = np.full(model.ngeom + 1, -1, dtype=np.int32)
        for geom, label in semantics.items():
            self.labels[geom + 1] = label
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
        self.spaces = {f"{self.key}/{name}": space for name, space in products.items()}

    def capture(self, rendering):
        camera = self.camera
        products = self.products

        def image(mode):
            return rendering.image(self.camera_id, camera.width, camera.height, mode=mode, hide=self.hidden)

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
        if products & {"segmentation", "semantic"} or self.masks:
            segmentation = image("segmentation")
            indices = segmentation + 1
            if "segmentation" in products:
                values["segmentation"] = segmentation
            if "semantic" in products:
                values["semantic"] = self.labels[indices]
        for name, lookup in self.masks.items():
            values[f"mask/{name}"] = lookup[indices]
        if products & {"overlay", "masked_inverse_depth"}:
            mask = np.logical_or.reduce([values[f"mask/{name}"] for name in self.masks])
            if "overlay" in products:
                values["overlay"] = np.where(mask[..., None], rgb, np.uint8(255))
        if products & {"inverse_depth", "masked_inverse_depth"}:
            inverse = depth_image(depth, camera.near, camera.far, inverse=True)
            if "inverse_depth" in products:
                values["inverse_depth"] = inverse
            if "masked_inverse_depth" in products:
                values["masked_inverse_depth"] = np.where(mask, inverse, np.float32(0))
        if camera.calibration:
            values["K"], values["C2W"] = rendering.calibration(self.camera_id, camera.width, camera.height)
        return {f"{self.key}/{name}": value for name, value in values.items()}

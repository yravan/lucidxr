"""Lazy native rendering; visibility changes affect the render scene only."""

from collections import OrderedDict
from contextlib import contextmanager

import mujoco
import numpy as np


class Rendering:
    def __init__(self, model, data):
        self.model, self.data = model, data
        self._renderers = OrderedDict()
        self._viewer = None
        self._batch_cache = None

    @contextmanager
    def batch(self):
        """Reuse identical image requests within one observation, never across steps."""
        if self._batch_cache is not None:
            yield
            return
        self._batch_cache = {}
        try:
            yield
        finally:
            self._batch_cache = None

    def image(self, camera, width, height, *, mode="rgb", hide=(), hide_sites=True):
        key = (camera, width, height, mode, tuple(hide), hide_sites)
        cache = self._batch_cache
        if cache is not None and key in cache:
            return cache[key].copy()
        pixels = self._image(camera, width, height, mode=mode, hide=hide, hide_sites=hide_sites)
        if cache is not None:
            cache[key] = pixels.copy()
        return pixels

    def _image(self, camera, width, height, *, mode="rgb", hide=(), hide_sites=True):
        if mode not in {"rgb", "depth", "segmentation"}:
            raise ValueError(f"Unknown render mode {mode!r}")
        if width <= 0 or height <= 0:
            raise ValueError("Image dimensions must be positive")
        size = (width, height)
        renderer = self._renderers.get(size)
        if renderer is None:
            # Bound GPU memory while retaining common multi-resolution views.
            if len(self._renderers) == 4:
                _, expired = self._renderers.popitem(last=False)
                expired.close()
            self.model.vis.global_.offwidth = max(width, self.model.vis.global_.offwidth)
            self.model.vis.global_.offheight = max(height, self.model.vis.global_.offheight)
            renderer = mujoco.Renderer(
                self.model, height=height, width=width, max_geom=max(10000, self.model.ngeom * 2)
            )
            self._renderers[size] = renderer
        self._renderers.move_to_end(size)
        renderer.disable_depth_rendering()
        renderer.disable_segmentation_rendering()
        if mode == "depth":
            renderer.enable_depth_rendering()
        elif mode == "segmentation":
            renderer.enable_segmentation_rendering()
        option = mujoco.MjvOption()
        if hide_sites:
            option.sitegroup[:] = 0
        renderer.update_scene(self.data, camera=camera, scene_option=option)
        # Compact the visualization scene rather than modifying physical geometry.
        hidden = set(hide)
        if hidden:
            kept = 0
            for index in range(renderer.scene.ngeom):
                geom = renderer.scene.geoms[index]
                if geom.objtype == mujoco.mjtObj.mjOBJ_GEOM and geom.objid in hidden:
                    continue
                if kept != index:
                    target = renderer.scene.geoms[kept]
                    for field in (
                        "camdist",
                        "category",
                        "dataid",
                        "emission",
                        "label",
                        "mat",
                        "matid",
                        "modelrbound",
                        "objid",
                        "objtype",
                        "pos",
                        "reflectance",
                        "rgba",
                        "segid",
                        "shininess",
                        "size",
                        "specular",
                        "texcoord",
                        "texid",
                        "texrepeat",
                        "texuniform",
                        "transparent",
                        "type",
                    ):
                        setattr(target, field, getattr(geom, field))
                renderer.scene.geoms[kept].segid = kept
                kept += 1
            renderer.scene.ngeom = kept
        pixels = renderer.render().copy()
        if mode == "segmentation":
            return np.where(pixels[..., 1] == mujoco.mjtObj.mjOBJ_GEOM, pixels[..., 0], -1).astype(np.int32)
        return pixels

    def calibration(self, camera, width, height):
        key = ("calibration", camera, width, height)
        cache = self._batch_cache
        if cache is not None and key in cache:
            return tuple(value.copy() for value in cache[key])
        result = self._calibration(camera, width, height)
        if cache is not None:
            cache[key] = tuple(value.copy() for value in result)
        return result

    def _calibration(self, camera, width, height):
        """Pinhole K and camera-to-world pose (OpenCV: x right, y down, z forward)."""
        cam = self.model.camera(camera).id
        if self.model.cam_projection[cam] == mujoco.mjtProjection.mjPROJ_ORTHOGRAPHIC:
            raise ValueError("Pinhole calibration is not defined for an orthographic camera")
        sensorsize = self.model.cam_sensorsize[cam]
        if np.all(sensorsize > 0):
            intrinsic = self.model.cam_intrinsic[cam]
            fx, fy = intrinsic[:2] / sensorsize * (width, height)
            # MuJoCo principal point is an offset from the optical center.
            cx, cy = np.array([width / 2, height / 2]) + intrinsic[2:] / sensorsize * (-width, height)
        else:
            fx = fy = 0.5 * height / np.tan(np.deg2rad(self.model.cam_fovy[cam]) / 2)
            cx, cy = width / 2, height / 2
        k = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float64)
        pose = np.eye(4)
        pose[:3, :3] = self.data.cam_xmat[cam].reshape(3, 3) @ np.diag([1.0, -1.0, -1.0])
        pose[:3, 3] = self.data.cam_xpos[cam]
        return k, pose

    def show(self):
        if self._viewer is None:
            import mujoco.viewer

            self._viewer = mujoco.viewer.launch_passive(self.model, self.data)
        if self._viewer.is_running():
            self._viewer.sync()

    def update_textures(self, texture_ids):
        """Upload changed assets once per existing context, without rebuilding renderers.

        MuJoCo 3.13 Renderer doesn't expose its context publicly. This isolated
        bridge uses its current context fields with the documented upload API;
        rebuild lazily if a future Renderer changes those fields.
        """
        if self._batch_cache is not None:
            self._batch_cache.clear()
        for renderer in self._renderers.values():
            context = getattr(renderer, "_mjr_context", None)
            if context is None or not hasattr(renderer, "_gl_context"):
                self.invalidate_images()
                break
            if renderer._gl_context is not None:
                renderer._gl_context.make_current()
            for index in texture_ids:
                mujoco.mjr_uploadTexture(self.model, context, index)
        if self._viewer is not None and self._viewer.is_running():
            for index in texture_ids:
                self._viewer.update_texture(index)

    def invalidate_images(self):
        """Reload GPU resources on the next image without closing the human viewer."""
        for renderer in self._renderers.values():
            renderer.close()
        self._renderers.clear()
        if self._batch_cache is not None:
            self._batch_cache.clear()

    def close(self):
        self.invalidate_images()
        if self._viewer is not None:
            self._viewer.close()
        self._viewer = None

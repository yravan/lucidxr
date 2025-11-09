from pathlib import Path

from vuer_mujoco.wrappers.camera_wrapper import CameraWrapper
import numpy as np
import torch

import transforms3d
from .model.neverwhere_splat_model import Model
from vuer_mujoco.wrappers.utils.tf_utils import get_camera_extrinsic_matrix


class SplatRGBWrapper(CameraWrapper):
    """
    Renders splat RGB image.
    """


    def __init__(self, env, *, gsplat_path, transform_path, image_key, width, height, camera_id, device="cuda", **kwargs):
        super().__init__(env, **kwargs)

        self.width = width
        self.height = height
        self.gsplat_path = gsplat_path
        self.transform_path = transform_path
        self.device = device
        self.image_key = image_key
        self.camera_id = camera_id

        self.fovy = self.unwrapped.env.physics.named.model.cam_fovy[camera_id]
        self.fx = 0.5 * self.height / np.tan(self.fovy * np.pi / 360)
        self.fy = self.fx

        # fixme: get rid of by adding better labeling tool. This is added by the XML creation
        # extra_mesh_translation = self.unwrapped.env.physics.named.data.xpos["eval"]
        extra_mesh_translation = np.zeros(3)

        self.model_tf_inv = self.grab_transform(transform_path, extra_mesh_translation)
        self.model = self.load_model(gsplat_path, device)
        self.splat_name = Path(self.gsplat_path).stem

    def load_model(self, dataset_path, device):
        model = Model(device=device)

        print("Loading model from", dataset_path, "...")
        sd = torch.load(f"{dataset_path}/3dgs/model.pt", map_location=device)
        model.load_ckpt(sd)
        model.eval()

        return model

    def grab_transform(self, dataset_path, extra_mesh_translation):

        # mesh_rot = self.unwrapped.env.physics.named.data.xmat["mesh"].reshape(3, 3)

        with open(f"{dataset_path}/collision_tf.json", "r") as f:
            import json
            data = json.load(f)
            scale = np.array(data["mesh_scale"])
            pos = np.array(data["mesh_pos"])
            euler = np.array(data["mesh_euler"])

            rot_mat = transforms3d.euler.euler2mat(*euler, axes="rxyz")
            scale_mat = np.diag([scale, scale, scale, 1])

            full_tf = np.eye(4)
            full_tf[:3, :3] = rot_mat @ scale_mat[:3, :3]
            full_tf[:3, 3] = pos + extra_mesh_translation

        return np.linalg.inv(full_tf)

    def splat_render(self, cam_info: dict):
        outputs = self.model.get_simple_outputs(**cam_info)

        raw_rgb = outputs["rgb"]
        rgb_np = (raw_rgb.clamp(0, 1) * 255).cpu().numpy()
        rgb_np = (rgb_np).astype(np.uint8)

        return rgb_np

    def _compute_additional_obs(self, obs=None):
        c2w = get_camera_extrinsic_matrix(physics=self.unwrapped.env.physics, camera_name=self.camera_id, axis_correction=False)
        c2w = self.model_tf_inv @ c2w

        cam_info = dict(c2w=c2w,
                        fx=self.fx,
                        fy=self.fy,
                        cx=self.width / 2,
                        cy=self.height / 2,
                        width=self.width,
                        height=self.height)

        render = self.splat_render(cam_info)

        # composite
        overlay = obs.get(f"{self.image_key}/overlay", None)
        overlay_mask = obs.get(f"{self.image_key}/overlay/mask", None)
        if overlay is not None:
            render[~overlay_mask] = overlay[~overlay_mask]

        return {
            f"{self.image_key}-{self.splat_name}": render,
        }

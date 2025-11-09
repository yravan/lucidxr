import random

import torch
from dotvar import auto_load  # noqa
from matplotlib import pyplot as plt
from matplotlib.patches import Ellipse
from ml_logger import logger
import numpy as np
from params_proto import ParamsProto, PrefixProto

from lucidxr.learning.act_config import ACT_Config
from lucidxr.learning.episode_datasets import load_data_combined
from lucidxr.learning.train import TrainArgs
from torch import GradScaler, autocast

from lucidxr.learning.unroll_eval import load_policy, UnrollEval
from sklearn.decomposition import PCA

import zarr.core.sync as zsync

zsync.reset_resources_after_fork()


class Params(PrefixProto, cli_parse=False):
    dataset_prefix: str = "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/pick_place_robot_room/2025/08/07/15.58.28/"


def main(**deps):
    print("[INFO] Updating configs...")
    Params._update(**deps)
    UnrollEval._update(**deps)
    TrainArgs._update(**deps)
    ACT_Config._update(**deps)
    print(deps)

    print("[INFO] Loading policy...")
    policy = load_policy()

    print(f"[INFO] Loading dataset... from {TrainArgs.dataset_host}")
    train_dataloader, val_dataloader = load_data_combined(
        dataset_dirs=[Params.dataset_prefix],
        cache_root=TrainArgs.cache_root,
        batch_size_train=TrainArgs.batch_size_train,
        batch_size_val=TrainArgs.batch_size_val,
        chunk_size=ACT_Config.chunk_size,
        train_ratio=1 - 0.2,
        aug_camera_randomization=False,
        prune_cache=TrainArgs.prune_local_cache,
        lucid_mode=TrainArgs.lucid_mode,
        dataset_host=TrainArgs.dataset_host,
        debug=TrainArgs.debug,
        train_image_keys=None,
        act_image_keys=deps["image_keys"],
        data_fractions=TrainArgs.data_fractions,
        real_robot=TrainArgs.real_robot,
    )

    print("[INFO] Starting saliency map extraction from first 3 batches...")
    policy.train()
    batch_limit = 5

    dataset = val_dataloader.dataset.dataset_collection[0]
    episodes = random.sample(list(range(len(dataset.episode_sizes))), batch_limit)

    all_imgs = []
    all_sals = []
    titles = []

    for i in episodes:
        index = sum(dataset.episode_sizes[:i])  # starting index of the i-th episode
        print(f"\n[INFO] Processing batch {i + 1}/{batch_limit}")
        data = dataset[index  + 100]

        data = {(k.split("/")[0] + "/rgb") if "/" in k else k: v for k, v in data.items()}
        cam_views = {
            view: data[view].to(TrainArgs.device).detach().clone().unsqueeze(0).requires_grad_(True) for view in ACT_Config.image_keys
        }

        obs = data["observation"].to(TrainArgs.device).unsqueeze(0)
        actions = data["actions"].to(TrainArgs.device).unsqueeze(0)
        is_pad = data["is_pad"].to(TrainArgs.device).unsqueeze(0)

        with autocast(device_type="cuda", dtype=torch.bfloat16):
            a_hat, mu, logvar, forward_dict = policy(
                observation=obs,
                actions=actions,
                is_pad=is_pad,
                cam_views=cam_views,
            )

        loss = forward_dict["loss"]
        # loss.backward()
        a_hat[:,:,:].sum().backward()

        for view in ACT_Config.image_keys:
            grad = cam_views[view].grad  # [B, C, H, W]
            saliency = torch.sqrt((grad**2).sum(dim=1))  # [B, H, W]

            img = cam_views[view].detach().cpu()[0]
            img = img.permute(1, 2, 0).numpy()
            img = (img - img.min()) / (img.max() - img.min() + 1e-6)

            cam = saliency.detach().cpu().numpy()[0]
            cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-6)

            all_imgs.append(img)
            all_sals.append(cam)
            titles.append(f"Episode {i + 1}")

    # === Plot everything together ===
    num_eps = len(all_imgs)
    fig, axes = plt.subplots(num_eps, 2, figsize=(6, 3 * num_eps))

    if num_eps == 1:
        axes = np.expand_dims(axes, 0)  # make iterable if only 1 episode

    for i in range(num_eps):
        axes[i, 0].imshow(all_imgs[i], interpolation="none")
        axes[i, 0].set_title(f"{titles[i]} - Input")
        axes[i, 0].axis("off")

        axes[i, 1].imshow(all_sals[i], cmap="hot", interpolation="none")
        axes[i, 1].set_title("Saliency")
        axes[i, 1].axis("off")

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main(
        **{
            "dataset_host": "http://escher.csail.mit.edu:4000",
            # "dataset_prefix": "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/pick_place_robot_room/2025/08/07/15.58.28/",
            "dataset_prefix": "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/pick_place_real/2025/08/07/16.43.17/",
            "load_checkpoint": "/lucidxr/lucidxr/post_corl_2025/yajvan/8-19-25/../8-19-25/pick_place_heaviest_dr/learn/2025/08/19/12-17-12/wrist-frame/chunk-size-10/dec_layers-1/nheads-8/lr_backbone-1e-05/checkpoints/policy_0015000.pt",
            "image_keys": ["right/rgb", "wrist/rgb", "left/rgb"],
            "load_from_cache": True,
            "prune_local_cache": False,
            "load_episodes": False,
        }
    )

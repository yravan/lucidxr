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


class Params(PrefixProto, cli_parse=False):
    dataset_prefix: str = "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2024/10/30/16.08.20/"



def main(**deps):
    Params._update(**deps)
    UnrollEval._update(**deps)
    TrainArgs._update(**deps)
    policy = load_policy()
    train_dataloader, val_dataloader = load_data_combined(
        dataset_dirs=[Params.dataset_prefix],
        cache_root=TrainArgs.cache_root,
        image_keys=ACT_Config.image_keys,
        batch_size_train=TrainArgs.batch_size_train,
        batch_size_val=TrainArgs.batch_size_val,
        chunk_size=ACT_Config.chunk_size,
        train_ratio=1 - 0.2,
        aug_camera_randomization=False,
        prune_cache=TrainArgs.prune_local_cache,
        lucid_mode=TrainArgs.lucid_mode,
        dataset_host=TrainArgs.dataset_host,
        debug=TrainArgs.debug,
    )
    all_mu = []
    episode_ids = []
    all_logvar = []
    for batch_idx, data in enumerate(val_dataloader):
        print(f"Processing batch {batch_idx + 1}/{len(train_dataloader)}")
        cam_views = {view: data[view].to(TrainArgs.device) for view in ACT_Config.image_keys}
        _, mu, logvar, *_ = policy(
            observation=data["obs"].to(TrainArgs.device),
            actions=data["actions"].to(TrainArgs.device),
            is_pad=data["episode_ids"].to(TrainArgs.device),
            cam_views=cam_views,
        )
        episode_ids.extend(data["episode_index"].detach().cpu().numpy())
        all_mu.append(mu.detach().cpu())
        all_logvar.append(logvar.detach().cpu())

    for batch_idx, data in enumerate(train_dataloader):
        print(f"Processing batch {batch_idx + 1}/{len(train_dataloader)}")
        cam_views = {view: data[view].to(TrainArgs.device) for view in ACT_Config.image_keys}
        _, mu, logvar, *_ = policy(
            observation=data["obs"].to(TrainArgs.device),
            actions=data["actions"].to(TrainArgs.device),
            is_pad=data["episode_ids"].to(TrainArgs.device),
            cam_views=cam_views,
        )
        episode_ids.extend(data["episode_index"].detach().cpu().numpy())
        all_mu.append(mu.detach().cpu())
        all_logvar.append(logvar.detach().cpu())

    # 1. Collect mu and logvar (as in your original code)
    mu_tensor = torch.cat(all_mu, dim=0)  # shape: [N, D]
    logvar_tensor = torch.cat(all_logvar, dim=0)  # shape: [N, D]
    episode_ids_np = np.array(episode_ids)

    # 2. Convert to numpy
    mu_np = mu_tensor.numpy()  # shape: [N, D]
    logvar_np = logvar_tensor.numpy()  # shape: [N, D]
    std_np = np.exp(0.5 * logvar_np)  # shape: [N, D]

    # 3. PCA
    pca = PCA(n_components=2)
    mu_2d = pca.fit_transform(mu_np)  # shape: [N, 2]

    # Project stds: for each sample, get 2D std in PCA space
    # shape: [N, D] @ [D, 2] -> [N, 2]
    projected_std = std_np @ pca.components_.T  # shape: [N, 2]

    # 4. Plot
    fig, ax = plt.subplots(figsize=(8, 6))

    # Scatter points

    # Add ellipses
    for i in range(mu_2d.shape[0]):
        x, y = mu_2d[i]
        dx, dy = projected_std[i]  # std in PC1 and PC2 direction
        e = Ellipse(
            (x, y),
            width=2 * dx,
            height=2 * dy,
            angle=0,  # axes already aligned with PCA axes
            edgecolor="none",
            facecolor="gray",
            alpha=0.2,
            zorder=0,
        )
        ax.add_patch(e)
    scatter = ax.scatter(mu_2d[:, 0], mu_2d[:, 1], c=episode_ids_np, cmap="tab20", s=5, alpha=0.9)

    plt.title("PCA of mu with projected std ellipses")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.colorbar(scatter, label="Episode ID")
    ax.set_aspect("equal")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main(
        dataset_prefix="/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/24/14.30.11/",
        load_checkpoint="/lucidxr/lucidxr/post_corl_2025/yajvan/mug_tree_randomization_v5/learn/2025/07/21/16-17-05/image_keys-wrist/0/checkpoints/policy_last.pt",
        load_from_cache=True,
        prune_local_cache=False,
        load_episodes=False,
    )
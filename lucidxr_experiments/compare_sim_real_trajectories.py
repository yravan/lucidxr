import random

import numpy as np
import pandas as pd
import torch
from dotvar import auto_load  # noqa
from matplotlib import pyplot as plt
from ml_logger import ML_Logger
from params_proto import PrefixProto

from lucidxr.learning.act_config import ACT_Config
from lucidxr.learning.episode_datasets import load_data_combined
from lucidxr.learning.train import TrainArgs

from lucidxr.learning.unroll_eval import UnrollEval

import zarr.core.sync as zsync

from vuer_mujoco.schemas.se3.rot_gs6 import gs62quat, quat2gs6
from vuer_mujoco.tasks.base.real_robot_env import RealRobotEnv

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

    print(f"[INFO] Loading dataset... from {TrainArgs.dataset_host}")
    train_dataloader, val_dataloader = load_data_combined(
        dataset_dirs=TrainArgs.dataset_prefix,
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


    ep_index = random.choice(range(1, 50))
    ep_index = 1

    index = train_dataloader.dataset.dataset_collection[0].episode_sizes[ep_index - 1]
    print(train_dataloader.dataset.dataset_collection[0].episode_paths[ep_index])
    first_chunk_0 = torch.cat((train_dataloader.dataset.dataset_collection[0][index + 0]["actions"],
                               train_dataloader.dataset.dataset_collection[0][index + 25]["actions"],
                               train_dataloader.dataset.dataset_collection[0][index + 50]["actions"],
                                 train_dataloader.dataset.dataset_collection[0][index + 75]["actions"],
                                 train_dataloader.dataset.dataset_collection[0][index + 100]["actions"],
                                 train_dataloader.dataset.dataset_collection[0][index + 125]["actions"],), dim=0)

    index = train_dataloader.dataset.dataset_collection[1].episode_sizes[ep_index - 1]
    print(train_dataloader.dataset.dataset_collection[1].episode_paths[ep_index])
    first_chunk_1 = torch.cat((train_dataloader.dataset.dataset_collection[1][index + 0]["actions"],
                                 train_dataloader.dataset.dataset_collection[1][index + 25]["actions"],
                                 train_dataloader.dataset.dataset_collection[1][index + 50]["actions"],
                                train_dataloader.dataset.dataset_collection[1][index + 75]["actions"],
                               train_dataloader.dataset.dataset_collection[1][index + 100]["actions"],
                               train_dataloader.dataset.dataset_collection[1][index + 125]["actions"],), dim=0)

    obs = torch.stack([train_dataloader.dataset.dataset_collection[1][index + i]["observation"] for i in range(train_dataloader.dataset.dataset_collection[1].episode_sizes[ep_index])])


    sc = plt.scatter(first_chunk_0[:, 0].numpy(), first_chunk_0[:, 1].numpy(), c=range(0, first_chunk_0.shape[0]), cmap="viridis", s=12, alpha=1)
    plt.colorbar(sc, label="Sim Dataset")
    sc = plt.scatter(first_chunk_1[:, 0].numpy(), first_chunk_1[:, 1].numpy(), c=range(0, first_chunk_1.shape[0]), cmap="Blues", s=12, alpha=1)
    plt.colorbar(sc, label="Real Dataset Actions (Mocap Pos)")
    # sc = plt.scatter(obs[:, 0].numpy(), obs[:, 1].numpy(), c=range(0, obs.shape[0]), cmap="hot", s=12, alpha=1)
    # plt.colorbar(sc, label="Real Dataset Observations (Qpos)")
    plt.legend()
    plt.title("First traj from Both Datasets")
    # plt.xlabel("Observation Dimension 1")
    # plt.ylabel("Observation Dimension 2")
    plt.show()
    # plt.plot(first_chunk_0[:,2].numpy(), label="Sim Dataset")
    # plt.plot(first_chunk_1[:,2].numpy(), label="Real Dataset")
    # plt.legend()
    # plt.show()
    #
    # loader = ML_Logger(prefix=Params.dataset_prefix[1])
    # print(loader.glob("*"))
    #
    # df = pd.DataFrame(loader.load_pkl("frames/ep_00002.pkl")[0])
    # obs, actions = loader.load_h5("data/ep_00002.h5:state,action")
    #
    # print("Loading real robot data, converting to mujoco pose.")
    # for i in range(len(obs)):
    #     o = obs[i]
    #     o = np.concatenate([o[:3], gs62quat(o[3:9])])
    #     o = RealRobotEnv.robot_to_mujoco_pose(o)
    #     obs[i] = np.concatenate([o[:3], quat2gs6(o[3:7]), [obs[i][9]]])
    #
    # for i in range(actions.shape[0]):
    #     a = actions[i]
    #     a = np.concatenate([a[:3], gs62quat(a[3:9])])
    #     a = RealRobotEnv.robot_to_mujoco_pose(a)
    #     actions[i] = np.concatenate([a[:3], quat2gs6(a[3:7]), [actions[i][9]]])
    #
    #
    # image_keys = ['right/rgb', 'wrist/rgb', 'left/rgb']
    # core_cols = ["mocap_pos", "mocap_quat", "qpos", "qvel", "ctrl"]
    # cam_cols = [c for c in image_keys if c in df.columns]
    # frames = df[core_cols + cam_cols].dropna()
    #
    # pos = np.stack(frames["mocap_pos"].to_numpy())  # (N, 3)
    #
    # x, y = pos[:, 0], pos[:, 1]
    #
    # plt.figure(figsize=(6, 6))
    # sc = plt.scatter(x, y, c = range(0,len(x)), cmap="hot", s=12, alpha=1)
    # plt.colorbar(sc, label="Pkl")
    # sc = plt.scatter(obs[:, 0], obs[:, 1], c = range(0,len(x)), cmap="viridis", s=12, alpha=1)
    # plt.colorbar(sc, label="h5 obs")
    # sc = plt.scatter(actions[:, 0], actions[:, 1], c = range(0,len(x)), cmap="Blues", s=12, alpha=1)
    # plt.colorbar(sc, label="h5 actions")
    # plt.xlabel("x")
    # plt.ylabel("y")
    # plt.title("Mocap trajectory (x–y)")
    # plt.axis("equal")
    # plt.show()


if __name__ == "__main__":
    main(
        **{
            "dataset_host": "http://escher.csail.mit.edu:4000",
            # "dataset_prefix": "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/pick_place_robot_room/2025/08/07/15.58.28/",
            "dataset_prefix": ["/lucidxr/lucidxr/datasets/lucidxr/corl-2025/pick_place_robot_room/2025/08/07/15.58.28/",
                                "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/pick_place_real/2025/08/07/16.43.17/"],
            "real_robot" : [False, True],
            "image_keys": ["right/rgb", "wrist/rgb", "left/rgb"],
            "load_from_cache": True,
            "prune_local_cache": False,
            "load_episodes": False,
        }
    )

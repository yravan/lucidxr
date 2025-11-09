import os
from time import sleep

import numpy as np
import torch
from matplotlib.pyplot import colormaps
from params_proto import ParamsProto, Proto

from vuer_mujoco.tasks import make


class RenderCfg(ParamsProto):
    env_name: str = Proto("lcs:Go1-flat_vision-v1")

    demo_prefix: str = Proto("lcs:Go1-flat_vision-v1")
    dataset_folder: str = None

    render_mode: str = Proto("rgb")

    device: str = "cuda" if torch.cuda.is_available() else "cpu"

    camera_lookat = [0, 0, 0]  # point to look at
    camera_distance = Proto(3)  # distance from points
    camera_azimuth = Proto(0)  # degrees in x-y plane (from x-axis)
    camera_elevation = Proto(230)  # degrees down from x-y plane

    custom_camera = Proto(False)


def render_one(dir, args):
    from ml_logger import ML_Logger

    loader = ML_Logger(dir)
    print(loader.get_dash_url())
    df = loader.read_metrics()["metrics.pkl"]
    mocap = df[["ts", "mpos", "mquat", "qpos", "act"]].dropna()
    observations = []
    actions = []

    env = make(args.env_name, device=args.device, random=0)

    if args.custom_camera:
        env.setCameraPose(args.camera_lookat, args.camera_distance, args.camera_azimuth, args.camera_elevation)

    obs = env.reset()
    observations.append(obs["observations"])

    cmap = colormaps.get_cmap("Spectral")

    frames = []
    mpos = np.zeros((3))
    mquat = np.zeros((4))
    for index, row in mocap.iterrows():
        action = np.hstack([row.mpos, row.mquat])[None, ...] - np.hstack([mpos, mquat])[None, ...]
        mpos = row.mpos
        mquat = row.mquat
        qpos = row.qpos
        act = row.act
        env.unwrapped.env.physics.set_mujoco_data(mocap_pos=mpos, mocap_quat=mquat, qpos=qpos, act=act)
        obs, _, _, info = env.step(action)
        actions.append(action)
        observations.append(obs["observations"])
        frames.append(info[f"render_{args.render_mode}"])
        for c_id in info[f"render_{args.render_mode}"]:
            image = frames[-1][c_id]
            image = image.transpose(1, 2, 0)
            if image.shape[2] == 1:
                image = np.squeeze(image)
                image = cmap(image)
            loader.save_image(image, key=f"render_{args.render_mode}/frame_{index:05d}_{c_id}.png")
            sleep(0.1)

    observations = observations[:-1]
    loader.save_pkl(observations, f"{env.unwrapped.env_id}_observations.pkl")
    loader.save_pkl(actions, f"{env.unwrapped.env_id}_actions.pkl")

    for c_id in frames[0]:
        record_frames = []
        for i, frame in enumerate(frames):
            image = frame[c_id]
            image = image.transpose(1, 2, 0)
            if image.shape[2] == 1:
                image = np.squeeze(image)
                image = cmap(image)
            record_frames.append(image)
        loader.save_video(record_frames, f"render_{args.render_mode}_{c_id}.mp4")


def render(args: RenderCfg):
    import jaynes

    jaynes.config("local")

    if args.dataset_folder is not None:
        loader = ML_Logger(args.dataset_folder)
        data_dirs = loader.glob("*/")
        for data_dir in data_dirs:
            jaynes.run(render_one, dir=os.path.join(args.dataset_folder, data_dir), args=args)
            # render_one(os.path.join(args.dataset_folder, data_dir), args)

        jaynes.listen()
    else:
        render_one(args.demo_prefix, args)

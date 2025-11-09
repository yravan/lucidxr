import os
from pathlib import Path

import numpy as np
from params_proto import Flag, ParamsProto, Proto

import torch
from lucidxr_base import make


class ReplayCfg(ParamsProto):
    env_name: str = Proto("lcs:Go1-flat_vision-v1")

    demo_prefix: str = Proto("lcs:Go1-flat_vision-v1")

    render = Flag("flag for rendering videos")
    render_mode: str = Proto("rgb")

    render_save_path: str = Proto("lcs:Go1-flat_vision-v1")

    device: str = "cuda" if torch.cuda.is_available() else "cpu"


def replay(args: ReplayCfg):
    from ml_logger import ML_Logger

    loader = ML_Logger(args.demo_prefix)
    print(loader.get_dash_url())
    df = loader.read_metrics()["metrics.pkl"]

    mocap = df[["ts", "mpos", "mquat"]].dropna()

    env = make(args.env_name, device=args.device, random=0)
    env.reset()

    frames = []
    for frame in mocap.to_dict(orient="records"):
        mpos = frame["mpos"]
        mquat = frame["mquat"]
        action = np.hstack([mpos, mquat])[None,...]
        _, _, _, info = env.step(action)
        frames.append(info[f"render_{args.render_mode}"])

    if args.render:
        loader.save_video(frames, args.render_save_path)


"""
[] replay a collected trajectory
[] output it & watch it
"""


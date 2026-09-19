"""Run a saved policy in a named scene; report execution without inventing success labels."""

import argparse
import json
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("--scene", required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--steps", type=int, default=100)
    parser.add_argument("--execute-steps", type=int, default=4)
    parser.add_argument(
        "--settle-steps", type=int, default=0, help="Physics warmup before the first observation"
    )
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--video", type=Path)
    args = parser.parse_args(argv)
    if args.steps < 1 or args.settle_steps < 0:
        parser.error("steps must be positive and settle-steps nonnegative")
    from contextlib import ExitStack
    from fractions import Fraction

    import av
    import numpy as np
    import torch

    from lucidxr.sim.mujoco_env import MujocoEnv
    from lucidxr.sim.scenes import make_scene
    from training.checkpoint import load_checkpoint
    from training.rollout import Controller

    torch.set_num_threads(2)
    saved = load_checkpoint(args.checkpoint)
    env = MujocoEnv(make_scene(args.scene, seed=args.seed), settle_steps=args.settle_steps)
    period = saved["data"]["control_period"]
    frame_skip = round(period / env.model.opt.timestep)
    if frame_skip < 1 or not np.isclose(frame_skip * env.model.opt.timestep, period, rtol=0, atol=1e-9):
        parser.error("Scene timestep cannot represent the trained control period")
    env.frame_skip = frame_skip
    try:
        env.reset(seed=args.seed)
        controller = Controller(
            args.checkpoint, env, execute_steps=args.execute_steps, device=args.device, seed=args.seed
        )
        with ExitStack() as stack:
            stream = None
            if args.video:
                args.video.parent.mkdir(parents=True, exist_ok=True)
                # Exclusive creation avoids overwriting an earlier rollout.
                output = stack.enter_context(args.video.open("xb"))
                container = stack.enter_context(av.open(output, "w", format="mp4"))
                stream = container.add_stream("libx264", rate=Fraction(1 / period).limit_denominator(100000))
                stream.width, stream.height, stream.pix_fmt = (
                    saved["contract"]["width"],
                    saved["contract"]["height"],
                    "yuv420p",
                )
            reward, terminated, truncated = 0.0, False, False
            norms = []
            try:
                for index in range(args.steps):
                    # Reuse the policy's camera captures for the optional diagnostic video.
                    with env.rendering.batch():
                        action = controller.action()
                        if stream is not None:
                            image = env.rendering.image(
                                saved["data"]["cameras"][0], stream.width, stream.height
                            )
                            frame = av.VideoFrame.from_ndarray(image, format="rgb24")
                            for packet in stream.encode(frame):
                                container.mux(packet)
                    norms.append(
                        float(
                            np.linalg.norm(np.concatenate([value.reshape(-1) for value in action.values()]))
                        )
                    )
                    _, value, terminated, truncated, _ = env.step(action)
                    reward += value
                    if terminated or truncated:
                        break
            finally:
                if stream is not None:
                    for packet in stream.encode():
                        container.mux(packet)
        print(
            json.dumps(
                {
                    "steps": index + 1,
                    "simulation_seconds": float(env.data.time),
                    "reward": reward,
                    "terminated": terminated,
                    "truncated": truncated,
                    "mean_command_norm": float(np.mean(norms)),
                    "inference_ms_p50": float(np.median(controller.inference_seconds) * 1000),
                    "success": None,
                },
                indent=2,
            )
        )
    finally:
        env.close()


if __name__ == "__main__":
    main()

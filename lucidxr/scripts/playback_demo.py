"""Replay saved physical frames without advancing physics or importing infra."""

import argparse
import time
from contextlib import nullcontext
from pathlib import Path

from lucidxr.sim.demos import Demo
from lucidxr.sim.mujoco_env import MujocoEnv


def playback(env, demo, *, speed=1.0, headless=False):
    if headless:
        context = nullcontext(None)
    else:
        import mujoco.viewer

        context = mujoco.viewer.launch_passive(env.model, env.data)
    with context as viewer:
        start = time.monotonic()
        for index, elapsed in enumerate(demo.elapsed):
            if viewer is not None:
                if not viewer.is_running():
                    break
                time.sleep(max(0, start + elapsed / speed - time.monotonic()))
            with viewer.lock() if viewer is not None else nullcontext():
                env.data.time = float(elapsed)
                env.restore_frame(demo.frame(index))
            if viewer is not None:
                viewer.sync()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("demo", type=Path)
    parser.add_argument("--assets", type=Path, help="Relocated matching asset tree")
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument(
        "--headless", action="store_true", help="Validate and restore all frames without a viewer"
    )
    args = parser.parse_args(argv)
    if not 0 < args.speed < float("inf"):
        parser.error("speed must be finite and positive")
    demo = Demo(args.demo)
    env = MujocoEnv(demo.scene(assets=args.assets))
    try:
        env.reset()
        for name, frames in demo.frames.items():
            if frames.shape[1:] != getattr(env.data, name).shape:
                raise ValueError(f"Recording {name} does not match the compiled model")
        playback(env, demo, speed=args.speed, headless=args.headless)
        print(f"Replayed {len(demo.elapsed)} frames from {args.demo}")
    finally:
        env.close()


if __name__ == "__main__":
    main()

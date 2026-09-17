"""Replay recorded states or apply mocap/ctrl commands through physics."""

import argparse
import time
from contextlib import nullcontext
from pathlib import Path

from lucidxr.scripts.replay_args import add_replay_arguments, replay_spec
from lucidxr.sim.demos import Demo
from lucidxr.sim.mujoco_env import MujocoEnv
from lucidxr.sim.playback import ReplaySpec, replay_frames


def playback(env, demo, *, speed=1.0, headless=False, spec=ReplaySpec()):
    if headless:
        context = nullcontext(None)
    else:
        import mujoco.viewer

        context = mujoco.viewer.launch_passive(env.model, env.data)
    with context as viewer:
        start = time.monotonic()
        frames = replay_frames(env, demo, spec)
        for index, elapsed in enumerate(demo.elapsed):
            if viewer is not None:
                if not viewer.is_running():
                    break
                time.sleep(max(0, start + elapsed / speed - time.monotonic()))
            with viewer.lock() if viewer is not None else nullcontext():
                next(frames)
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
    add_replay_arguments(parser)
    args = parser.parse_args(argv)
    if not 0 < args.speed < float("inf"):
        parser.error("speed must be finite and positive")
    demo = Demo(args.demo)
    spec = replay_spec(args)
    env = MujocoEnv(spec.make_scene(demo, assets=args.assets))
    try:
        env.reset()
        playback(env, demo, speed=args.speed, headless=args.headless, spec=spec)
        print(f"Replayed {len(demo.elapsed)} frames from {args.demo}")
    finally:
        env.close()


if __name__ == "__main__":
    main()

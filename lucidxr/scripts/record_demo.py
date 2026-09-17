"""Record simulator frames using Vuer's browser/VR controls."""

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

from lucidxr.sim.mujoco_env import MujocoEnv
from lucidxr.sim.scenes import SCENES, make_scene


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scene", choices=SCENES)
    parser.add_argument("--output", type=Path, required=True, help="Filesystem directory for demo files")
    parser.add_argument("--assets", type=Path)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--scene-options", type=json.loads, default={}, help="Scene options as a JSON object")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8012)
    parser.add_argument("--public-url", help="Reachable HTTP(S) server URL, e.g. your HTTPS proxy")
    parser.add_argument("--right-actuator", help="Named actuator controlled by right-hand pinch")
    parser.add_argument("--left-actuator", help="Named actuator controlled by left-hand pinch")
    parser.add_argument("--fps", type=int, default=50)
    parser.add_argument("--max-frames", type=int, default=30000)
    args = parser.parse_args(argv)
    if not isinstance(args.scene_options, dict) or {"seed", "assets"} & args.scene_options.keys():
        parser.error("scene-options must be an object without seed/assets; use their explicit flags")
    if not 1 <= args.port <= 65535 or args.fps < 1 or args.max_frames < 1:
        parser.error("Invalid port, fps or max-frames")
    if args.public_url:
        url = urlparse(args.public_url)
        if url.scheme not in ("http", "https") or not url.netloc or url.query or url.fragment:
            parser.error("public-url must be an HTTP(S) base URL")
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    from lucidxr.sim.teleop.vuer import collect

    scene = make_scene(args.scene, assets=args.assets, seed=args.seed, **args.scene_options)
    env = MujocoEnv(scene)
    try:
        env.reset(seed=args.seed)
        collect(
            env,
            args.scene,
            output,
            host=args.host,
            port=args.port,
            public_url=args.public_url,
            right_actuator=args.right_actuator,
            left_actuator=args.left_actuator,
            fps=args.fps,
            max_frames=args.max_frames,
        )
    finally:
        env.close()


if __name__ == "__main__":
    main()

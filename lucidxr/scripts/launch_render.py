"""Launch a versioned code snapshot and recordings through Jaynes on MIT Slurm."""

import argparse
import json
import logging
import shutil
import tempfile
from pathlib import Path

from lucidxr.scripts.replay_args import add_replay_arguments, replay_spec


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("demos", type=Path, nargs="+")
    parser.add_argument("--cluster", required=True)
    parser.add_argument("--infra-config", type=Path)
    parser.add_argument("--cameras", nargs="+", required=True)
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=360)
    parser.add_argument("--fps", type=int, default=50)
    parser.add_argument("--products", nargs="+", default=["rgb"], choices=["rgb", "depth", "segmentation"])
    parser.add_argument("--dry-run", action="store_true")
    add_replay_arguments(parser)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    from infra.cluster import cluster
    from infra.launch import launch_render
    from lucidxr.rendering.jobs import plan
    from lucidxr.rendering.spec import RenderSpec

    profile = cluster(args.cluster, config=args.infra_config)
    spec = RenderSpec(
        tuple(args.cameras), args.width, args.height, args.fps, tuple(args.products), replay_spec(args)
    )
    jobs, inputs = plan(args.demos, spec)
    with tempfile.TemporaryDirectory(prefix="lucidxr-launch-") as temporary:
        payload = Path(temporary) / "render_inputs"
        payload.mkdir()
        for relative, source in inputs.items():
            target = payload / relative
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(source, target)
        (payload / "plan.json").write_text(json.dumps(jobs, indent=2))
        launch_render(
            profile, Path(__file__).resolve().parents[2], payload, len(jobs["items"]), dryrun=args.dry_run
        )


if __name__ == "__main__":
    main()

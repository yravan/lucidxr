"""Capture code, stage an explicit cache and launch one MIT GPU training job."""

import argparse
import logging
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--cluster", required=True)
    parser.add_argument("--infra-config", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--wandb", choices=("disabled", "offline", "online"), default="offline")
    parser.add_argument("--project", default="lucidxr")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    from infra.cluster import cluster
    from infra.training import launch_training

    profile = cluster(args.cluster, config=args.infra_config)
    launch_training(
        profile,
        Path(__file__).resolve().parents[2],
        args.config,
        args.data,
        dryrun=args.dry_run,
        wandb_mode=args.wandb,
        project=args.project,
    )


if __name__ == "__main__":
    main()

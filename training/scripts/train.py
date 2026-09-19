"""Train any supported policy locally or from a captured MIT job."""

import argparse
import logging
from pathlib import Path
from uuid import uuid4


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("--data", required=True, type=Path)
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument("--output", type=Path)
    destination.add_argument("--location")
    parser.add_argument("--infra-config", type=Path)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--wandb", choices=("disabled", "offline", "online"), default="offline")
    parser.add_argument("--project", default="lucidxr")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    from training.config import read_config
    from training.trainer import train

    output = args.output
    if output is None:
        if args.resume:
            parser.error("Resume needs the existing --output path")
        from infra.locations import location

        output = location(args.location, config=args.infra_config) / uuid4().hex
    print(
        train(
            args.data,
            output,
            read_config(args.config),
            resume=args.resume,
            wandb_mode=args.wandb,
            project=args.project,
        )
    )


if __name__ == "__main__":
    main()

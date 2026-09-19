"""A captured cluster job stages data, then calls the same ordinary trainer."""

import argparse
import json
import logging
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    from infra.training import training_cache
    from training.config import read_config
    from training.trainer import train

    job = json.loads(args.job.read_text())
    with training_cache(job["cache"], job["fingerprint"]) as cache:
        print(
            train(
                cache,
                args.output,
                read_config(args.job.parent / "config.toml"),
                resume=True,
                wandb_mode=job["wandb"],
                project=job["project"],
            )
        )


if __name__ == "__main__":
    main()

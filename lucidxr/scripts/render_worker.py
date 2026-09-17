"""Run one manifest item or verify completion of the entire work set."""

import argparse
import logging
import os
import tempfile
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--index", type=int)
    action.add_argument("--collect", action="store_true")
    action.add_argument("--worker-index", type=int)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument(
        "--scratch", type=Path, default=Path(os.environ.get("SLURM_TMPDIR", tempfile.gettempdir()))
    )
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    from lucidxr.rendering.jobs import collect, run_item

    if args.collect:
        print(collect(args.manifest, args.output))
    elif args.worker_index is not None:
        from infra.rendering import run_worker

        run_worker(args.manifest, args.worker_index, args.workers, args.output, args.scratch)
    else:
        if args.index < 0:
            parser.error("index must be nonnegative")
        print(run_item(args.manifest, args.index, args.output))


if __name__ == "__main__":
    main()

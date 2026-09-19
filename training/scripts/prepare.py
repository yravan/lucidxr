"""Prepare a derived training cache from explicit HDF5/MP4 render results."""

import argparse
import logging
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("recipe", type=Path)
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument("--output", type=Path)
    destination.add_argument(
        "--location", help="Named infra root; cache identity becomes the child directory"
    )
    parser.add_argument("--infra-config", type=Path)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    from training.data.manifest import file_hash
    from training.data.prepare import prepare

    output = args.output
    if output is None:
        from infra.locations import location

        output = location(args.location, config=args.infra_config) / file_hash(args.recipe)
    print(prepare(args.recipe, output))


if __name__ == "__main__":
    main()

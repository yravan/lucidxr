"""Render one recording into a verified HDF5 file and paired camera videos."""

import argparse
import logging
from pathlib import Path

from lucidxr.rendering.spec import RenderSpec


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("demo", type=Path)
    output = parser.add_mutually_exclusive_group(required=True)
    output.add_argument("--output", type=Path)
    output.add_argument("--output-location", help="Named root in infra configuration")
    parser.add_argument("--infra-config", type=Path)
    parser.add_argument("--assets", type=Path)
    parser.add_argument("--cameras", nargs="+", required=True, help="Exact MuJoCo camera names")
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=360)
    parser.add_argument("--fps", type=int, default=50, help="Video playback rate, not recorded control rate")
    parser.add_argument("--products", nargs="+", default=["rgb"], choices=["rgb", "depth", "segmentation"])
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    destination = args.output
    if args.output_location:
        from infra import location

        destination = location(args.output_location, config=args.infra_config)
    from lucidxr.rendering.replay import render_demo

    record = render_demo(
        args.demo,
        destination,
        RenderSpec(tuple(args.cameras), args.width, args.height, args.fps, tuple(args.products)),
        assets=args.assets,
    )
    print(record)


if __name__ == "__main__":
    main()

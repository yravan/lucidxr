"""Resolve configured locations and inspect or retry captured remote launches."""

import argparse
import logging


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    paths = commands.add_parser("path", help="Print a configured filesystem location")
    paths.add_argument("name")
    paths.add_argument("--config", help="Override ~/.config/lucidxr/infra.toml")
    for command in ("status", "resume"):
        commands.add_parser(command).add_argument("receipt", help="Saved launch.json")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    try:
        if args.command == "path":
            from .locations import location

            print(location(args.name, config=args.config))
        elif args.command == "status":
            from .launch import status

            print(status(args.receipt))
        else:
            from .recovery import resume

            print(resume(args.receipt))
    except (OSError, ValueError, RuntimeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()

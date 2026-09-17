"""Print a configured path for tools that accept ordinary filesystem paths."""

import argparse

from .locations import location


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("path",))
    parser.add_argument("name", help="Location name in your infra TOML")
    parser.add_argument("--config", help="Override ~/.config/lucidxr/infra.toml")
    args = parser.parse_args(argv)
    try:
        print(location(args.name, config=args.config))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()

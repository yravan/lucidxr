"""List scenes, export XML, or smoke-check the complete catalogue."""

import argparse
from pathlib import Path

from lucidxr.sim.scenes import SCENES, build_xml, compile_model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list")
    build = commands.add_parser("build")
    build.add_argument("scene", choices=SCENES)
    build.add_argument("output", type=Path)
    build.add_argument("--assets", type=Path)
    build.add_argument("--seed", type=int, default=0)
    check = commands.add_parser("check")
    check.add_argument("scenes", nargs="*", choices=SCENES)
    check.add_argument("--assets", type=Path)
    args = parser.parse_args()
    if args.command == "list":
        print("\n".join(SCENES))
    elif args.command == "build":
        xml = build_xml(args.scene, assets=args.assets, seed=args.seed)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(xml)
        print(args.output)
    else:
        import mujoco
        import numpy as np

        failed = []
        for scene in args.scenes or SCENES:
            try:
                model = compile_model(scene, assets=args.assets)
                data = mujoco.MjData(model)
                mujoco.mj_step(model, data)
                if not np.isfinite(data.qpos).all():
                    raise ValueError("Non-finite state after stepping")
                print(f"OK {scene}: {model.nbody} bodies, {model.nmesh} meshes", flush=True)
            except Exception as error:
                failed.append(scene)
                print(f"FAIL {scene}: {error}", flush=True)
        if failed:
            raise SystemExit(1)


if __name__ == "__main__":
    main()

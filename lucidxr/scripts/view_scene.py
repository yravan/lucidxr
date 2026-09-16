"""Inspect a scene's controls or open it in MuJoCo's native viewer."""

import argparse

from lucidxr.sim.mujoco_env import MujocoEnv
from lucidxr.sim.scenes import SCENES, make_scene


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scene", choices=SCENES)
    parser.add_argument("--assets")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--describe", action="store_true", help="Print camera, mocap and actuator names, then exit"
    )
    args = parser.parse_args(argv)
    env = MujocoEnv(make_scene(args.scene, assets=args.assets, seed=args.seed))
    try:
        env.reset(seed=args.seed)
        if args.describe:
            for index in range(env.model.ncam):
                print(f"camera: {env.model.camera(index).name}")
            for index in range(env.model.nbody):
                if env.model.body_mocapid[index] >= 0:
                    print(f"mocap: {env.model.body(index).name}")
            for index in range(env.model.nu):
                low, high = env.action_space["ctrl"].low[index], env.action_space["ctrl"].high[index]
                print(f"actuator: {env.model.actuator(index).name} [{low}, {high}]")
        else:
            import mujoco.viewer

            mujoco.viewer.launch(env.model, env.data)
    finally:
        env.close()


if __name__ == "__main__":
    main()

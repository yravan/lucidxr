import colorsys
import os
import sys
from asyncio import sleep
from datetime import datetime
from importlib import import_module
from os.path import join
from time import perf_counter
from typing import List, Literal
import numpy as np

# from dotvar import auto_load  # noqa
from params_proto import ARGS, Flag, ParamsProto, Proto
from termcolor import colored

from vuer_mujoco.schemas.se3.rot_gs6 import quat2gs6
from vuer_mujoco.scripts.util.working_directory_context_manager import WorkDir

from vuer_mujoco.scripts.util.relative_mocap_tracker import RelativeMocapTracker
from vuer_mujoco.tasks import make


def pi2_hsv(pi):
    """return '#RRGGBB' for a given angle in radians."""
    r, g, b = colorsys.hsv_to_rgb((pi % (2 * 3.14159)) / (2 * 3.14159), 1, 1)
    return [int(r * 255), int(g * 255), int(b * 255)]


def parse_num_list(s):
    return [*map(int, s.split(","))]


class Params(ParamsProto, cli_parse=False):
    """Script for collecting virtual reality demos.

    - [x] install collect_demo.py as a cli
    - [x] write params-proto for setting the work dir etc
    - [x] load an example scene (UR5)
    - [ ] add logic to glob and find all files in the directory
    - ask Yajjy to make a scene with a UR5 and a table
    - add ml-logger prefix/dir structure.
    - document in the docs / Notion page.
    """

    wd: str = Proto(env="PWD", help="Working directory")
    vuer_port = Proto(8012, env="PORT", help="vuer port")

    name: str = "scene"
    assets: str = "{name}"
    entry_file: str = "{name}.mjcf.xml"
    factory_fn: str = None
    assets_cache_prefix = Proto(env="$LUCIDXR_CACHE")

    demo_prefix: str = f"lucidxr/lucidxr/datasets/lucidxr/corl-2025/{{name}}/{datetime.now():%Y/%m/%d/%H.%M.%S}/"

    # asset_prefix: str = Proto("http://localhost:{vuer_port}/static", env="ASSET_PREFIX")
    asset_prefix: str = Proto(env="https://$USER-vuer-port.ngrok.app/static")
    asset_paths: List[str] = None

    frame_keys: str = Proto("mocap_pos mocap_quat qpos qvel site_xpos site_xmat ctrl sensordata")
    init_keyframe: dict = {}
    init_fn: str = None
    clip_head: int = 10

    src: str = "{asset_prefix}/{entry_file}"
    visible_groups: List[int] = Proto([0, 1, 2], help="Visible groups", dtype=parse_num_list)
    show_lights: bool = Flag("Show lights, default to false to speed up rendering.")
    actuators: Literal["mono", "duo", "none"] = Proto("mono", help="mono | duo | none  Use none for hands.")

    verbose = Flag(help="Print out the assets that are being loaded.")
    reset_time: float = Proto(1.0, help="Time delay before starting trajectory recording (in seconds).")

    def __post_init__(self):
        for k, v in self.__dict__.items():
            if isinstance(v, str):
                value = v.format(**self.__dict__)
                setattr(self, k, value)

                if self.verbose:
                    print(f"{colored(k, 'cyan')}:\t{colored(value, 'yellow')}")


def main():
    # need to do local import to avoid the schema parsing side effect.

    # need to manually parse because the cli_parse is set to False.
    ARGS.parse_args()

    args = Params()

    from ml_logger import logger
    from vuer import Vuer, VuerSession
    from vuer.events import ClientEvent
    from vuer.schemas import MuJoCo

    from vuer_mujoco.schemas.utils.collect_asset_paths import collect_asset_paths

    # current work directory should have already been set.
    vuer = Vuer(static_root=".", port=args.vuer_port)

    if args.factory_fn:
        path = "/static/" + args.name + ".mjcf.xml"
        print("adding args.src", path)

        def build_fn():
            print(args.factory_fn)
            module_name, fn_name = args.factory_fn.rsplit(":", 1)

            # auto-reload
            if module_name in sys.modules:
                del sys.modules[module_name]

            m = import_module(module_name)
            # todo: add arguments to the make_schema function call
            xml = getattr(m, fn_name)(mode="demo", dual_gripper=args.actuators == "duo")
            # with open("example_file.mjcf.xml", "w") as f:
            #     f.write(xml)
            return xml

        vuer.add_route(path, build_fn)

    logger.configure(prefix=args.demo_prefix)
    logger.job_started(vars(args))

    # change the work directory.
    os.chdir(args.wd)

    asset_folder = join(args.assets)
    file_path = args.entry_file

    assets = collect_asset_paths(file_path)
    args.asset_paths = [join(args.asset_prefix, args.assets, asset) for asset in assets]
    # print(f"Found {len(assets)} assets in {args.src}")
    print(f"Found {len(assets)} assets in {asset_folder}")

    if args.verbose:
        print("Assets:")
        print(*assets, sep="\n")
        print("----------------------------------")
        print("Asset Paths:")
        print(*args.asset_paths, sep="\n")

    if args.assets_cache_prefix:
        print("Using the local cache folder at")
        print(args.assets_cache_prefix)

    print("Visit: https://vuer.ai/editor?ws=" + args.asset_prefix.replace("https://", "wss://").replace("/static", ""))

    from datetime import datetime

    now = datetime.now()

    IS_LOADED = False

    @vuer.add_handler("ON_CONTRIB_LOAD")
    async def on_contrib_load(event: ClientEvent, proxy: VuerSession):
        nonlocal IS_LOADED

        IS_LOADED = True
        print("ON_CONTRIB_LOAD event", event.value)

    box_state = "#23aaff"

    _t = None

    class TrackerValue:
        val = None

    tracker = RelativeMocapTracker()
    mj_env = make(args.mj_env_name, strict=False)
    mj_env.reset()

    @vuer.add_handler("HAND_MOVE")
    async def handle_hand_movement(event, session):
        nonlocal _t, mj_env
        """Handle hand movement events and compute mocap point and control value"""
        hand_data = event.value

        # Get right hand data (since your HandActuator uses "right-squeeze" and "right:thumb-tip,right:index-finger-tip")
        if hand_data.get("right") and hand_data.get("rightState"):
            right_poses = hand_data["right"]
            right_state = hand_data["rightState"]

            TrackerValue.val = tracker.update(
                hand_poses=right_poses,
                hand_state=right_state,
                joint_name="wrist",  # for tracking position / orientation
                value="right:thumb-tip,right:index-finger-tip",  # value to use for pinch
                squeeze_condition="squeeze",  # condition to check for squeeze
                physics=mj_env.unwrapped.env.physics,  # pass the physics object
                align_mujoco_frame=True,
            )

    @vuer.add_handler("ON_MUJOCO_LOAD")
    async def on_load(event: ClientEvent, proxy: VuerSession):
        print("ON_MUJOCO_LOAD event")

    with WorkDir(args.wd):

        @vuer.spawn(start=True)
        async def main(proxy: VuerSession):
            nonlocal IS_LOADED, box_state, mj_env

            IS_LOADED = False

            t0 = perf_counter() + 5.0

            while not IS_LOADED and perf_counter() < t0:
                print("\rwaiting for module load...")
                await sleep(1.0)
            if not IS_LOADED:
                print("timed out after five seconds. Trying to load.")

            print("now insert MuJoCo component.")
            physics = mj_env.unwrapped.env.physics
            qpos = physics.data.qpos

            proxy.upsert @ MuJoCo(
                key="default-sim",
                src=args.src,  # + f"?ts={now:0.3f}",
                assets=args.asset_paths,
                frameKeys=args.frame_keys,
                pause=True,
                # turn of light to make it run faster.
                useLights=args.show_lights,
                visible=args.visible_groups,
                fps=50,
                qpos=qpos,
                useMocap=False,
            )

            await sleep(1.0)

            _box_state = None

            while TrackerValue.val is None:
                print("Waiting for tracker value to be set...")
                await sleep(0.2)

            while True:
                t0 = perf_counter()
                pos = TrackerValue.val["position"]
                quat = TrackerValue.val["quaternion"]
                control = TrackerValue.val["control"]

                action = np.array([*pos, *quat2gs6(quat), control])

                if action is None:
                    continue

                mj_env.step(action)
                t2 = perf_counter()
                print(f"sim time: {t2 - t0:.3f} seconds")
                proxy.update @ MuJoCo(key="default-sim", qpos=qpos.tolist())
                t1 = perf_counter()
                print(f"Time taken for step: {t1 - t0:.3f} seconds")

                await sleep(max(0.02 - (t1 - t0), 0.005))

    logger.job_completed()


if __name__ == "__main__":
    from vuer import Vuer
    from killport import kill_ports

    kill_ports(ports=[8012])

    Params.wd = "../tasks"
    Params.show_lights = False
    Params.assets = "assets"

    Params.name = "mug_tree"
    Params.entry_file = "mug_tree.mjcf.xml"
    Params.factory_fn = "vuer_mujoco.tasks.mug_tree:make_schema"
    # Params.init_fn = "vuer_mujoco.tasks.mug_tree:MugRandom"
    Params.mj_env_name = "MugTree-fixed-v1"

    # Params.name = "mug_tree_ur"
    # Params.entry_file = "mug_tree_ur.mjcf.xml"
    # Params.factory_fn = "vuer_mujoco.tasks.mug_tree_ur:make_schema"
    # Params.init_fn = "vuer_mujoco.tasks.mug_tree_ur:MugFixed"

    # Params.name = "tie_knot"
    # Params.entry_file = "tie_knot.mjcf.xml"
    # Params.factory_fn = "vuer_mujoco.tasks.tie_knot:make_schema"
    # Params.init_fn = "vuer_mujoco.tasks.tie_knot:RopeRandom"

    # Params.name = "pick_place"
    # Params.entry_file = "pick_place.mjcf.xml"
    # Params.factory_fn = "vuer_mujoco.tasks.pick_place:make_schema"
    # Params.mj_env_name = "PickPlace-v1"

    # Params.name = "ball_sorting_toy"
    # Params.entry_file = "ball_sorting_toy.mjcf.xml"
    # Params.factory_fn = "vuer_mujoco.tasks.ball_sorting_toy:make_schema"
    # Params.mj_env_name = "BallSortingToy-v1"
    # Params.init_fn = "vuer_mujoco.tasks.ball_sorting_toy:BallRandom"

    # Params.name = "fishing_toy"
    # Params.entry_file = "fishing_toy.mjcf.xml"
    # Params.factory_fn = "vuer_mujoco.tasks.fishing_toy:make_schema"

    # Params.name = "basketball_shot"
    # Params.entry_file = "basketball_shot.mjcf.xml"
    # Params.factory_fn = "vuer_mujoco.tasks.basketball_shot:make_schema"

    # Params.name = "flip_mug"
    # Params.entry_file = "flip_mug.mjcf.xml"
    # Params.factory_fn = "vuer_mujoco.tasks.flip_mug:make_schema"

    # Params.name = "mug_drawer"
    # Params.entry_file = "mug_drawer.mjcf.xml"
    # Params.factory_fn = "vuer_mujoco.tasks.mug_drawer:make_schema"

    Params.actuators = "mono"
    Vuer.cors = "https://vuer.ai,*"

    main()

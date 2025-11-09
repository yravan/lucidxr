import os
import sys
from importlib import import_module
from os.path import join
from pathlib import Path
from time import perf_counter
from asyncio import sleep


import imageio
import numpy as np
import torch
from dotvar import auto_load
from ml_logger import ML_Logger
from vuer.schemas import Line, Arrow

from lucidxr.learning.act_config import ACT_Config
from lucidxr.learning.unroll_eval import load_policy, UnrollEval, ActionGenerator
from lucidxr.learning.utils import set_seed
from vuer_mujoco.scripts.util.color_palette import interpolate
from vuer_mujoco.scripts.util.working_directory_context_manager import WorkDir
from params_proto import ParamsProto, Proto, Flag, ARGS
from typing import List, Literal

from vuer_mujoco.tasks import make
NEON_WHEEL = [
    (77, 238, 234),  # 4deeea
    (116, 238, 21),  # 74ee15
    (255, 231, 0),  # ffe700
    (240, 0, 255),  # f000ff
    (0, 30, 255),  # 001eff
]


def parse_num_list(s):
    return [*map(int, s.split(","))]


class Params(ParamsProto):
    dataset_host: str = Proto(env="ML_LOGGER_HOST")
    dataset_prefix = [
        "lucidxr/lucidxr/datasets/lucidxr/rss-demos/pick_block/2025/03/31",
        "lucidxr/lucidxr/datasets/lucidxr/rss-demos/pick_place/2025/03/31",
        "lucidxr/lucidxr/datasets/lucidxr/rss-demos/flip_mug/2025/03/31",
    ]

    wd: str = "../vuer_mujoco/tasks"
    vuer_port = Proto(8012, env="PORT", help="vuer port")

    name: str = "scene"
    assets: str = "assets"
    entry_file: str = "{name}.mjcf.xml"
    factory_fn: str = None
    assets_cache_prefix = Proto(env="$LUCIDXR_CACHE")

    asset_prefix: str = Proto(env="https://$USER-vuer-port.ngrok.app/static")
    asset_paths: List[str] = None

    init_keyframe: dict = {}
    init_fn: str = None
    clip_head: int = 10

    src: str = "{asset_prefix}/{entry_file}"
    visible_groups: List[int] = Proto([0, 1, 2], help="Visible groups", dtype=parse_num_list)
    show_lights: bool = Flag("Show lights, default to false to speed up rendering.")
    actuators: Literal["mono", "duo", "none"] = Proto("mono", help="mono | duo | none  Use none for hands.")
    frame_keys: str = Proto("mocap_pos mocap_quat qpos qvel site_xpos site_xmat ctrl sensordata")

    verbose = Flag(help="Print out the assets that are being loaded.")
    reset_time: float = Proto(1.0, help="Time delay before starting trajectory recording (in seconds).")

    # visualization parameters
    line_width = 0.5
    line_brightness = 0.05

    env_name = Proto(None, help="Environment name to use for visualization. Defaults to None.")
    policy_checkpoints = Proto(None, help="Path to the policy checkpoint to visualize. Defaults to None.")
    seed = Proto(0, help="Seed for the environment. Defaults to 0.")


def visualize(**deps):
    # Placeholder for visualization logic
    print("Visualizing dataset...")
    # need to manually parse because the cli_parse is set to False.
    ARGS.parse_args()

    args = Params()
    set_seed(args.seed)

    from vuer import Vuer, VuerSession
    from vuer.events import ClientEvent
    from vuer.schemas import Box, HandActuator, Html, MuJoCo, Octahedron, Sphere, group, span

    from vuer_mujoco.schemas.utils.collect_asset_paths import collect_asset_paths

    logger = ML_Logger(args.dataset_host)

    with logger.PrefixContext(args.dataset_prefix[0]):
        load_pkl = logger.memoize(logger.load_pkl)
        # params = load_pkl("parameters.pkl")[0]["job"]
        # args.name = params["name"]
        # args.factory_fn = params["factory_fn"]
        # args.init_fn = params["init_fn"]
        args.entry_file = "pick_place_robot_room.mjcf.xml"
        print(args.name)
        args.src = "{asset_prefix}/{name}.mjcf.xml".format(**args.__dict__)
        args.__post_init__()

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

    def _get_mujoco_model(
        *,
        mode: Literal["mono", "duo", "none"],
        visible=None,
        show_lights=None,
    ):
        actuators = []

        if mode.lower() in ["mono", "duo"]:
            actuators += [
                HandActuator(
                    key="pinch-on-squeeze",
                    cond="right-squeeze",
                    value="right:thumb-tip,right:index-finger-tip",
                    offset=0.10,
                    scale=-12,
                    low=-0,
                    high=1,
                    ctrlId=-1,
                ),
            ]
        if mode.lower() == "duo":
            actuators += [
                HandActuator(
                    key="left-pinch-on-squeeze",
                    cond="left-squeeze",
                    value="left:thumb-tip,left:index-finger-tip",
                    offset=0.10,
                    scale=-12,
                    low=0,
                    high=1,
                    ctrlId=-2,
                ),
            ]

        return MuJoCo(
            *actuators,
            key="default-sim",
            src=args.src,  # + f"?ts={now:0.3f}",
            assets=args.asset_paths,
            frameKeys=args.frame_keys,
            pause=True,
            # turn of light to make it run faster.
            useLights=show_lights,
            visible=visible,
            mocapHandleSize=0.05,
            mocapHandleWireframe=True,
            fps=50,
            **args.init_keyframe,
        )

    IS_LOADED = False

    @vuer.add_handler("ON_CONTRIB_LOAD")
    async def on_contrib_load(event: ClientEvent, proxy: VuerSession):
        nonlocal IS_LOADED

        IS_LOADED = True
        print("ON_CONTRIB_LOAD event", event.value)

    @vuer.add_handler("ON_MUJOCO_LOAD")
    async def on_load(event: ClientEvent, proxy: VuerSession):
        frame = event.value["keyFrame"]
        print("ON_MUJOCO_LOAD event")

    @vuer.spawn(start=True)
    async def main(proxy: VuerSession):
        nonlocal IS_LOADED

        IS_LOADED = False

        t0 = perf_counter() + 5.0

        while not IS_LOADED and perf_counter() < t0:
            print("\rwaiting for module load...")
            await sleep(1.0)
        if not IS_LOADED:
            print("timed out after five seconds. Trying to load.")

        print("now insert MuJoCo component.")

        proxy.upsert @ _get_mujoco_model(mode=args.actuators, visible=args.visible_groups, show_lights=args.show_lights)

        await sleep(1.0)

        for dataset in args.dataset_prefix:
            with logger.Prefix(dataset):
                # load_pkl = logger.memoize(logger.load_pkl)
                load_pkl = logger.load_pkl

                metric_files = logger.glob("**/ep_*.pkl")
                metric_files = sorted(metric_files)

                from pandas import DataFrame
                from tqdm import tqdm

                metrics = {}
                for k in tqdm(metric_files, desc="Loading metrics"):
                    metrics[k] = DataFrame(load_pkl(k)[0])
                print("Found", len(metrics), "metrics")

            # Set up the scene with Fog to simulate MuJoCo's default style.
            for i, (key, df) in enumerate(metrics.items()):
                try:
                    mocap_traj = df["mocap_pos"].dropna()
                    visualize_trajectory_with_arrows(
                        proxy,
                        mocap_traj.values,
                        df["mocap_quat"].dropna().values,
                        key=f"traj-{Path(dataset).name}-{key}",
                        color=interpolate(*NEON_WHEEL, x=i / len(metrics.keys()), scale=args.line_brightness),
                    )
                except KeyError:
                    print("no stuff")
            await sleep(2.0)

        # if args.env_name is not None:
        #     for _, policy in enumerate(args.policy_checkpoints):
        #         print("Visualizing policy for environment:", args.env_name)
        #         UnrollEval._update(**{"load_checkpoint": policy, "env_name": args.env_name})
        #         env = make(args.env_name, strict=False)
        #         policy = load_policy()
        #         images = {}
        #         with logger.PrefixContext(args.dataset_prefix[0]):
        #             for image_key in ACT_Config.image_keys:
        #                 image = logger.load_file(f"render/ep_00007/{image_key}/00000.png")
        #                 images[image_key] = imageio.v3.imread(image)
        #                 print(f"Loaded image {image_key}")
        #             obs, actions = logger.load_h5("data/ep_00007.h5" + ":state,action")
        #             actions = torch.from_numpy(actions[None, 1:101, :]).to(UnrollEval.device, dtype=torch.float32)
        #
        #         await visualize_policy(proxy, env, policy, key = f"policy_{_}",images=images, actions = actions, color=interpolate(*NEON_WHEEL, x=_/len(args.policy_checkpoints), scale=args.line_brightness))

        while True:
            await sleep(5000)


async def visualize_policy(proxy, env, policy, images=None, actions=None, color=[255, 0, 0], key="policy_trajectory_"):
    is_pad = torch.zeros(1, 100).to(UnrollEval.device, dtype=torch.bool)
    action_generator = ActionGenerator(policy)
    obs = env.reset()
    if images is not None:
        obs.update(**images)
    for seed in range(Params.seed, Params.seed + 10):
        print(f"Visualizing policy for seed {seed}...")
        set_seed(seed)
        _, first_chunk = action_generator(obs, actions=actions, is_pad=is_pad)
        traj_positions = first_chunk[:, :3].tolist()  # Extract positions * seed
        traj_rotations = first_chunk[:, 3:7].tolist()  # Extract rotations (quaternions)
        first_chunk[:, :3] = first_chunk[:, :3] + 0.02
        print(first_chunk[0], first_chunk[-1])
        _, first_chunk_reconstructed = action_generator(
            obs, actions=torch.from_numpy(first_chunk[None, ...]).to(UnrollEval.device, dtype=torch.float32), is_pad=is_pad
        )

        visualize_trajectory_with_arrows(proxy, traj_positions, traj_rotations, key=f"{key}_{seed}", color=color)
        visualize_trajectory_with_arrows(
            proxy,
            actions[0, :, :3].cpu().numpy().tolist(),
            actions[0, :, 3:7].cpu().numpy().tolist(),
            key=f"{key}_actions_{seed}",
            color=[0, 0, 255],
        )
        # visualize_trajectory_with_arrows(proxy, first_chunk[:, :3].tolist(), first_chunk[:, 3:7].tolist(), key=f"{key}_pre_{seed}", color=[0, 255, 255])
        # visualize_trajectory_with_arrows(proxy, first_chunk_reconstructed[:, :3].tolist(), first_chunk_reconstructed[:, 3:7].tolist(), key=f"{key}_reconstructed_{seed}", color=[255, 0, 255])
        break


from scipy.spatial.transform import Rotation as R


def visualize_trajectory_with_arrows(proxy, traj_positions, traj_quat, key, **kwargs):
    """
    traj_positions: List of [x, y, z] points
    traj_rotations: List of [rx, ry, rz] angles (Euler)
    step: Use every Nth point to reduce clutter
    """
    n = len(traj_positions)
    NEON_GRADIENT = [
        [0, 255, 0],  # green
        [255, 255, 0],  # yellow
        [255, 0, 0],  # red
    ]

    colors = [interpolate(*NEON_GRADIENT, x=i / (n - 1), scale=Params.line_brightness) for i in range(n)]

    # Create a line with color gradient
    line = Line(
        key=key,
        points=[[x, z, -y] for x, y, z in traj_positions],
        **kwargs,
    )

    q_xyzw = [[q[1], q[2], q[3], q[0]] for q in traj_quat]  # Convert to xyzw format
    z_up_rot = R.from_euler("x", -np.pi / 2)
    traj_quat = [(z_up_rot * R.from_quat([q[0], q[1], q[2], q[3]])).as_euler("xyz", degrees=False) for q in q_xyzw]

    # Create arrows at each (sampled) point
    # arrows = [
    #     Arrow(
    #         name=f"{key}_arrow_{i}",
    #         position=[traj_positions[i][0], traj_positions[i][2], -traj_positions[i][1]],
    #         quaternion=traj_quat[i],
    #         scale=arrow_scale,
    #         color=color,
    #     )
    #     for i in range(0, n, step)
    # ]

    # Add to the scene
    proxy.upsert @ line
    # proxy.upsert @ arrows[0]
    # for arrow in arrows:
    #     proxy.upsert @ arrow


if __name__ == "__main__":
    Params.dataset_prefix = [
        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_1/",
        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_2/",
        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_3/",
        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_4/",
        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_5/",
    ]

    Params.name = "ball_sorting_toy_new"
    Params.entry_file = "ball_sorting_toy_new.mjcf.xml"
    Params.factory_fn = "vuer_mujoco.tasks.ball_sorting_toy_new:make_schema"
    # Params.init_fn = "vuer_mujoco.tasks.pick_place:BlockRandom"
    Params.env_name = "BallSortingToyNew-ball_random-v1"
    Params.seed = 0
    UnrollEval.image_keys = ["left/rgb", "wrist/rgb", "right/rgb"]
    visualize()

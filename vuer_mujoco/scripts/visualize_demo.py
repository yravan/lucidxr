from asyncio import sleep
from glob import glob
from os.path import join
from time import perf_counter
from typing import List

from params_proto import ParamsProto, Flag, Proto
from termcolor import colored

from vuer_mujoco.scripts.util.color_palette import interpolate
from vuer_mujoco.scripts.util.working_directory_context_manager import WorkDir

NEON_WHEEL = [
    (77, 238, 234),  # 4deeea
    (116, 238, 21),  # 74ee15
    (255, 231, 0),  # ffe700
    (240, 0, 255),  # f000ff
    (0, 30, 255),  # 001eff
]


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

    demo_prefix: str = "lucidxr/lucidxr/datasets/lucidxr/rss-demos/{name}"

    # asset_prefix: str = Proto("http://localhost:{vuer_port}/static", env="ASSET_PREFIX")
    asset_prefix: str = Proto(env="https://$USER-vuer-port.ngrok.app/static")
    asset_paths: List[str] = None

    src: str = "{asset_prefix}/{entry_file}"
    visible_groups: List[int] = Proto([0, 1, 2], help="Visible groups", dtype=parse_num_list)
    invisible_groups: List[int] = Proto([], help="Invisible groups", dtype=parse_num_list)
    show_lights: bool = Flag("Show lights, default to false to speed up rendering.")

    # visualization parameters
    line_width = 1.0
    line_brightness = 0.05

    verbose = Flag(help="Print out the assets that are being loaded.")

    def __post_init__(self):
        for k, v in self.__dict__.items():
            if isinstance(v, str):
                value = v.format(**self.__dict__)
                setattr(self, k, value)

                if self.verbose:
                    print(f"{colored(k, 'cyan')}:\t{colored(value, 'yellow')}")


def main(**deps):
    from params_proto import ARGS
    from vuer.events import ClientEvent
    from vuer.schemas import Line, MuJoCo, HandActuator
    from vuer import Vuer, VuerSession

    from ml_logger import ML_Logger

    ARGS.parse_args()

    Params._update(deps)
    Vuer._update(deps)

    args = Params()

    # Vuer setup with CORS configuration
    vuer = Vuer(static_root=args.wd, port=args.vuer_port)

    print(vars(args))

    loader = ML_Logger(prefix=args.demo_prefix)

    metric_files = loader.glob("**/ep_*.pkl")
    metric_files = sorted(metric_files)

    from pandas import DataFrame
    from tqdm import tqdm

    metrics = {}
    for k in tqdm(metric_files, desc="Loading metrics"):
        metrics[k] = DataFrame(loader.load_pkl(k)[0])

    # df = metrics["2025/01/31/02.37.11/ep_00001.pkl"]
    # ctrls = df[['ctrl']].dropna()
    # import matplotlib.pyplot as plt
    # plt.title("Control")
    # plt.plot(ctrl.values)
    # ctrl.values.min()
    # len(ctrl.values)
    # plt.show()

    asset_folder = join(args.wd, args.assets)

    with WorkDir(asset_folder):
        assets = glob("**/*.*", recursive=True)
        args.asset_paths = [join(args.asset_prefix, args.assets, asset) for asset in assets]
        print(f"Found {len(assets)} assets in {asset_folder}")

    if args.verbose:
        print("Assets:")
        print(*assets, sep="\n")
        print("----------------------------------")
        print("Asset Paths:")
        print(*args.asset_paths, sep="\n")

    is_loaded = False

    @vuer.add_handler("ON_CONTRIB_LOAD")
    async def on_contrib_load(event: ClientEvent, proxy: VuerSession):
        nonlocal is_loaded

        is_loaded = True
        print("ON_CONTRIB_LOAD event", event.value)

    @vuer.add_handler("ON_MUJOCO_FRAME")
    async def on_mujoco_frame(event: ClientEvent, proxy: VuerSession):
        # pprint(event.value)
        pass

    with WorkDir(Params.wd):

        @vuer.spawn(start=True)
        async def main(proxy: VuerSession):
            nonlocal is_loaded

            is_loaded = False

            t0 = perf_counter() + 5.0

            while not is_loaded and perf_counter() < t0:
                print("\rwaiting for module load...")
                await sleep(1.0)
            if not is_loaded:
                print("timed out after five seconds. Trying to load.")

            print("now insert MuJoCo component.")

            proxy.upsert @ MuJoCo(
                HandActuator(key="pinch-on-squeeze", offset=0.10, scale=-2500, low=1, high=255),
                key="default-sim",
                src=args.src,
                assets=args.asset_paths,
                frameKeys="mocap_pos mocap_quat qpos qvel ctrl sensordata",
                pause=True,
                # turn of light to make it run faster.
                useLights=args.show_lights,
                visible=args.visible_groups,
                invisible=args.invisible_groups,
            )
            await sleep(0.1)

            print("Found", len(metrics), "metrics")

            # Set up the scene with Fog to simulate MuJoCo's default style.
            for i, (key, df) in enumerate(metrics.items()):
                # mocap = df[["ts", "mpos", "mquat"]].dropna()
                print(key, df.keys())
                try:
                    # print("getting mocap points")
                    mocap_traj = df["mocap_pos"].dropna()
                    # print("got", len(mocap_traj), "mocap points")
                    # camera_matrix = df[["ts", "camera_matrix"]].dropna()

                    proxy.upsert @ Line(
                        key=f"traj-{key}",
                        points=[[x, z, -y] for x, y, z in mocap_traj.values[20:-20]],
                        color=interpolate(*NEON_WHEEL, x=i / len(metrics.keys()), scale=args.line_brightness),
                        lineWidth=args.line_width,
                    )
                except KeyError:
                    print("no stuff")

            while True:
                await sleep(5)


if __name__ == "__main__":
    main(
        wd="vuer_mujoco/tasks",
        name="pick_place",
        assets="assets",
        demo_prefix="/lucidxr/lucidxr/datasets/lucidxr/rss-demos/pick_place",
        show_lights=True,
        **{"Vuer.cors": "https://vuer.ai,https://ge-vuer-port.ngrok.app"},
    )

# - [x] install collect_demo.py as a cli
# - [ ] write paramsproto for setting the work dir etc
# - [ ] load an example scene (UR5)
# - [ ] ask Yajjy to make a scene with a UR5 and a table
# - [ ] add ml-logger prefix/dir structure.
# - [ ] document in the docs / Notion page.

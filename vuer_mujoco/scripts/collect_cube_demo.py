import colorsys
from asyncio import sleep
from collections import deque
from datetime import datetime
from glob import glob
from os.path import join
from typing import List
import random

from params_proto import ParamsProto, Flag, Proto
from termcolor import colored
from vuer.events import ClientEvent
from vuer.schemas import Box, span, Html, group, Line, HandActuator

from vuer_mujoco.scripts.util.working_directory_context_manager import WorkDir


def pi2_hsv(pi):
    """return '#RRGGBB' for a given angle in radians."""
    r, g, b = colorsys.hsv_to_rgb((pi % (2 * 3.14159)) / (2 * 3.14159), 1, 1)
    return [int(r * 255), int(g * 255), int(b * 255)]


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

    wd: str = "."
    vuer_port = 8012

    scene_folder: str = ""
    scene_name: str = "scene"
    scene_file: str = join("{scene_folder}", "{scene_name}.mjcf.xml")

    # asset_prefix: str = "http://localhost:{vuer_port}/static"
    asset_prefix: str = "https://adam-2.ngrok.app/static"
    assets: List[str] = None
    asset_paths: List[str] = None
    frame_keys: str = Proto("mocap_pos mocap_quat qpos qvel site_xpos site_xmat ctrl sensordata image eq_active")

    src: str = "{asset_prefix}/{scene_file}"
    src_path: str = "{wd}/{scene_file}"

    demo_prefix: str = "lucidxr/lucidxr/datasets/lucidxr/poc/demos/pnp/data/{scene_folder}/"
    init_dir: str = "lucidxr/lucidxr/datasets/lucidxr/scene_init/{scene_folder}/{scene_name}"


    verbose = Flag(help="Print out the assets that are being loaded.")

    def __post_init__(self):
        for k, v in self.__dict__.items():
            if isinstance(v, str):
                value = v.format(**self.__dict__)
                setattr(self, k, value)

                if self.verbose:
                    print(f"{colored(k, 'cyan')}:\t{colored(value, 'yellow')}")

        with WorkDir(join(self.wd, self.scene_folder)):
            self.assets = glob("**/*.*", recursive=True)
            self.asset_paths = [join(self.asset_prefix, self.scene_folder, asset) for asset in self.assets]

        if self.verbose:
            print("Assets:")
            print(*self.assets, sep="\n")
            print("Asset Paths:")
            print(*self.asset_paths, sep="\n")


def main():
    args = Params()

    from vuer import Vuer, VuerSession
    from vuer.schemas import MuJoCo
    from ml_logger import logger, ML_Logger

    vuer = Vuer(static_root=args.wd, port=args.vuer_port)

    box_state = "#23aaff"
    box_red = "#ff2323"
    box_green = "#54f963"
    time_start = datetime.now().strftime("%Y/%m/%d/%H.%M.%S")
    reset_sim = False
    sim_steps = 0
    x = 0
    y = 0
    rollout = 0

    loader = ML_Logger(prefix=args.init_dir)

    print("LOADER")
    print(loader)
    metrics = loader.read_metrics(path="metrics.pkl")
    df = metrics["metrics.pkl"]
    mpos = [*df["mocap_pos"].dropna()][0]
    mquat = [*df["mocap_quat"].dropna()][0]
    qpos = [*df["qpos"].dropna()][0]

    is_loaded = False

    mpos_history = deque(maxlen=200)
    color_ticker = 0



    @vuer.add_handler("ON_CLICK")
    async def on_click(event: ClientEvent, proxy: VuerSession):
        nonlocal box_state, box_red, reset_sim, x, y, rollout

        key = event.value["key"]
        print(f"Clicked: {key}")
        box_state = box_red
        print("State:", box_state)

        # Generate two random values for the box position x and y (y: 0 - 0.7 x: 0.2 - -0.4)
        x = round(random.uniform(0.2, 1.0), 2)
        y = round(random.uniform(0.15, 0.7), 2)
        print(f"New position: {x}, {y}")
        print(type(x), type(y))
        reset_sim = True
        rollout += 1

        if rollout > 1:
            logger.job_completed()

        logger.configure(args.demo_prefix + time_start + '/' + str(rollout))
        logger.job_started()

        await sleep(1)
        logger.remove("metrics.pkl")

        box_state = box_green
        print(logger.get_dash_url())


    @vuer.add_handler("CAMERA_MOVE")
    async def on_camera_move(event: ClientEvent, proxy: VuerSession):
        camera = event.value["camera"]

        logger.log(
            ts=event.ts,
            camera_matrix=camera["matrix"],
            flush=True,
            silent=True,
        )

    @vuer.add_handler("ON_MUJOCO_FRAME")
    async def on_mujoco_frame(event: ClientEvent, proxy: VuerSession):
        nonlocal mpos_history

        frame = event.value["keyFrame"]
        print("Frame Keys:", list(frame.keys()))
        # mpos_history.append([x, z, -y])


    with WorkDir(args.wd):

        @vuer.spawn(start=True)
        async def main(proxy: VuerSession):
            nonlocal sim_steps, reset_sim, x, y, mpos_history, color_ticker

            await sleep(10)

            # todo: add a ContribLoader to load the MuJoCo plugin.
            proxy.upsert @ MuJoCo(
                HandActuator(key="pinch-on-squeeze", high=0.01, low=1, ctrlId=-1),
                key="default-sim",
                src=args.src,
                assets=args.asset_paths,
                frameKeys=args.frame_keys,
            )
            while True:
                if mpos_history:
                    print("showing the line")
                    proxy.upsert @ Line(
                        points=[*mpos_history],
                        # note: change to 0.001 to view in VR, 1.0 to view on desktop.
                        linewidth=1.0,
                        vertexColors=[pi2_hsv((i + color_ticker) / 100) for i in range(len(mpos_history))],
                        # color="#ff0000",
                    )
                    await sleep(0.100)
                    last = mpos_history[-1]
                    mpos_history.clear()
                    mpos_history.append(last)
                    color_ticker += mpos_history.__len__()

                proxy.upsert @ group(
                    Html(
                        span(f"Rollout {rollout}"),
                        key="ctnr",
                        style={"width": 700, "fontSize": 20},
                    ),
                    Box(
                        args=[0.1, 0.1, 0.1],
                        key="demo-button",
                        material={"color": box_state},
                    ),
                    key="button-group-1",
                    position=[0, 1.5, -1],
                )
                await sleep(0.016)

                if reset_sim:
                    # qpos[14] = x
                    # qpos[15] = y
                    proxy.upsert @ MuJoCo(
                        HandActuator(key="pinch-on-squeeze", high=0.01, low=1, ctrlId=-1),
                        key="default-sim",
                        src=args.src,
                        assets=args.asset_paths,
                        qpos=qpos,
                        mocap_pos=mpos,
                        mocap_quat=mquat,
                        frameKeys=args.frame_keys,

                        # qpos=[1.54777e-05, 0.00713122, -0.0140634, 0.00517243, -0.000797466, 0.00116947, 0.00260148, 0.000146546, 0.00284469, -0.00307591, 0.00260143, 0.000146418, 0.00284853, -0.00308389, x, y, 0.779778, 1, 3.94652e-17, -1.43726e-19, -6.17826e-19, -1.46173e-19, -0.5, 0.769784, 1, 3.81151e-17, -2.98284e-21, -4.23138e-22],
                        # qpos=qpos,
                        # qvel=[0] * len(qpos),
                        # mpos=[0.14, 0.818, 0.825],
                        # mpos=[-0.045, -0.135, 1.46],
                        # mquat=[1, 0, 0, 0],
                        # pause=True,
                    )
                    if sim_steps > 3:
                        reset_sim = False
                        sim_steps = 0
                    else:
                        sim_steps += 1

                await sleep(0.016)

    logger.job_completed()


if __name__ == "__main__":
    Params.wd = "/Users/yajvanravan/fortyfive/lucidxr/vuer_mujoco/"


    Params.scene_name = "pick_block"
    Params.scene_folder = "tasks"

    args = Params()

    main()
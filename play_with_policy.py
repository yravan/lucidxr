import colorsys
import os
import sys
from asyncio import sleep
from datetime import datetime
from importlib import import_module
from os.path import join
from time import perf_counter, time
from typing import List, Literal
import numpy as np

import yaml

from dotvar import auto_load  # noqa
from params_proto import ARGS, Flag, ParamsProto, Proto
from termcolor import colored

from lucidxr.learning.utils import set_seed
from vuer_mujoco.schemas.se3.rot_gs6 import mat2gs6, quat2gs6
from vuer_mujoco.scripts.util.working_directory_context_manager import WorkDir
from vuer.schemas.physics_components import MjCameraView
from scipy.spatial.transform import Rotation as R

class LEFT_CAM_POS:
    # x = 0.466
    # y = 0.46
    # height = 0.274
    x = 0.375
    y = 0.355
    height = 0.325


l = LEFT_CAM_POS()
CAM_MODULE_W = 0.034

W, H = 640, 360
# FOV = 74.5
FOV = 42.5


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


def mocap_site_alignment(*, site_xmat, mocap_quat):
    # avoid quaternion because of the sign ambiguity
    # site_quat = xmat2quat(frame["site_xmat"][-18:-9])
    site_mat = site_xmat[-18:-9]
    site_gs6 = mat2gs6(site_mat)

    # a = np.array(frame['mocap_pos'] ) - frame['site_xpos'][-6:-3]
    m_quat = mocap_quat
    m_gs6 = quat2gs6(m_quat)
    import numpy as np

    # print("----------------------", [f"{x:1.3f}" for x in site_gs6], [f"{x:1.3f}" for x in m_gs6], sep="\n", end="\n", flush=True)
    delta = np.array(site_gs6) - np.array(m_gs6)
    print("\r", [f"{x:1.3f}" for x in delta], end="\r", flush=True)


def _get_camera_rig():
    # Camera config
    left_pos = np.array([l.x + 0.065, l.y, l.height])
    left_lookat = np.array([left_pos[0], 0, 0.167914592])

    # Forward (z), right (x), up (y) axes
    forward = left_lookat - left_pos
    forward /= np.linalg.norm(forward)

    # Up vector assumption (world up is z+)
    world_up = np.array([0, 0, 1])

    # Compute right and true up vectors
    right = np.cross(world_up, forward)
    right /= np.linalg.norm(right)

    up = np.cross(forward, right)

    # Rotation matrix: columns are [right, up, forward]
    rot_mat = np.column_stack((right, up, forward))

    # Convert to Euler angles (XYZ order)
    rot = R.from_matrix(rot_mat)
    euler = rot.as_euler("xyz", degrees=True)

    return MjCameraView(
        key="left_rig_cam",
        fov=FOV,
        width=W,
        height=H,
        position=left_pos.tolist(),
        rotation=euler.tolist(),
        fps=30,
        near=0.1,
        far=20,
        movable=False,
        showCameraFrustum=True,
    )

def main():
    # need to do local import to avoid the schema parsing side effect.

    # need to manually parse because the cli_parse is set to False.
    ARGS.parse_args()

    args = Params()

    from ml_logger import logger
    from vuer import Vuer, VuerSession
    from vuer.events import ClientEvent
    from vuer.schemas import Box, HandActuator, Html, MuJoCo, Octahedron, Sphere, group, span

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

    box_state = "#23aaff"

    demo_counter = 0
    frame_stack = []

    async def handle_reset(log_trajectory: bool, button_key: str, proxy: VuerSession):
        nonlocal demo_counter, frame_stack, box_state

        import yaml

        # For the reset button, log the trajectory.
        if log_trajectory:
            demo_counter += 1
            logger.save_pkl(frame_stack[args.clip_head:], f"frames/ep_{demo_counter:05d}.pkl")

        from vuer_mujoco.schemas.utils.file import Read

        config = Read(args.name + ".frame.yaml")
        keyframes = yaml.load(config, Loader=yaml.FullLoader)
        if keyframes:
            args.init_keyframe = {k: np.array(v) for k, v in keyframes[-1].items() if k in ["qpos", "qvel", "mocap_pos", "mocap_quat", "ctrl"]}
            if args.init_fn:
                set_seed(int(time() * 1e6) % (2**32))
                module_name, task_name = args.init_fn.rsplit(":", 1)
                m = import_module(module_name)
                task_class = getattr(m, task_name)
                args.init_keyframe = task_class.random_state(**args.init_keyframe)

        proxy.upsert @ _get_mujoco_model(mode=args.actuators, visible=args.visible_groups, show_lights=args.show_lights)

        box_state = "#FFA500"
        await sleep(args.reset_time + 0.1)
        box_state = "#54f963"

        frame_stack = []

    @vuer.add_handler("ON_CLICK")
    async def on_click(event: ClientEvent, proxy: VuerSession):
        nonlocal frame_stack, demo_counter

        key = event.value["key"]
        if key == "reset-button":
            await handle_reset(log_trajectory=True, button_key=key, proxy=proxy)
        elif key == "delete-button":
            await handle_reset(log_trajectory=False, button_key=key, proxy=proxy)
        elif key == "record-button":
            from vuer_mujoco.schemas.utils.file import Save

            yaml.dump([last_frame], default_flow_style=False) | Save(args.name + ".frame.yaml", append=True)
            print("Saved init at", os.getcwd(), os.listdir())

        print(f"Clicked: {key} N: {demo_counter}")

    @vuer.add_handler("CAMERA_MOVE")
    async def on_mujoco_frame(event: ClientEvent, proxy: VuerSession):
        camera = event.value["camera"]
        if event.key != "ego":
            return
        mat = camera["matrix"]
        print("camera moved", mat)
        if len(frame_stack):
            frame_stack[-1]["camera_matrix"] = mat

    last_frame = None
    frame_stack = []

    @vuer.add_handler("ON_MUJOCO_LOAD")
    async def on_load(event: ClientEvent, proxy: VuerSession):
        frame = event.value["keyFrame"]
        print("ON_MUJOCO_LOAD event")

    @vuer.add_handler("ON_MUJOCO_FRAME")
    async def on_frame(event: ClientEvent, proxy: VuerSession):
        nonlocal frame_stack, last_frame

        last_frame = frame = event.value["keyFrame"]
        frame_stack.append(frame)

        # print("this is working")

        if Params.verbose:
            mocap_site_alignment(**frame)

        # print("action:", [f"{x:1.3f}" for x in frame["ctrl"]], flush=True)
        return

    with WorkDir(args.wd):

        @vuer.spawn(start=True)
        async def main(proxy: VuerSession):
            nonlocal IS_LOADED, box_state

            IS_LOADED = False

            t0 = perf_counter() + 5.0

            # # done: add a ContribLoader to load the MuJoCo plugin.
            # proxy.upsert @ ContribLoader(
            #     key="contrib-loader-mujoco",
            #     library="@vuer-ai/mujoco-ts",
            #     version="0.0.51",
            #     main="dist/index.umd.js",
            #     dependencies=["VUER", "LEVA", "FIBER"],
            # )

            while not IS_LOADED and perf_counter() < t0:
                print("\rwaiting for module load...")
                await sleep(1.0)
            if not IS_LOADED:
                print("timed out after five seconds. Trying to load.")

            print("now insert MuJoCo component.")

            proxy.upsert @ _get_mujoco_model(mode=args.actuators, visible=args.visible_groups, show_lights=args.show_lights)

            proxy.upsert @ _get_camera_rig()
            await sleep(1.0)

            _box_state = None

            while True:
                if _box_state and _box_state == box_state:
                    await sleep(0.016)
                    continue

                _box_state = box_state
                await sleep(0.016)

                proxy.upsert @ group(
                    Html(
                        span("reset pose"),
                        key="reset-label",
                        style={"top": 30, "width": 700, "fontSize": 20},
                    ),
                    Box(
                        args=[0.25, 0.25, 0.25],
                        key="reset-button",
                        material={"color": box_state},
                    ),
                    key="reset-button",
                    position=[-0.4, 1.4, -1],
                )  # type: ignore

                proxy.upsert @ group(
                    Html(
                        span("delete traj"),
                        key="delete-label",
                        style={"top": 30, "width": 150, "fontSize": 20},
                    ),
                    Octahedron(
                        args=[0.15, 0],
                        key="delete-button",
                        material={"color": box_state},
                    ),
                    key="delete-button",
                    position=[0, 1.4, -1],
                )  # type: ignore
                proxy.upsert @ group(
                    Html(
                        span("record initial pose"),
                        key="record-label",
                        style={"top": 30, "width": 150, "fontSize": 20},
                    ),
                    Sphere(
                        args=[0.1, 32, 16],
                        key="record-button",
                        material={"color": "red"},
                    ),
                    key="record-button",
                    position=[0.4, 1.4, -1],
                )  # type: ignore
                proxy.upsert @ group(
                    Html(
                        span(f"Trajectory: {demo_counter}"),
                        key="traj-label",
                        style={"top": 30, "width": 150, "fontSize": 20},
                    ),
                    key="traj-label",
                    position=[-0.1, 1.9, -1],
                )  # type: ignore

                await sleep(0.016)

    logger.job_completed()


if __name__ == "__main__":
    from vuer import Vuer
    from killport import kill_ports

    kill_ports(ports=[8012])

    Params.wd = "../tasks"
    Params.show_lights = False
    Params.assets = "assets"

    # Params.name = "mug_tree"
    # Params.entry_file = "mug_tree.mjcf.xml"
    # Params.factory_fn = "vuer_mujoco.tasks.mug_tree:make_schema"
    # Params.init_fn = "vuer_mujoco.tasks.mug_tree:MugRandom"

    # Params.name = "push_t"
    # Params.entry_file = "push_t.mjcf.xml"
    # Params.factory_fn = "vuer_mujoco.tasks.push_t:make_schema"

    #
    # Params.name = "mug_tree_ur"
    # Params.entry_file = "mug_tree_ur.mjcf.xml"
    # Params.factory_fn = "vuer_mujoco.tasks.mug_tree_ur:make_schema"
    # Params.init_fn = "vuer_mujoco.tasks.mug_tree:Fixed"
    #

    Params.name = "kitchen_room"
    Params.entry_file = "kitchen_room.mjcf.xml"
    Params.factory_fn = "vuer_mujoco.tasks.kitchen_room:make_schema"
    Params.init_fn = "vuer_mujoco.tasks.kitchen_room:CleanSink"


    # Params.name = "tie_knot"
    # Params.entry_file = "tie_knot.mjcf.xml"
    # # Params.factory_fn = "vuer_mujoco.tasks.tie_knot:make_schema"
    # Params.init_fn = "vuer_mujoco.tasks.tie_knot:RopeRandom"

    # Params.name = "pick_place"
    # Params.entry_file = "pick_place.mjcf.xml"
    # Params.factory_fn = "vuer_mujoco.tasks.pick_place:make_schema"
    # Params.init_fn = "vuer_mujoco.tasks.pick_place:BlockRandom"

    # Params.name = "ball_sorting_toy"
    # Params.entry_file = "ball_sorting_toy.mjcf.xml"
    # Params.factory_fn = "vuer_mujoco.tasks.ball_sorting_toy:make_schema"
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

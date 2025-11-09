from asyncio import sleep
from glob import glob
from os.path import join
from pathlib import Path
from typing import List

from params_proto import ParamsProto, Flag
from termcolor import colored
from vuer.events import ClientEvent
from vuer.schemas import CoordsMarker, Group, Html, span, CatmullRomLine, Line

from vuer_mujoco.scripts.util.working_directory_context_manager import WorkDir


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
    demo_prefix: str = "lucidxr/lucidxr/datasets/lucidxr/poc/demos/ability/2025/01/09/19.49.00/"

    wd: str = "."
    vuer_port = 8012

    scene_folder: str = ''
    scene_name: str = "scene"
    scene_file: str = join("{scene_folder}", "{scene_name}.mjcf.xml")

    asset_prefix: str = "http://localhost:{vuer_port}/static"
    assets: List[str] = None
    asset_paths: List[str] = None

    src: str = "{asset_prefix}/{scene_file}"
    src_path: str = "{wd}/{scene_file}"

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
    from ml_logger import ML_Logger
    args = Params()

    from vuer import Vuer, VuerSession
    from vuer.schemas import MuJoCo

    vuer = Vuer(static_root=args.wd, port=args.vuer_port)

    loader = ML_Logger(prefix=args.demo_prefix)

    df = loader.read_metrics()["metrics.pkl"]

    mocap = df[["ts", "mpos", "mquat"]].dropna()
    mocap_traj = df["mpos"].dropna()
    camera_matrix = df[["ts", "camera_matrix"]].dropna()

    @vuer.add_handler("ON_MUJOCO_FRAME")
    async def on_mujoco_frame(event: ClientEvent, proxy: VuerSession):
        # pprint(event.value)
        pass

    with WorkDir(args.wd):

        @vuer.spawn(start=True)
        async def main(proxy: VuerSession):
            frame_stack = camera_matrix.to_dict(orient="records")
            if (args.verbose): print(f"frame_stake contains {len(frame_stack)} frames.")
            for i, frame in [*enumerate(frame_stack)][::10]:
                ts = frame["ts"]
                mat = frame["camera_matrix"]
                proxy.upsert @ Group(
                    CoordsMarker(key=f"coord.ts-{ts}", scale=0.1),
                    Html(span(f"#{i}", style={"width": 100})),
                    key=f"ts-{ts}",
                    matrix=[*mat],
                )
                await sleep(0.016)

            # # todo: add a ContribLoader to load the MuJoCo plugin.
            # proxy.upsert @ MuJoCo(key="default-sim", src=args.src, assets=asset_paths)
            if (args.verbose): print([*mocap_traj.values])
            proxy.upsert @ Line(
                key="traj",
                points=[[x, z, -y] for x, y, z in mocap_traj.values],
            )

            while True:
                for frame in mocap.to_dict(orient="records"):
                    ts = frame["ts"]
                    mpos = frame["mpos"]
                    mquat = frame["mquat"]
                    if (args.verbose): print("mpos", mpos, end="\r", flush=True)

                    proxy.upsert @ MuJoCo(
                        key="default-sim",
                        src=args.src,
                        assets=args.asset_paths,
                        qpos = [0,0,0,0,0,0,0,
                                0,0,0,0,0,0,0,
                                0,0,1,0,0,0,0,]
                    )

                    await sleep(0.016)


if __name__ == "__main__":
    from ml_logger import ML_Logger

    Params.demo_prefix = "/lucidxr/lucidxr/datasets/lucidxr/poc/demos/ability/2025/01/13/20.53.03/"
    Params.wd = "/Users/yajvanravan/fortyfive/lucidxr/assets/development/robots"
    Params.scene_name = "scene"
    Params.scene_folder = "universal_robots_ur5e"

    args = Params()

    main()

# - [x] install collect_demo.py as a cli
# - [ ] write paramsproto for setting the work dir etc
# - [ ] load an example scene (UR5)
# - [ ] ask Yajjy to make a scene with a UR5 and a table
# - [ ] add ml-logger prefix/dir structure.
# - [ ] document in the docs / Notion page.

import os
from asyncio import sleep

from vuer import Vuer, VuerSession
from vuer.schemas import MuJoCo, Scene, Sphere, AmbientLight, Hands, \
    HandActuator  # , MotionControllers, MotionControllerActuator


app = Vuer(static_root="../assets")
asset_pref = "http://localhost:8012/static/trossen_vx300s/" # SET ASSET PATH
assets_folder = "../assets/trossen_vx300s/assets/" # SET ASSET PATH


# Function to dynamically list all asset files in the folder
def get_asset_files(folder_path):
    return [asset_pref + f"assets/{f}" for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]


@app.spawn(start=True)
async def main(sess: VuerSession):
    # Setup the scene with Fog to simulate MuJoCo's default style.
    sess.set @ Scene(
        bgChildren=[
            AmbientLight(),
            Hands(),
            # MotionControllers(),
            Sphere(
                args=[50, 10, 10],
                materialType="basic",
                material=dict(color=0x2c3f57, side=1),
            ),
        ],
    )
    await sleep(0.0005)

    # Load asset files dynamically
    asset_files = get_asset_files(assets_folder)

    # Add any include files not in asset folder into asset files path, eg. (asset_files += [asset_pref + "vx300s.xml"])
    asset_files += [asset_pref + "vx300s.xml"]


    sess.upsert @ MuJoCo(
        HandActuator(key="pinch-on-squeeze", high=0.06, low=0.001, ctrlId=-1), # Adjust actuator's range here,
        # MotionControllerActuator(high=0.06, low=0.001, ctrlId=-1),
        key="kitchen-1",
        src=asset_pref + "scene.xml", # CHANGE SCENE NAME
        assets=asset_files,
        useLights=True,
    )

    await sleep(1000.0)

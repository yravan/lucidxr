import os

import numpy as np
from cmx import CommonMark
from params_proto import ParamsProto, Proto

from vuer_mujoco.tasks import make

CWD = os.getcwd()


class Args(ParamsProto, prefix="dg"):
    """
    Use the lxr prefix to avoid conflict with other parameters.
    """

    wd = Proto(CWD, help="automatically switch to this directory")
    env_name = "MugTree-v1"
    image_keys = "front/rgb,right/rgb,wrist/rgb"
    visualize_k_inits: int = Proto(0, help="visualize random placement by averaging top-down view", dtype=int)


def scene_spec():
    from pprint import pprint

    args = Args()

    print("changing directory to: ", args.wd, "and running:", end="")
    os.chdir(args.wd)
    pprint(vars(args))

    doc = CommonMark(args.env_name + ".md", root=os.getcwd(), prefix=".")

    doc @ f"""
    # Render {args.env_name}

    """

    # Create the figures directory if it doesn't exist
    figures_dir = f"figures/{args.env_name}"
    os.makedirs(figures_dir, exist_ok=True)

    with doc @ f"create and initialize the environment: `{args.env_name}`":
        env = make(args.env_name)
        env.reset()

        prev_act = env.get_prev_action()
        obs, *_ = env.step(prev_act)

    with doc, doc.table() as table:
        with table.figure_row() as row:
            for i, img_key in enumerate(args.image_keys.split(",")):
                img = obs[img_key]
                print("data type is", img.dtype)

                fname = f"{figures_dir}/{img_key}.png?ts={doc.now()}"
                row.figure(img, src=fname, title=img_key, caption="this is the details")

    doc.flush()

    raw_env = env.unwrapped.env
    if not raw_env.task.pose_buffer:
        exit()

    doc @ """
    ### Visualizing Random Placement
    
    visualize random placement by aggregating top-down views:
    """

    with doc:
        # Collect 10 images after resets
        images = []
        first_key = "top/rgb"

        # stop the loop
        while raw_env.task.pose_buffer:
            obs = env.reset()
            images.append(obs[first_key].astype(np.float32))

        # Average the images
        max_img = np.max(images, axis=0).astype(np.uint8)
        min_img = np.min(images, axis=0).astype(np.uint8)

    # Save averaged image
    fname_max = f"{figures_dir}/maxmix_{first_key}.png?ts={doc.now()}"
    fname_min = f"{figures_dir}/minmix_{first_key}.png?ts={doc.now()}"

    caption = f"{first_key}"
    with doc, doc.table() as table:
        with table.figure_row() as row:
            row.figure(max_img, src=fname_max, title=f"Max Mixed{first_key}", caption=caption)
            row.figure(min_img, src=fname_min, title=f"Min Mixed {first_key}", caption=caption)

    doc.flush()


if __name__ == "__main__":
    from pathlib import Path

    Args.wd = Path(__file__).parent / "../tasks/__docs__"
    scene_spec()

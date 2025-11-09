import os

import jaynes
from jaynes import Jaynes
from dotvar import auto_load  # noqa

from lucidxr.traj_samplers.process_steps.render_worker import mujoco_render_entrypoint
import time


def keep_retrying(fn):
    """Decorator to keep retrying a function until it succeeds."""

    def wrapper(*args, **kwargs):
        while True:
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                print(f"Error: {e}. Retrying...")
                time.sleep(1.0)

    return wrapper


config = dict(
    name="utensil_drawer",
    env_name="UtensilDrawer-Random-lucid-v1",
    camera_keys=[
        # "front_r/lucid/midas_depth_full",
        # "front_r/lucid",
        "wrist/lucid/midas_depth_full",
        "wrist/lucid",
        # "front/lucid/midas_depth_full",
        # "front/lucid",
    ],
    lucid_mode=True,
    workflow_arg_keys={
        "image_0": "cup",
        "image_1": "spoon",
        "image_2": "midas_depth",
    },
    workflow_cls="weaver.workflows.lucidxr_2_object_mask_workflow:Imagen",
    prompt_jsonl_file="utensil_drawer.jsonl",
    # env_name="UtensilDrawer-Random-v1",
    # camera_keys=["front/rgb", "front_r/rgb", "wrist/rgb"],
    dry_run=False,
    overwrite=False,
    playback_policy=True,
)


demo_prefixes = [
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/utensil_drawer/2025/08/28/18.48.03/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/utensil_drawer/2025/08/28/18.48.03_0/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/utensil_drawer/2025/08/28/18.48.03_1/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/utensil_drawer/2025/08/28/18.48.03_2/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/utensil_drawer/2025/08/28/18.48.03_3/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/utensil_drawer/2025/08/28/18.48.03_4/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/utensil_drawer/2025/08/28/18.48.03_5/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/utensil_drawer/2025/08/28/18.48.03_6/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/utensil_drawer/2025/08/28/18.48.03_7/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/utensil_drawer/2025/08/28/18.48.03_8/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/utensil_drawer/2025/08/28/18.48.03_9/",
]

demo_ep_start = 1
demo_ep_end = 102

num_render_workers = 200
render_worker_chain_length = 8

def main():

    from zaku import TaskQ

    mujoco_queue_name = f"{os.environ.get('ZAKU_USER')}:lucidxr:mujoco-queue-2"
    weaver_queue_name = f"{os.environ.get('ZAKU_USER')}:lucidxr:weaver-queue-1"
    mujoco_queue = TaskQ(name=mujoco_queue_name)
    weaver_queue = TaskQ(name=weaver_queue_name)
    # mujoco_queue.clear_queue()
    # weaver_queue.clear_queue()

    for demo_prefix in demo_prefixes:
        for i in range(demo_ep_start, demo_ep_end + 1):
            mujoco_queue.add(
                dict(
                    ep_ind=i,
                    demo_prefix=demo_prefix,
                    **config,
                )
            )
    print(len(demo_prefixes) * (demo_ep_end - demo_ep_start + 1))
    print(f"{mujoco_queue.count()} jobs added to {mujoco_queue_name} queue.")
    print(f"{weaver_queue.count()} jobs in {weaver_queue_name} queue.")
    exit()

    Jaynes.runner_config = None
    for i in range(1, num_render_workers + 1, render_worker_chain_length):
        jaynes.config(mode="render", runner=dict(name=f"render_worker-{i}"),)
                      # config_path="../../../../../.jaynes_fortyfive.yml")

        job = jaynes.add(
            keep_retrying(mujoco_render_entrypoint),
            queue_name=mujoco_queue_name,
        )

        for j in range(1, render_worker_chain_length):
            if i + j <= num_render_workers:
                job = job.chain(
                    keep_retrying(mujoco_render_entrypoint),
                    queue_name=mujoco_queue_name,
                )

    jaynes.execute()
    jaynes.listen()

if __name__ == "__main__":
    main()

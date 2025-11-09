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
    name="ball_sorting_toy_new",
    env_name="BallSortingToyNew-fixed-lucid-v1",
    camera_keys=["left/lucid", "right/lucid", "wrist/lucid", "left/lucid/midas_depth_full", "right/lucid/midas_depth_full", "wrist/lucid/midas_depth_full"],
    # lucid_mode=True,
    workflow_arg_keys={
        "image_0": "cylinder-blue",
        "image_1": "cylinder-orange",
        "image_2": "midas_depth",
        "image_3": "ball-sorter-toy",
    },
    workflow_cls="weaver.workflows.lucidxr_3_mask_workflow:Imagen",
    prompt_jsonl_file="ball_sorting_toy.jsonl",
    # env_name = "BallSortingToyNew-ball_random-v1",
    # camera_keys = ["left/rgb", "right/rgb", "wrist/rgb"],
    dry_run=True,
    overwrite=True,
    playback_policy=True,
    num_objects=3,
)


demo_prefixes = [
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_1/"
]

demo_ep_start = 1
demo_ep_end = 88

num_render_workers = 29
render_worker_chain_length = 6

def main():

    from zaku import TaskQ

    mujoco_queue_name = f"{os.environ.get('ZAKU_USER')}:lucidxr:mujoco-queue-1"
    mujoco_queue = TaskQ(name=mujoco_queue_name)
    mujoco_queue.clear_queue()

    for demo_prefix in demo_prefixes:
        for i in range(demo_ep_start, demo_ep_end + 1):
            mujoco_queue.add(
                dict(
                    ep_ind=i,
                    demo_prefix=demo_prefix,
                    **config,
                )
            )
        # exit()
    print(len(demo_prefixes) * (demo_ep_end - demo_ep_start + 1))
    print(f"{mujoco_queue.count()} jobs added to {mujoco_queue_name} queue.")

    Jaynes.runner_config = None
    for i in range(1, num_render_workers + 1, render_worker_chain_length):
        jaynes.config(mode="render", runner=dict(name=f"render_worker-{i}"))

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

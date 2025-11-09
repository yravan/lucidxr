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
    name="mug_tree",
    env_name="MugTree-mug_rand-v1",
    camera_keys=["right/rgb", "left/rgb", "wrist/rgb"],
    overwrite=False,
    playback_policy=True,
    num_objects=2,
)


demo_prefixes = ["/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/24/14.30.11_1",
                 "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/24/14.30.11_2",
                 "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/24/14.30.11_3",
                 "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/24/14.30.11_4",
                 "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/24/14.30.11_5",]

demo_ep_start = 1
demo_ep_end = 50

num_render_workers = 50
render_worker_chain_length = 6

def main():

    from zaku import TaskQ

    mujoco_queue_name = f"{os.environ.get('ZAKU_USER')}:lucidxr:mujoco-queue-2"
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
    print(len(demo_prefixes) * (demo_ep_end - demo_ep_start + 1))
    print(f"{mujoco_queue.count()} jobs added to {mujoco_queue_name} queue.")

    Jaynes.runner_config = None
    for i in range(1, num_render_workers + 1, render_worker_chain_length):
        jaynes.config(mode="render", runner=dict(name=f"render_worker-{i}"),)
                      # config_path=f"../../../../../.jaynes_fortyfive.yml")

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

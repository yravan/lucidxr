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
    name="tie_knot",
    env_name="TieKnot-rope_random-v1",
    camera_keys=["left/rgb", "right/rgb", "wrist/rgb"],
    overwrite=False,
    dry_run=False,
    lucid_mode=False,
)

demo_prefix = "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/tie_knot/2025/08/19/22.06.11/"
demo_ep_start = 1
demo_ep_end = 100

num_render_workers = 40
render_worker_chain_length = 6


def main():
    from zaku import TaskQ

    mujoco_queue_name = f"{os.environ.get('ZAKU_USER')}:lucidxr:mujoco-queue-2"
    # mujoco_queue = TaskQ(name=mujoco_queue_name)
    # # mujoco_queue.clear_queue()
    #
    # for i in range(demo_ep_start, demo_ep_end + 1):
    #     mujoco_queue.add(
    #         dict(
    #             ep_ind=i,
    #             demo_prefix=demo_prefix.format(**config),
    #             **config,
    #         )
    #     )
    #     # exit()
    # print(f"{mujoco_queue.count()} jobs added to {mujoco_queue_name} queue.")

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

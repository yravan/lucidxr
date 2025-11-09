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


mujoco_queue_name = f"{os.environ.get('ZAKU_USER')}:lucidxr:mujoco-queue-3"
generative_queue_name = f"{os.environ.get('ZAKU_USER')}:lucidxr:generative-queue-3"
weaver_queue_name = f"{os.environ.get('ZAKU_USER')}:lucidxr:weaver-queue-3"

config = dict(
    name="tie_knot",
    env_name="TieKnot-lucid-v1",
    camera_keys=["left/lucid", "right/lucid", "wrist/lucid"],
    generative_workflow_arg_keys={
        "image_0": None,
        "image_1": "rope",
        "image_2": "midas_depth",
        "strength_3": 0.9,
        "strength_1": 10,
    },
    generative_workflow_cls="weaver.workflows.lucidxr_2_object_mask_workflow:Imagen",
    prompt_jsonl_file="tie_knot.jsonl",
    dry_run=False,
    overwrite=False,
    lucid_mode=True,
    generative_queue_name= generative_queue_name,
    weaver_queue_name = weaver_queue_name
)

demo_prefix = "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/tie_knot/2025/06/30/13.35.46/"
demo_ep_start = 1
demo_ep_end = 20

num_render_workers = 18
render_worker_chain_length = 6
num_generative_workers = 24
generative_worker_chain_length = 8

def main():

    from zaku import TaskQ

    mujoco_queue = TaskQ(name=mujoco_queue_name)
    # mujoco_queue.clear_queue()

    for i in range(demo_ep_start, demo_ep_end + 1):
        mujoco_queue.add(
            dict(
                ep_ind=i,
                demo_prefix=demo_prefix.format(**config),
                **config,
            )
        )
        # exit()
    print(f"{mujoco_queue.count()} jobs added to {mujoco_queue_name} queue.")

    # jaynes.config(mode="local")
    Jaynes.runner_config = None
    for i in range(1, num_render_workers + 1, render_worker_chain_length):
        jaynes.config(mode="render", runner=dict(name=f"render_worker-{i}"), config_path="/Users/yajvanravan/fortyfive/lucidxr/.jaynes.yml")

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

    from lucidxr.traj_samplers.process_steps.generative_worker import entrypoint
    Jaynes.runner_config = None
    for i in range(0, num_generative_workers, generative_worker_chain_length):
        jaynes.config(mode="render", runner=dict(name=f"generative_worker-{i}"), config_path="/Users/yajvanravan/fortyfive/lucidxr/.jaynes.yml")

        job = jaynes.add(
            keep_retrying(entrypoint),
            **config,
        )

        for _ in range(1, generative_worker_chain_length):
            if i * generative_worker_chain_length + _ < num_generative_workers:
                job = job.chain(
                    keep_retrying(entrypoint),
                    **config,
                )

    jaynes.execute()
    jaynes.listen()

if __name__ == "__main__":
    main()

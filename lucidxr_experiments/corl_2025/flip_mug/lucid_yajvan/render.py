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


mujoco_queue_name = f"{os.environ.get('ZAKU_USER')}:lucidxr:mujoco-queue-1"
num_generative_queues = 6
generative_queue_names = [f"{os.environ.get('ZAKU_USER')}:lucidxr:generative-queue-{i}" for i in range(7, 7 + num_generative_queues)]
print(f"Using {num_generative_queues} generative queues: {generative_queue_names}")
weaver_queue_name = f"{os.environ.get('ZAKU_USER')}:lucidxr:weaver-queue-1"

master_config = dict(
    name="flip_mug",
    env_name="FlipMug-random-lucid-v1",
    camera_keys=[
        "wrist/lucid",
        "right/lucid",
        "back/lucid",
        "wrist/lucid/midas_depth_full",
        "right/lucid/midas_depth_full",
        "back/lucid/midas_depth_full",
    ],
    generative_workflow_arg_keys={
        "image_0": None,
        "image_1": "mug",
        "image_2": "midas_depth",
    },
    generative_workflow_cls="weaver.workflows.lucidxr_2_object_mask_workflow:Imagen",
    prompt_jsonl_file="mug_tree.jsonl",
    dry_run=False,
    overwrite=True,
    lucid_mode=True,
    weaver_queue_name = weaver_queue_name
)
def get_config(i):
    config = master_config.copy()
    config["generative_queue_name"] = generative_queue_names[i % num_generative_queues]
    return config


demo_prefix = "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/flip_mug/2025/07/02/00.25.57/"
demo_ep_start = 1
demo_ep_end = 63

num_render_workers = 63
render_worker_chain_length = 6
num_generative_workers = 80
generative_worker_chain_length = 8

def main():

    from zaku import TaskQ

    for generative_queue_name in generative_queue_names:
        generative_queue = TaskQ(name=generative_queue_name)
        # generative_queue.clear_queue()
    print("cleared generative queues.")

    mujoco_queue = TaskQ(name=mujoco_queue_name)
    # mujoco_queue.clear_queue()
    print("cleared mujoco queue.")

    # for i in range(demo_ep_start, demo_ep_end + 1):
    #     mujoco_queue.add(
    #         dict(
    #             ep_ind=i,
    #             demo_prefix=demo_prefix.format(**master_config),
    #             **get_config(i),
    #         )
    #     )
    #     # exit()
    # print(f"{mujoco_queue.count()} jobs added to {mujoco_queue_name} queue.")

    # Jaynes.runner_config = None
    # for i in range(1, num_render_workers + 1, render_worker_chain_length):
    #     jaynes.config(mode="render", runner=dict(name=f"render_worker-{i}"))
    #
    #     job = jaynes.add(
    #         keep_retrying(mujoco_render_entrypoint),
    #         queue_name=mujoco_queue_name,
    #     )
    #
    #     for j in range(1, render_worker_chain_length):
    #         if i + j <= num_render_workers:
    #             job = job.chain(
    #                 keep_retrying(mujoco_render_entrypoint),
    #                 queue_name=mujoco_queue_name,
    #             )

    from lucidxr.traj_samplers.process_steps.generative_worker import entrypoint
    Jaynes.runner_config = None
    for i in range(0, num_generative_workers, generative_worker_chain_length):
        jaynes.config(mode="generative_worker", runner=dict(name=f"generative_worker-{i}"))

        job = jaynes.add(
            keep_retrying(entrypoint),
            **get_config(i * generative_worker_chain_length),
        )

        for _ in range(1, generative_worker_chain_length):
            if i + _ <= num_generative_workers:
                job = job.chain(
                    keep_retrying(entrypoint),
                    **get_config(i * generative_worker_chain_length + _),
                )

    jaynes.execute()
    jaynes.listen()

if __name__ == "__main__":
    main()

from dotvar import auto_load  # noqa

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
    name="mug_tree_ur",
    env_name="MugTreeUr-fixed-lucid-v1",
    generative_image_keys=["right", "wrist", "left"],
    generative_workflow_arg_keys={
        "image_0": "tree",
        "image_1": "mug",
        "image_2": "midas_depth",
    },
    generative_workflow_cls="weaver.workflows.lucidxr_2_object_mask_workflow:Imagen",
    prompt_jsonl_file="mug_tree.jsonl",
)

demo_prefix = "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree_ur/2025/07/01/12.23.54"
demo_ep_start = 1
demo_ep_end = 1

num_render_workers = 1
render_worker_chain_length = 1
overwrite = True

from zaku import TaskQ

mujoco_queue_name = "alanyu:lucidxr:mujoco-queue-1"
mujoco_queue = TaskQ(name=mujoco_queue_name)
# mujoco_queue.clear_queue()

for i in range(demo_ep_start, demo_ep_end + 1):
    mujoco_queue.add(
        dict(
            ep_ind=i,
            demo_prefix=demo_prefix.format(**config),
            **config,
            overwrite=overwrite,
            lucid_mode=True,
            dry_run=False,
        )
    )
print(f"{mujoco_queue.count()} jobs added to {mujoco_queue_name} queue.")

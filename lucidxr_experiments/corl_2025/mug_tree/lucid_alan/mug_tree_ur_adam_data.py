import jaynes
from jaynes import Jaynes
from dotvar import auto_load  # noqa

from lucidxr.traj_samplers.process_steps.render_worker import render_worker, mujoco_render_entrypoint
from lucidxr.traj_samplers.process_steps.generative_worker import entrypoint
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

demo_prefix = "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree_ur/2025/06/17/15.53.21/"
demo_ep_start = 1
demo_ep_end = 35

num_render_workers = 35
render_worker_chain_length = 6

num_generative_workers = 70
generative_worker_chain_length = 15
overwrite = False

from zaku import TaskQ
mujoco_queue_name = "alanyu:lucidxr:mujoco-queue-1"
mujoco_queue = TaskQ(name=mujoco_queue_name)
# mujoco_queue.clear_queue()

for i in range(demo_ep_start, demo_ep_end+1):
    mujoco_queue.add(
        dict(
            ep_ind=i,
            demo_prefix=demo_prefix.format(**config),
            camera_keys=[],
            **config,
            overwrite=overwrite,
            lucid_mode=True,
            dry_run=False,
        )
    )
print(f"{mujoco_queue.count()} jobs added to {mujoco_queue_name} queue.")
# exit()
Jaynes.runner_config = None
for i in range(1, num_render_workers+1, render_worker_chain_length):
    jaynes.config(mode="render_worker", runner=dict(name=f"render_worker-{i}"))

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

Jaynes.runner_config = None
for i in range(0, num_generative_workers, generative_worker_chain_length):
    jaynes.config(mode="generative_worker", runner=dict(name=f"generative_worker-{i}"))

    job = jaynes.add(
        keep_retrying(entrypoint),
        dry_run=False,
        overwrite=overwrite,
        demo_prefix=demo_prefix.format(**config),
        **config,
    )

    for _ in range(1, generative_worker_chain_length):
        if i + _ <= num_generative_workers:
            job = job.chain(
                keep_retrying(entrypoint),
                dry_run=False,
                overwrite=overwrite,
                demo_prefix=demo_prefix.format(**config),
                **config,
            )
jaynes.execute()
jaynes.listen()






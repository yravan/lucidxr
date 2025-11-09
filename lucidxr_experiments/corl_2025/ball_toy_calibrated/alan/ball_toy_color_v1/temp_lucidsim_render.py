import jaynes
from jaynes import Jaynes
from dotvar import auto_load  # noqa

from lucidxr.traj_samplers.process_steps.render_worker import mujoco_render_entrypoint
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


master_config = dict(
    name="ball_sorting_toy_calibrated",
    env_name="BallSortingToyCalibrated-color_random-lucid-v1",
    camera_keys=[
        "wrist/lucid",
        "right/lucid",
        "left/lucid",
        "wrist/lucid/midas_depth_full",
        "right/lucid/midas_depth_full",
        "left/lucid/midas_depth_full",
    ],
    generative_workflow_arg_keys={
        "image_0": None,
        "image_1": None,
        "image_2": "midas_depth",
    },
    generative_workflow_cls="weaver.workflows.lucidxr_2_object_mask_workflow:Imagen",
    prompt_jsonl_file="mug_tree.jsonl",  # reuse the background prompts from mug tree.
    # generative_queue_name=generative_queue_name,
)


def get_config(i):
    config = master_config.copy()
    config["generative_queue_name"] = generative_queue_names[i % num_generative_queues]
    return config


demo_prefix = "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_calibrated/2025/07/01/23.59.36/"
demo_ep_start = 1
demo_ep_end = 54

num_render_workers = 55
render_worker_chain_length = 7

num_generative_workers = 40
generative_worker_chain_length = 6
overwrite = False

num_generative_queues = 4
generative_queue_names = [f"alanyu:lucidxr:generative-queue-{i}" for i in range(num_generative_queues)]
print(f"Using {num_generative_queues} generative queues: {generative_queue_names}")

# from zaku import TaskQ
# 
# for generative_queue_name in generative_queue_names:
#     generative_queue = TaskQ(name=generative_queue_name)
#     generative_queue.clear_queue()
# print("cleared generative queues.")
# 
# mujoco_queue_name = "alanyu:lucidxr:mujoco-queue-1"
# mujoco_queue = TaskQ(name=mujoco_queue_name)
# mujoco_queue.clear_queue()
# 
# for i in range(demo_ep_start, demo_ep_end + 1):
#     if i in [51, 7]:
#         continue
#     mujoco_queue.add(
#         dict(
#             ep_ind=i,
#             demo_prefix=demo_prefix.format(**get_config(i)),
#             **get_config(i),
#             overwrite=overwrite,
#             lucid_mode=True,
#             dry_run=False,
#         )
#     )
    # exit()
# print(f"{mujoco_queue.count()} jobs added to {mujoco_queue_name} queue.")
# exit()
# Jaynes.runner_config = None
# for i in range(1, num_render_workers + 1, render_worker_chain_length):
#     jaynes.config(mode="render_worker", runner=dict(name=f"render_worker-{i}"))
# 
#     job = jaynes.add(
#         keep_retrying(mujoco_render_entrypoint),
#         queue_name=mujoco_queue_name,
#         # generative_queue_name=generative_queue_name,
#     )
# 
#     for j in range(1, render_worker_chain_length):
#         if i + j <= num_render_workers:
#             job = job.chain(
#                 keep_retrying(mujoco_render_entrypoint),
#                 queue_name=mujoco_queue_name,
#                 # generative_queue_name=generative_queue_name,
#             )

Jaynes.runner_config = None
for i in range(0, num_generative_workers, generative_worker_chain_length):
    # jaynes.config(mode="generative_worker", runner=dict(name=f"generative_worker-{i}"))
    jaynes.config(mode="local")

    job = jaynes.run(
        keep_retrying(entrypoint),
        dry_run=False,
        overwrite=overwrite,
        demo_prefix=demo_prefix.format(**get_config(i)),
        **get_config(3),
        weaver_queue_name="yravan:lucidxr:weaver-queue-1",
        verbose=True,  # Use a different queue for rendering
    )
    # jaynes.listen()

    for _ in range(1, generative_worker_chain_length):
        if i + _ <= num_generative_workers:
            job = job.chain(
                keep_retrying(entrypoint),
                dry_run=False,
                overwrite=overwrite,
                demo_prefix=demo_prefix.format(**get_config(i)),
                **get_config(i),
                weaver_queue_name="yravan:lucidxr:weaver-queue-1",  # Use a different queue for rendering
            )
jaynes.execute()
jaynes.listen()

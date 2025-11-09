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
    name="robosuite_stack",
    env_name="RobosuiteStack-random-v1",
    camera_keys=["front/rgb", "right/rgb", "wrist/rgb", "right_r/rgb"],
)

demo_prefix = "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/robosuite_stack/2025/06/18/18.16.48/"
demo_ep_start = 5
demo_ep_end = 116

ignore = []

new_ids = [1, 3, 5, 6, 7, 8, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 25, 26, 27, 28, 29, 30, 35, 36, 37, 38, 40, 47, 50, 52, 54, 55, 56, 57, 58, 60, 65, 67,  69, 70, 71, 72, 78, 82, 87, 88, 89, 90, 93, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 109, 113, 114]
ep_ids = [i for i in new_ids if i not in ignore]

num_render_workers = 30
render_worker_chain_length = 6
overwrite = True

from zaku import TaskQ
mujoco_queue_name = "kmcclenn:lucidxr:mujoco-queue-1"
mujoco_queue = TaskQ(name=mujoco_queue_name, uri="http://escher.csail.mit.edu:8100", verbose=True)
# print("created queue")
print(mujoco_queue.count())
# # # mujoco_queue.clear_queue()
# # # print(mujoco_queue.count())
# print("cleared queue")
# for i in new_ids:
#     print(i)
#     mujoco_queue.add(
#         dict(
#             ep_ind=i,
#             demo_prefix=demo_prefix.format(**config),
#             **config,
#             overwrite=overwrite,
#             lucid_mode=False,
#             dry_run=False,
#         )
#     )
#
# print(f"{mujoco_queue.count()} jobs added to {mujoco_queue_name} queue.")
# exit()
Jaynes.runner_config = None
for i in range(1, num_render_workers + 1, render_worker_chain_length):
    jaynes.config(mode="default", runner=dict(name=f"render_worker-{i}"))

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





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
#
# import os
# os.environ["MUJOCO_GL"] = "osmesa"
#
#
#


config = dict(
    name="flip_mug",
    env_name="FlipMug-random-v1",
    camera_keys=["back/rgb", "wrist/rgb", "right/rgb"],
)

demo_prefix = "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/flip_mug/2025/07/02/00.25.57/"
demo_ep_start = 1
demo_ep_end = 63

ignore = []


new_ids = list(range(demo_ep_start, demo_ep_end + 1))
ep_ids = [i for i in new_ids if i not in ignore]

num_render_workers = 60
render_worker_chain_length = 6
overwrite = True

from zaku import TaskQ
mujoco_queue_name = "kmcclenn:lucidxr:flip:mujoco-queue-2"
mujoco_queue = TaskQ(name=mujoco_queue_name, uri="http://escher.csail.mit.edu:8100", verbose=True)
print("created queue")

print(mujoco_queue.count())
try:
    mujoco_queue.clear_queue()
    print("cleared queue")
except:
    pass
# print(mujoco_queue.count())

for i in ep_ids:
    print(i)
    mujoco_queue.add(
        dict(
            ep_ind=i,
            demo_prefix=demo_prefix.format(**config),
            **config,
            overwrite=overwrite,
            lucid_mode=False,
            dry_run=False,
        )
    )

print(f"{mujoco_queue.count()} jobs added to {mujoco_queue_name} queue.")
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





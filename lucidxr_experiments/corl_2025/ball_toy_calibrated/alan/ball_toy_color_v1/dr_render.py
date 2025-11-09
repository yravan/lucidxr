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
    name="ball_sorting_toy_calibrated",
    env_name="BallSortingToyCalibrated-color_random-dr-v1",
    camera_keys=["wrist/domain_rand", "left/domain_rand", "right/domain_rand"],
)

demo_prefix = "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_calibrated/2025/07/01/23.59.36/"
demo_ep_start = 1
demo_ep_end = 54

num_render_workers = 54
render_worker_chain_length = 6
overwrite = True

from zaku import TaskQ

mujoco_queue_name = "alanyu:lucidxr:mujoco-dr-queue-1"
mujoco_queue = TaskQ(name=mujoco_queue_name)
# mujoco_queue.clear_queue()

for i in range(demo_ep_start, demo_ep_end + 1):
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
    # exit()
print(f"{mujoco_queue.count()} jobs added to {mujoco_queue_name} queue.")
# exit()
Jaynes.runner_config = None
for i in range(1, num_render_workers + 1, render_worker_chain_length):
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

jaynes.execute()
jaynes.listen()

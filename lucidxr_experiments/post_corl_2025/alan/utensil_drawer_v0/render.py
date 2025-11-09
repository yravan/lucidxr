import jaynes
from jaynes import Jaynes
from dotvar import auto_load  # noqa
from zaku import TaskQ

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
    name="utensil_drawer",
    env_name="UtensilDrawer-Random-v1",
    camera_keys=["front/rgb", "front_r/rgb", "wrist/rgb"],
    start_frame=0,
    end_frame=None,
)

demo_prefix = "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/utensil_drawer/2025/08/28/18.48.03/"
demo_ep_start = 1
demo_ep_end = 102

num_render_workers = 40
render_worker_chain_length = 5
overwrite = True

#
mujoco_queue_name = "alanyu:lucidxr:mujoco-queue-1"
mujoco_queue = TaskQ(name=mujoco_queue_name)
print(mujoco_queue.count())
# mujoco_queue.clear_queue()
while mujoco_queue.count() > 0:
    with mujoco_queue.pop() as job:
        if job is not None:
            print('popped')
            continue
        print('none')
    

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

Jaynes.runner_config = None
for i in range(1, num_render_workers + 1, render_worker_chain_length):
    # jaynes.config(mode="mujoco_eval", runner=dict(name=f"render_worker-{i}"), config_path="/Users/alanyu/fortyfive/lucidxr/.jaynes_fortyfive.yml")
    jaynes.config(
        mode="render",
        runner=dict(name=f"render_worker-{i}"),
        verbose=True,
    )

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

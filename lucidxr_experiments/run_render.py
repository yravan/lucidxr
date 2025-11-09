from params_proto.hyper import Sweep
from zaku import TaskQ
import jaynes
from tqdm import tqdm


def launch_workers():
    from lucidxr.traj_samplers.process_steps.render_worker import mujoco_render_entrypoint

    num_jobs = 6
    worker_chain_length = 4
    for wid in range(num_jobs):
        jaynes.config(
            mode="mujoco_eval",
            runner=dict(name=f"render-worker-{wid}"),
            config_path="/Users/yajvanravan/fortyfive/lucidxr/.jaynes_fortyfive.yml",
        )
        job = jaynes.add(
            mujoco_render_entrypoint,
            queue_name="alanyu:lucidxr:mujoco-queue-1",
        )
        for _ in range(worker_chain_length - 1):
            job = job.chain(
                mujoco_render_entrypoint,
                queue_name="alanyu:lucidxr:mujoco-queue-1",
            )

    jaynes.execute()
    jaynes.listen()


if __name__ == "__main__":
    launch_workers()

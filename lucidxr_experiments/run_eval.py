import os
from pathlib import Path

from dotvar import auto_load

from params_proto.hyper import Sweep
from zaku import TaskQ
import jaynes
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).parent.parent
def add_jobs(filename, **deps):
    jobs = Sweep.read(filename)

    eval_queue_name = f"{os.environ.get('ZAKU_USER')}:lucidxr:eval-queue-9-27"
    eval_queue = TaskQ(name=eval_queue_name)
    # eval_queue.clear_queue()
    print(eval_queue.count())
    # exit()
    deps["UnrollEval.num_evals"] = len(jobs)
    for i, job in enumerate(tqdm(jobs)):
        job.update(deps)
        eval_queue.add(job)
    print(f"Added {len(jobs)} jobs to the queue: {eval_queue_name}")


def launch_workers(num_jobs=10, worker_chain_length=8):

    from lucidxr.learning.eval_node import entrypoint
    for wid in range(num_jobs):
        jaynes.config(
            mode="eval",
            runner=dict(name=f"eval-worker-{wid}"),
            config_path=f"{PROJECT_ROOT}/.jaynes.yml",
            # config_path=f"{PROJECT_ROOT}/.jaynes_fortyfive.yml",
        )
        # jaynes.config(mode="local")
        job = jaynes.add(
            entrypoint,
        )
        for _ in range(worker_chain_length - 1):
            job = job.chain(
                entrypoint,
            )

    jaynes.execute()
    jaynes.listen()

if __name__ == "__main__":

    eval_queue_name = f"{os.environ.get('ZAKU_USER')}:lucidxr:eval-queue-9-27"
    eval_queue = TaskQ(name=eval_queue_name)
    eval_queue.clear_queue()

    deps = {
        "UnrollEval.load_from_cache": True,
        "UnrollEval.results_file": f"eval_340000.pkl",
        "UnrollEval.train_step": 340000,
        "UnrollEval.load_checkpoint": "/lucidxr/lucidxr/post_corl_2025/yajvan/9-20-25/pour_liquid_mujoco_dunet/learn/2025/09/20/17-17-06/unet/all-three/100/checkpoints/policy_latest_ema.pt",
        "RUN.prefix": "/lucidxr/lucidxr/post_corl_2025/yajvan/9-20-25/pour_liquid_mujoco_dunet/learn/2025/09/20/17-17-06/unet/all-three/100",
        "UnrollEval.policy": "diffusion",

        # "DiffusionPolicyArgs.chunk_size": 48,
        # "DiffusionPolicyArgs.channels": [64, 128, 256, 512],
        # "DiffusionPolicyArgs.image_keys": ['wrist/rgb'],
        # "DiffusionPolicyArgs.vis_dim": 512,
        # "DiffusionPolicyArgs.action_len": 24,
        # "DiffusionPolicyArgs.embed_dim": 512,
        # "DiffusionPolicyArgs.backbone": "cnn",
    }
    add_jobs("post_corl_2025/yajvan/9-20-25/pour_liquid_mujoco_dunet/learn_eval.jsonl", **deps)
    # eval_queue_name = f"{os.environ.get('ZAKU_USER')}:lucidxr:eval-queue-9-17"
    # eval_queue = TaskQ(name=eval_queue_name)
    # eval_queue.clear_queue()

    # launch_workers(10, 8)

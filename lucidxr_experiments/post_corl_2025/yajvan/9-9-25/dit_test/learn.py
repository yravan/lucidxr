from pathlib import Path

from params_proto.hyper import Sweep

from lucidxr_experiments import RUN
from diffusion.train_policy_conditional import Args as TrainArgs
from diffusion.models.policy import DiffusionPolicyArgs
from lucidxr.learning.unroll_eval import UnrollEval as Unroll

# Differences with Alan's code
# Different vision backbone resnet vs regular cnn -> changed this in policy.py
# mixed-precision inference -> just got rid of this
# ema on unroll -> changed this in training loop
# different hyperparams -> made it be the same


with Sweep(RUN, TrainArgs, DiffusionPolicyArgs) as sweep:
    TrainArgs.dataset_host = "/home/ravan/datasets/escher_snapshot"

    TrainArgs.prune_cache = False

    TrainArgs.eval_arg_file = f"{Path(*Path(__file__).parts[-6:-1])}/{Path(__file__).stem}_eval.jsonl"

    DiffusionPolicyArgs.chunk_size = 24
    DiffusionPolicyArgs.action_len = 12

    TrainArgs.weight_decay = 1e-4
    TrainArgs.lr_start = 1e-4

    TrainArgs.n_steps = 100000
    TrainArgs.step_checkpoint_interval = 5000
    DiffusionPolicyArgs.score_net = 'causal_transformer'
    with sweep.product:
        TrainArgs.seed = [100]
        with sweep.zip:
            DiffusionPolicyArgs.backbone = ["cnn"]
            DiffusionPolicyArgs.vis_dim = [512]
        TrainArgs.dataset_prefix = [
            [
                "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/24/14.30.11_1/",
                # "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/24/14.30.11_2/",
                # "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/24/14.30.11_3/",
                # "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/24/14.30.11_4/",
                # "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/24/14.30.11_5/",
            ],
        ]
        DiffusionPolicyArgs.image_keys = [
            ["wrist/rgb"],
        ]
        TrainArgs.batch_size = [64]


from datetime import datetime

time = datetime.now()

checkpoints = {}


@sweep.each
def tail(RUN, TrainArgs, DiffusionPolicyArgs):
    RUN.prefix, RUN.job_name, _ = RUN(
        script_path=__file__, job_name=f"{time:%Y/%m/%d/%H-%M-%S}/use_aux_loss-{TrainArgs.use_aux_loss}/{'all-three' if len(DiffusionPolicyArgs.image_keys) > 1 else 'wrist-only'}/aug_camera_randomization-{TrainArgs.aug_camera_randomization}/{TrainArgs.seed}"
    )
    checkpoints[RUN.prefix + "/checkpoints/policy_last.pt"] = f"chunksize-{DiffusionPolicyArgs.chunk_size}/{TrainArgs.seed}"


sweep.save(Path(__file__).stem + ".jsonl")
print(checkpoints)
print("Num checkpoints:", len(checkpoints))

with Sweep(RUN, Unroll, TrainArgs) as sweep:
    Unroll.checkpoint_host = "http://escher.csail.mit.edu:4000"

    Unroll.log_metrics = True
    Unroll.max_steps = 500
    # important
    Unroll.load_from_cache = False
    Unroll.overwrite = True
    Unroll.action_smoothing = True

    with sweep.product:
        with sweep.zip:
            Unroll.env_name = [
                "MugTree-mug_rand-v1",
            ]
            Unroll.image_keys = [
                ["right/rgb", "wrist/rgb", "left/rgb"],
            ]

        with sweep.zip:
            Unroll.seed = [*range(10)]
            Unroll.render = [True for _ in range(5)] + [False for _ in range(5)]  # only render 10% of the runs


@sweep.each
def tail(RUN, Unroll, TrainArgs):
    RUN.prefix, RUN.job_name, _ = RUN(
        script_path=__file__,
    )
    print(RUN.prefix)


from ml_logger.job import RUN, instr  # noqa

RUN.job_name = "{now:%Y/%m-%d}"
RUN.prefix = "lucidxr/lucidxr/{file_stem}/{job_name}"
# this sets the root for calculating the prefix
RUN.script_root = Path(__file__).parent
sweep.save(f"{Path(__file__).stem}_eval.jsonl")

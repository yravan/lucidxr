from pathlib import Path

from params_proto.hyper import Sweep

from lucidxr_experiments import RUN
from diffusion.train_policy_conditional import Args as TrainArgs
from diffusion.models.policy import DiffusionPolicyArgs
from lucidxr.learning.unroll_eval import UnrollEval as Unroll


with Sweep(RUN, TrainArgs, DiffusionPolicyArgs) as sweep:
    TrainArgs.dataset_host = "/home/ravan/datasets/escher_snapshot"

    TrainArgs.prune_cache = False

    TrainArgs.eval_arg_file = f"{Path(*Path(__file__).parts[-6:-1])}/{Path(__file__).stem}_eval.jsonl"

    DiffusionPolicyArgs.chunk_size = 24
    DiffusionPolicyArgs.action_len = 12
    TrainArgs.debug = False
    TrainArgs.n_steps = 300000
    TrainArgs.step_checkpoint_interval = 20000

    with sweep.product:
        with sweep.zip:
            DiffusionPolicyArgs.backbone = ["cnn", 'resnet']
            DiffusionPolicyArgs.vis_dim = [512, 1024]
        TrainArgs.dataset_prefix = [
            [
                "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/tie_knot/2025/08/19/22.06.11/",
            ],
        ]
        with sweep.zip:
            DiffusionPolicyArgs.image_keys = [
                ["wrist/rgb"],
                ["right/rgb", "wrist/rgb", "left/rgb"],
            ]
            TrainArgs.batch_size = [64, 20]

        DiffusionPolicyArgs.embed_dim = [128]


from datetime import datetime

time = datetime.now()

checkpoints = {}


@sweep.each
def tail(RUN, TrainArgs, DiffusionPolicyArgs):
    RUN.prefix, RUN.job_name, _ = RUN(
        script_path=__file__,
        job_name=f"{time:%Y/%m/%d/%H-%M-%S}/{'wrist-only' if len(DiffusionPolicyArgs.image_keys) == 1 else 'all-three'}/{DiffusionPolicyArgs.backbone}"
    )
    checkpoints[RUN.prefix + "/checkpoints/policy_last.pt"] = f"chunksize-{DiffusionPolicyArgs.chunk_size}/{TrainArgs.seed}"


sweep.save(Path(__file__).stem + ".jsonl")
print(checkpoints)
print("Num checkpoints:", len(checkpoints))

with Sweep(RUN, Unroll, TrainArgs) as sweep:
    Unroll.checkpoint_host = "http://escher.csail.mit.edu:4000"

    Unroll.log_metrics = True
    Unroll.max_steps = 700
    # important
    Unroll.load_from_cache = False
    Unroll.overwrite = True
    Unroll.action_smoothing = True

    with sweep.product:
        with sweep.zip:
            Unroll.env_name = [
                "TieKnot-rope_random-v1",
            ]
            Unroll.image_keys = [
                ["right/rgb", "wrist/rgb", "left/rgb"],
            ]

        with sweep.zip:
            Unroll.seed = [*range(20)]
            Unroll.render = [True for _ in range(10)] + [False for _ in range(10)]  # only render 10% of the runs


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

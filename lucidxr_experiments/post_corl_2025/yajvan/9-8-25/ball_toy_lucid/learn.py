from pathlib import Path

from params_proto.hyper import Sweep

from lucidxr_experiments import RUN
from diffusion.train_policy_conditional import Args as TrainArgs
from diffusion.models.policy import DiffusionPolicyArgs
from lucidxr.learning.unroll_eval import UnrollEval as Unroll

demo_prefixes = [
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_1/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_2/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_3/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_4/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_5/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_6/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_7/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_8/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_9/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_10/",
]

with Sweep(RUN, TrainArgs, DiffusionPolicyArgs) as sweep:
    TrainArgs.dataset_host = "/home/ravan/datasets/escher_snapshot"

    TrainArgs.prune_cache = True

    TrainArgs.eval_arg_file = f"{Path(*Path(__file__).parts[-6:-1])}/{Path(__file__).stem}_eval.jsonl"


    TrainArgs.aug_camera_randomization = True
    TrainArgs.p_cam_rand = 1.0
    TrainArgs.randomize_wrist = True
    TrainArgs.n_steps = 1000000
    TrainArgs.step_checkpoint_interval = 50000
    with sweep.product:
        with sweep.zip:
            DiffusionPolicyArgs.chunk_size = [24]
            DiffusionPolicyArgs.action_len = [12]
        TrainArgs.seed = [100]
        with sweep.zip:
            DiffusionPolicyArgs.backbone = ["cnn", "resnet"]
            DiffusionPolicyArgs.vis_dim = [512, 1024]
        TrainArgs.dataset_prefix = [
            demo_prefixes[:1],
            demo_prefixes[:5],
            demo_prefixes,
        ]
        with sweep.zip:
            DiffusionPolicyArgs.image_keys = [
                ["wrist/lucid"],
                # ["right/lucid", "wrist/lucid", "left/lucid"],
            ]
            TrainArgs.batch_size = [64]

        DiffusionPolicyArgs.embed_dim = [512]

from datetime import datetime

time = datetime.now()

checkpoints = {}


@sweep.each
def tail(RUN, TrainArgs, DiffusionPolicyArgs):
    RUN.prefix, RUN.job_name, _ = RUN(
        script_path=__file__,
        job_name=f"{time:%Y/%m/%d/%H-%M-%S}/datasets-{len(TrainArgs.dataset_prefix)}/backbone-{DiffusionPolicyArgs.backbone}/{TrainArgs.seed}"
    )
    checkpoints[
        RUN.prefix + "/checkpoints/policy_last.pt"] = f"chunksize-{DiffusionPolicyArgs.chunk_size}/{TrainArgs.seed}"


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
                "BallSortingToyNew-ball_random-v1",
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

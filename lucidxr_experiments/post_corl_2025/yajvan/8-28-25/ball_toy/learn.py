from pathlib import Path

from params_proto.hyper import Sweep

from lucidxr_experiments import RUN
from diffusion.train_policy_conditional import Args as TrainArgs
from diffusion.models.policy import DiffusionPolicyArgs
from lucidxr.learning.unroll_eval import UnrollEval as Unroll


with Sweep(RUN, TrainArgs, DiffusionPolicyArgs) as sweep:
    TrainArgs.dataset_host = "/home/ravan/datasets/escher_snapshot"

    TrainArgs.prune_cache = True

    TrainArgs.eval_arg_file = f"{Path(*Path(__file__).parts[-6:-1])}/{Path(__file__).stem}_eval.jsonl"

    TrainArgs.chunk_size = 24
    TrainArgs.debug = False
    TrainArgs.vis_dim = 1024

    TrainArgs.aug_camera_randomization = True
    TrainArgs.p_cam_rand = 1.0
    TrainArgs.randomize_wrist = True
    TrainArgs.n_steps = 50000
    TrainArgs.step_checkpoint_interval = 10000
    with sweep.zip:
        with sweep.product:
            with sweep.zip:
                TrainArgs.dataset_prefix = [
                    [
                        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_1/",
                    ],
                    [
                        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_1/",
                    ],
                    [
                        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_1/",
                    ],
                    [
                        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/pick_place_real/2025/08/25/17.02.44/",
                    ],
                    [
                        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/pick_place_real/2025/08/25/17.02.44/",
                    ],
                    [
                        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/pick_place_real/2025/08/25/17.02.44/",
                    ],
                ]
                TrainArgs.data_fractions = [
                    [1.0] ,
                    [0.666] ,
                    [0.333] ,
                    [1.0] ,
                    [0.666] ,
                    [0.333] ,
                ]
                TrainArgs.image_keys = [
                    ["wrist/lucid"],
                    ["wrist/lucid"],
                    ["wrist/lucid"],
                    ["wrist/rgb"],
                    ["wrist/rgb"],
                    ["wrist/rgb"],
                ]

            TrainArgs.embed_dim = [128]
            TrainArgs.batch_size = [64]


from datetime import datetime

time = datetime.now()

checkpoints = {}


@sweep.each
def tail(RUN, TrainArgs, DiffusionPolicyArgs):
    RUN.prefix, RUN.job_name, _ = RUN(
        script_path=__file__,
        job_name=f"{time:%Y/%m/%d/%H-%M-%S}/data_fraction-{TrainArgs.data_fractions[0]}/{'lucid-xr-aug' if len(TrainArgs.data_fractions) > 3 else ('lucid-xr' if 'real' not in TrainArgs.dataset_prefix[0] else 'real')}",
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

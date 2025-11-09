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
    TrainArgs.n_steps = 100000
    TrainArgs.step_checkpoint_interval = 10000
    with sweep.zip:
        TrainArgs.load_checkpoint=[
            "/lucidxr/lucidxr/post_corl_2025/yajvan/8-28-25/mug_tree_data_test/learn/2025/08/28/14-58-03/data_fraction-1.0/lucid-xr/checkpoints/latest.pth",
            "/lucidxr/lucidxr/post_corl_2025/yajvan/8-28-25/mug_tree_data_test/learn/2025/08/28/14-58-03/data_fraction-0.666/lucid-xr/checkpoints/latest.pth",
            "/lucidxr/lucidxr/post_corl_2025/yajvan/8-28-25/mug_tree_data_test/learn/2025/08/28/14-58-03/data_fraction-0.333/lucid-xr/checkpoints/latest.pth",
            "/lucidxr/lucidxr/post_corl_2025/yajvan/8-28-25/mug_tree_data_test/learn/2025/08/28/14-58-03/data_fraction-1.0/real/checkpoints/latest.pth",
            "/lucidxr/lucidxr/post_corl_2025/yajvan/8-28-25/mug_tree_data_test/learn/2025/08/28/14-58-03/data_fraction-0.666/real/checkpoints/latest.pth",
            "/lucidxr/lucidxr/post_corl_2025/yajvan/8-28-25/mug_tree_data_test/learn/2025/08/28/14-58-03/data_fraction-0.333/real/checkpoints/latest.pth",
        ]
        with sweep.product:
            with sweep.zip:
                TrainArgs.dataset_prefix = [
                    [
                        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/25/11.43.11/",
                        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/28/11.20.15/",
                    ],
                    [
                        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/25/11.43.11/",
                        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/28/11.20.15/",
                    ],
                    [
                        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/25/11.43.11/",
                        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/28/11.20.15/",
                    ],
                    [
                        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree_real/2025/08/27/19.25.25/",
                        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree_real/2025/08/27/19.43.42",
                        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree_real/2025/08/27/20.03.16",
                    ],
                    [
                        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree_real/2025/08/27/19.25.25/",
                        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree_real/2025/08/27/19.43.42",
                        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree_real/2025/08/27/20.03.16",
                    ],
                    [
                        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree_real/2025/08/27/19.25.25/",
                        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree_real/2025/08/27/19.43.42",
                        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree_real/2025/08/27/20.03.16",
                    ],
                ]
                TrainArgs.data_fractions = [
                    [1.0] * 2,
                    [0.666] * 2,
                    [0.333] * 2,
                    [1.0] * 3,
                    [0.666] * 3,
                    [0.333] * 3,
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
    Unroll.max_steps = 500
    # important
    Unroll.load_from_cache = False
    Unroll.overwrite = True
    Unroll.action_smoothing = True

    with sweep.product:
        with sweep.zip:
            Unroll.env_name = ["MugTree-mug_rand-gsplat-v1",
                               "MugTree-mug_rand-v1",
                               "MugTree-mug_rand-gsplat-v2",
                               "MugTree-ur-mug_rand-v1"]
            Unroll.image_keys = [["right/splat_rgb", "wrist/splat_rgb", "left/splat_rgb"],
                                    ["right/rgb", "wrist/rgb", "left/rgb"],
                                    ["right/splat_rgb", "wrist/splat_rgb", "left/splat_rgb"],
                                    ["right/rgb", "wrist/rgb", "left/rgb"]]

        with sweep.zip:
            Unroll.seed = [*range(10)]
            Unroll.render = [True for _ in range(10)] + [False for _ in range(0)]  # only render 10% of the runs


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

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


demo_prefixes = [
    ["/lucidxr/lucidxr/datasets/lucidxr/corl-2025/utensil_drawer/2025/08/28/18.48.03/"], # Utensil Drawer
    ["/lucidxr/lucidxr/datasets/lucidxr/corl-2025/microwave_muffin/2025/08/28/20.23.43"], # Microwave Muffin
    ["/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/24/14.30.11_1/",
     "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/24/14.30.11_2/",
     "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/24/14.30.11_3/",
     "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/24/14.30.11_4/",
     "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/24/14.30.11_5/",], # Mug Tree
    ["/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_1/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_2/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_3/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_4/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_5/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_6/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_7/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_8/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_9/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_10/"], # Ball Toy
    ["/lucidxr/lucidxr/datasets/lucidxr/corl-2025/pour_liquid/2025/08/22/13.44.21"],# Pour Liquid
    ["/lucidxr/lucidxr/datasets/lucidxr/corl-2025/tie_knot/2025/08/19/22.06.11/"], # Knot Tying
    ["/lucidxr/lucidxr/datasets/lucidxr/corl-2025/pick_place_robot_room/2025/08/07/15.58.28"], # Pick Place
]
steps = [
    200000,
    200000,
    200000,
    500000,
    300000,
    200000,
    200000,
]


with Sweep(RUN, TrainArgs, DiffusionPolicyArgs) as sweep:
    TrainArgs.dataset_host = "/home/ravan/datasets/escher_snapshot"

    TrainArgs.prune_cache = False
    DiffusionPolicyArgs.obs_dim =146
    DiffusionPolicyArgs.action_dim =146

    TrainArgs.eval_arg_file = f"{Path(*Path(__file__).parts[-6:-1])}/{Path(__file__).stem}_eval.jsonl"

    DiffusionPolicyArgs.chunk_size = 24
    DiffusionPolicyArgs.action_len = 12


    TrainArgs.dataset_prefix = demo_prefixes[4]
    TrainArgs.n_steps = steps[4]
    TrainArgs.step_checkpoint_interval = TrainArgs.n_steps//5
    TrainArgs.eval_ema = True

    TrainArgs.weight_decay = 1e-4
    TrainArgs.lr_start = 2e-4
    TrainArgs.lr_end = 1e-5

    DiffusionPolicyArgs.score_net = 'unet'
    DiffusionPolicyArgs.backbone = "cnn"
    DiffusionPolicyArgs.vis_dim = 512
    DiffusionPolicyArgs.channels = [1024, 2048, 4096, 8192]
    DiffusionPolicyArgs.kernel_size = 5
    with sweep.product:
        TrainArgs.seed = [100, 200, 300]
        DiffusionPolicyArgs.image_keys = [
            ["back/rgb", "top/rgb", "right/rgb"],
        ]
        TrainArgs.batch_size = [24]


from datetime import datetime

time = datetime.now()

checkpoints = {}


@sweep.each
def tail(RUN, TrainArgs, DiffusionPolicyArgs):
    RUN.prefix, RUN.job_name, _ = RUN(
        script_path=__file__, job_name=f"{time:%Y/%m/%d/%H-%M-%S}/{DiffusionPolicyArgs.score_net}/{'all-three' if len(DiffusionPolicyArgs.image_keys)==3 else 'wrist-only'}/{TrainArgs.seed}"
    )
    checkpoints[RUN.prefix + "/checkpoints/policy_last.pt"] = f"chunksize-{DiffusionPolicyArgs.chunk_size}/{TrainArgs.seed}"


sweep.save(Path(__file__).stem + ".jsonl")
print(checkpoints)
print("Num checkpoints:", len(checkpoints))

with Sweep(RUN, Unroll, TrainArgs) as sweep:
    Unroll.checkpoint_host = "http://escher.csail.mit.edu:4000"

    Unroll.log_metrics = True
    Unroll.max_steps = 600
    # important
    Unroll.load_from_cache = False
    Unroll.overwrite = True
    Unroll.action_smoothing = True

    with sweep.product:
        with sweep.zip:
            Unroll.env_name = [
                "PourLiquid-cup_random-v1",
            ]
            Unroll.image_keys = [
                ["stereo_far_left/rgb", "stereo_far_right/rgb", "right/rgb", "back/rgb", "top/rgb"],
            ]

        with sweep.zip:
            Unroll.seed = [*range(20)]
            Unroll.render = [True for _ in range(20)] + [False for _ in range(0)]  # only render 10% of the runs


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

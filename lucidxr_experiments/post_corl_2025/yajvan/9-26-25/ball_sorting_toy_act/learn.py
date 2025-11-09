from pathlib import Path

from params_proto.hyper import Sweep

from lucidxr.learning.train import TrainArgs
from lucidxr_experiments import RUN

from lucidxr.learning.unroll_eval import UnrollEval as Unroll
from lucidxr.learning.act_config import ACT_Config



demo_prefixes = [
    ["/lucidxr/lucidxr/datasets/lucidxr/corl-2025/utensil_drawer/2025/08/28/18.48.03/",
     "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/utensil_drawer/2025/08/28/18.48.03_0/",
        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/utensil_drawer/2025/08/28/18.48.03_1/",
        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/utensil_drawer/2025/08/28/18.48.03_2/",
        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/utensil_drawer/2025/08/28/18.48.03_3/",
        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/utensil_drawer/2025/08/28/18.48.03_4/",
        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/utensil_drawer/2025/08/28/18.48.03_5/",
        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/utensil_drawer/2025/08/28/18.48.03_6/",
        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/utensil_drawer/2025/08/28/18.48.03_7/",
        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/utensil_drawer/2025/08/28/18.48.03_8/",
        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/utensil_drawer/2025/08/28/18.48.03_9/",
        ], # Utens
    ["/lucidxr/lucidxr/datasets/lucidxr/corl-2025/microwave_muffin/2025/08/28/20.23.43",
     "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/microwave_muffin/2025/08/28/20.23.43_0",
     "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/microwave_muffin/2025/08/28/20.23.43_1",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/microwave_muffin/2025/08/28/20.23.43_2",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/microwave_muffin/2025/08/28/20.23.43_3",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/microwave_muffin/2025/08/28/20.23.43_4",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/microwave_muffin/2025/08/28/20.23.43_5",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/microwave_muffin/2025/08/28/20.23.43_6",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/microwave_muffin/2025/08/28/20.23.43_7",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/microwave_muffin/2025/08/28/20.23.43_8",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/microwave_muffin/2025/08/28/20.23.43_9",
    ], # Microwave Muffin
    ["/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/24/14.30.11_1/"], # Mug Tree
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
    300000,
    300000,
    300000,
    300000,
    300000,
    300000,
    300000,
]



with Sweep(RUN, TrainArgs, ACT_Config) as sweep:
    ACT_Config.normalize_actions = True
    ACT_Config.normalize_obs = True

    TrainArgs.dataset_host = '/home/ravan/datasets/escher_snapshot'

    TrainArgs.eval_interval = 10000
    TrainArgs.checkpoint_interval = 10000
    TrainArgs.prune_local_cache = False
    TrainArgs.lucid_mode = False
    TrainArgs.local_load = False
    TrainArgs.load_checkpoint = None
    TrainArgs.eval_arg_file = f"{Path(*Path(__file__).parts[-6:-1])}/{Path(__file__).stem}_eval.jsonl"

    TrainArgs.dataset_prefix = demo_prefixes[3]
    ACT_Config.lr = 5e-5
    ACT_Config.clip_max_norm = 0.0
    ACT_Config.kl_weight = 10
    ACT_Config.skip_encoder = False
    with sweep.product:
        ACT_Config.enc_layers = [4]
        ACT_Config.dec_layers = [4]
        ACT_Config.nheads = [8]
        ACT_Config.lr_backbone = [5e-5]
        with sweep.zip:
            TrainArgs.batch_size_val = [20]
            TrainArgs.batch_size_train = [20]
            ACT_Config.resnet_layer = [4]
        ACT_Config.backbone = ["resnet18"]
        ACT_Config.chunk_size = [25]
        TrainArgs.image_keys = [["wrist/rgb"]]
        ACT_Config.image_keys = [["wrist/rgb"]]
        TrainArgs.num_steps = [50000]
        TrainArgs.seed = [100,200,300]



from datetime import datetime

time = datetime.now()

checkpoints = {}


@sweep.each
def tail(RUN, TrainArgs, ACT_Config):
    RUN.prefix, RUN.job_name, _ = RUN(
        script_path=__file__,
        job_name=f"{time:%Y/%m/%d/%H-%M-%S}/backbone-{ACT_Config.backbone}/{'wrist-frame' if ACT_Config.delta_space else 'base-frame'}/lr_backbone-{ACT_Config.lr_backbone}/{TrainArgs.seed}"
    )
    checkpoints[RUN.prefix + "/checkpoints/policy_last.pt"] = f"chunksize-{ACT_Config.chunk_size}/{TrainArgs.seed}"


sweep.save(Path(__file__).stem + ".jsonl")
print(checkpoints)
print("Num checkpoints:", len(checkpoints))

with Sweep(RUN, Unroll, ACT_Config) as sweep:
    Unroll.checkpoint_host = "http://escher.csail.mit.edu:4000"

    Unroll.log_metrics = True
    Unroll.max_steps = 800
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
                ["left/rgb", "wrist/rgb", "right/rgb"],
            ]

        with sweep.zip:
            Unroll.seed = [*range(20)]
            Unroll.render = [True for _ in range(20)] + [False for _ in range(0)]  # only render 10% of the runs


@sweep.each
def tail(RUN, Unroll, ACT_Config):
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
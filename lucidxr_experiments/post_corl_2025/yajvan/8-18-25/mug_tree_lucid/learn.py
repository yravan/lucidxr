from pathlib import Path

from params_proto.hyper import Sweep

from lucidxr_experiments import RUN
from lucidxr.learning.act_config import ACT_Config
from lucidxr.learning.train import TrainArgs
from lucidxr.learning.unroll_eval import UnrollEval as Unroll
from lucidxr.learning.act_config import ACT_Config



demo_prefixes = [
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/24/14.30.11/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/25/11.43.11/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/28/11.20.15/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/28/11.50.11/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/28/12.13.04/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/28/12.29.47/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/28/13.38.46/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/28/14.06.58/",
]


with Sweep(RUN, TrainArgs, ACT_Config) as sweep:
    ACT_Config.normalize_actions = True
    ACT_Config.normalize_obs = True

    TrainArgs.dataset_host = '/home/ravan/datasets/escher_snapshot'

    TrainArgs.eval_interval = 5000
    TrainArgs.checkpoint_interval = 5000
    TrainArgs.prune_local_cache = False
    TrainArgs.lucid_mode = False
    TrainArgs.local_load = False
    TrainArgs.load_checkpoint = None
    TrainArgs.eval_arg_file = f"{Path(*Path(__file__).parts[-6:-1])}/{Path(__file__).stem}_eval.jsonl"
    TrainArgs.num_steps = 15000
    ACT_Config.lr = 1e-4
    ACT_Config.lr_backbone = 1e-5
    TrainArgs.batch_size_train = 64
    TrainArgs.batch_size_eval = 64

    ACT_Config.kl_weight = 10
    ACT_Config.skip_encoder = True
    ACT_Config.color_jitter = True
    with sweep.product:
        TrainArgs.dataset_prefix = [demo_prefixes[3:5]]
        ACT_Config.enc_layers = [4]
        ACT_Config.dec_layers = [4]
        ACT_Config.lr_backbone = [2e-4]
        ACT_Config.downsample_images = [1,2]
        TrainArgs.aug_camera_randomization = [True, False]
        with sweep.zip:
            ACT_Config.chunk_size = [25]
            ACT_Config.image_keys = [["wrist/lucid"]]



from datetime import datetime

time = datetime.now()

checkpoints = {}


@sweep.each
def tail(RUN, TrainArgs, ACT_Config):
    RUN.prefix, RUN.job_name, _ = RUN(
        script_path=__file__,
        job_name=f"{time:%Y/%m/%d/%H-%M-%S}/{'low-res' if ACT_Config.downsample_images>1 else 'high-res'}/cam_aug-{TrainArgs.aug_camera_randomization}"
    )
    checkpoints[RUN.prefix + "/checkpoints/policy_last.pt"] = f"chunksize-{ACT_Config.chunk_size}/{TrainArgs.seed}"


sweep.save(Path(__file__).stem + ".jsonl")
print(checkpoints)

with Sweep(RUN, Unroll, ACT_Config) as sweep:
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
            Unroll.seed = [*range(30)]
            Unroll.render = [True for _ in range(10)] + [False for _ in range(20)]  # only render 10% of the runs


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
from pathlib import Path

from params_proto.hyper import Sweep

from lucidxr.learning.train import TrainArgs
from lucidxr_experiments import RUN

from lucidxr.learning.unroll_eval import UnrollEval as Unroll
from lucidxr.learning.act_config import ACT_Config


with Sweep(RUN, TrainArgs, ACT_Config) as sweep:
    ACT_Config.normalize_actions = True
    ACT_Config.normalize_obs = True

    ACT_Config.obs_dim = 146
    ACT_Config.action_dim = 146

    TrainArgs.dataset_host = '/home/ravan/datasets/escher_snapshot'

    TrainArgs.eval_interval = 5000
    TrainArgs.checkpoint_interval = 5000
    TrainArgs.prune_local_cache = True
    TrainArgs.lucid_mode = False
    TrainArgs.local_load = False
    TrainArgs.load_checkpoint = None
    TrainArgs.eval_arg_file = f"{Path(*Path(__file__).parts[-6:-1])}/{Path(__file__).stem}_eval.jsonl"


    TrainArgs.dataset_prefix = ["/lucidxr/lucidxr/datasets/lucidxr/corl-2025/pour_liquid/2025/08/22/13.44.21",]
    ACT_Config.lr = 1e-4
    ACT_Config.clip_max_norm = 0.0
    ACT_Config.skip_encoder = False
    with sweep.product:
        ACT_Config.delta_space = [False]
        ACT_Config.downsample_images = [1]
        ACT_Config.enc_layers = [4]
        ACT_Config.dec_layers = [1]
        ACT_Config.nheads = [8]
        ACT_Config.color_jitter = [True]
        ACT_Config.lr_backbone = [1e-5, 1e-4, 2e-4]
        with sweep.zip:
            TrainArgs.batch_size_val = [64]
            TrainArgs.batch_size_train = [64]
            ACT_Config.resnet_layer = [4]
        ACT_Config.norm_layer = ["FrozenBatchNorm2d"]
        ACT_Config.backbone = ["resnet18"]
        ACT_Config.chunk_size = [25]
        ACT_Config.image_keys = [["right/rgb", "back/rgb", "top/rgb"]]
        TrainArgs.num_steps = [15000]



from datetime import datetime

time = datetime.now()

checkpoints = {}


@sweep.each
def tail(RUN, TrainArgs, ACT_Config):
    RUN.prefix, RUN.job_name, _ = RUN(
        script_path=__file__,
        job_name=f"{time:%Y/%m/%d/%H-%M-%S}/lr_backbone-{ACT_Config.lr_backbone}"
    )
    checkpoints[RUN.prefix + "/checkpoints/policy_last.pt"] = f"chunksize-{ACT_Config.chunk_size}/{TrainArgs.seed}"


sweep.save(Path(__file__).stem + ".jsonl")
print(checkpoints)
print("Num checkpoints:", len(checkpoints))

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
            Unroll.env_name = ["PourLiquid-cup_random-v1"]
            Unroll.image_keys = [
                ["right/rgb", "back/rgb", "top/rgb"],
            ]

        with sweep.zip:
            Unroll.seed = [*range(10)]
            Unroll.render = [True for _ in range(10)] + [False for _ in range(0)]  # only render 10% of the runs


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
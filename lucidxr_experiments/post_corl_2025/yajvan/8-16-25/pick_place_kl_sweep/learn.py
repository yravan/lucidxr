from pathlib import Path

from params_proto.hyper import Sweep

from lucidxr_experiments import RUN
from lucidxr.learning.act_config import ACT_Config
from lucidxr.learning.train import TrainArgs
from lucidxr.learning.unroll_eval import UnrollEval as Unroll
from lucidxr.learning.act_config import ACT_Config


with Sweep(RUN, TrainArgs, ACT_Config) as sweep:
    ACT_Config.normalize_actions = True
    ACT_Config.normalize_obs = True

    TrainArgs.dataset_host = '/home/ravan/datasets/escher_snapshot'

    TrainArgs.eval_interval = 5000
    TrainArgs.checkpoint_interval = 5000
    TrainArgs.prune_local_cache = True
    TrainArgs.lucid_mode = False
    TrainArgs.local_load = False
    TrainArgs.load_checkpoint = None
    TrainArgs.eval_arg_file = f"{Path(*Path(__file__).parts[-6:-1])}/{Path(__file__).stem}_eval.jsonl"


    TrainArgs.dataset_prefix = ["/lucidxr/lucidxr/datasets/lucidxr/corl-2025/pick_place_robot_room/2025/08/07/15.58.28/"]
    TrainArgs.batch_size_val = 48
    TrainArgs.batch_size_train = 48
    ACT_Config.lr = 1e-4
    ACT_Config.clip_max_norm = 0.0
    with sweep.product:
        ACT_Config.kl_weight = [0.001, 0.01, 0.1, 1]
        ACT_Config.downsample_images = [1,2]
        ACT_Config.enc_layers = [4]
        ACT_Config.dec_layers = [1]
        ACT_Config.nheads = [8]
        ACT_Config.lr_backbone = [2e-4]
        ACT_Config.backbone = ["resnet18"]
        ACT_Config.chunk_size = [25]
        ACT_Config.image_keys = [["wrist/domain_rand"]]
        TrainArgs.num_steps = [15000]



from datetime import datetime

time = datetime.now()

checkpoints = {}


@sweep.each
def tail(RUN, TrainArgs, ACT_Config):
    RUN.prefix, RUN.job_name, _ = RUN(
        script_path=__file__,
        job_name=f"{time:%Y/%m/%d/%H-%M-%S}/{'low-res' if ACT_Config.downsample_images > 1 else 'high-res'}/kl_weight-{ACT_Config.kl_weight}"
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
            Unroll.env_name = ["PickPlaceRobotRoom-single_random-v1",
                               "PickPlaceRobotRoom-single_random-domain_rand-v1",
                               "PickPlaceRobotRoom-single_random-domain_rand-v2",]
            Unroll.image_keys = [["right/rgb", "wrist/rgb", "left/rgb"],
                                 ["right/domain_rand", "wrist/domain_rand", "left/domain_rand"],
                                 ["right/domain_rand", "wrist/domain_rand", "left/domain_rand"],]
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
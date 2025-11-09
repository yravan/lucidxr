from pathlib import Path

from params_proto.hyper import Sweep

from lucidxr.learning.unroll_eval import UnrollEval as Unroll
from lucidxr_experiments import RUN
from lucidxr.learning.act_config import ACT_Config
from lucidxr.learning.train import TrainArgs

with Sweep(RUN, TrainArgs, ACT_Config) as sweep:
    ACT_Config.normalize_actions = True
    ACT_Config.normalize_obs = True
    ACT_Config.obs_dim = 10
    ACT_Config.action_dim = 10

    TrainArgs.dataset_prefix = ["/lucidxr/lucidxr/datasets/lucidxr/corl-2025/pick_place_robot_room/2025/07/25/18.08.37/"]
    TrainArgs.prune_local_cache = False
    TrainArgs.lucid_mode = False
    TrainArgs.local_load = False

    TrainArgs.load_checkpoint = None
    TrainArgs.eval_interval = 3000
    TrainArgs.checkpoint_interval = 3000
    TrainArgs.num_steps = 20000

    TrainArgs.seed = 42
    TrainArgs.eval_arg_file = f"{Path(*Path(__file__).parts[-5:-1])}/{Path(__file__).stem}_eval.jsonl"

    with sweep.product:
        ACT_Config.image_keys = [
            ["wrist/rgb"],
            ["wrist/rgb", "left/rgb", "right/rgb"],
        ]
        TrainArgs.aug_camera_randomization = [True, False]
        with sweep.zip:
            TrainArgs.batch_size_train = [64]
            TrainArgs.batch_size_eval = [64]
            ACT_Config.kl_weight = [1e-4]
            ACT_Config.lr = [1e-4]
            ACT_Config.lr_backbone = [1e-5]
        ACT_Config.chunk_size = [
            25,
            50,
            100,
        ]


from datetime import datetime

time = datetime.now()


@sweep.each
def tail(RUN, TrainArgs, ACT_Config):
    RUN.prefix, RUN.job_name, _ = RUN(
        script_path=__file__,
        job_name=f"{time:%Y/%m/%d/%H-%M-%S}/chunksize-{ACT_Config.chunk_size}/lr-{ACT_Config.lr:0.0e}/kl-{ACT_Config.kl_weight:0.0e}/{TrainArgs.seed}/image_keys-{ACT_Config.image_keys}/aug_camera_randomization-{TrainArgs.aug_camera_randomization}",
    )


sweep.save(Path(__file__).stem + ".jsonl")

with Sweep(RUN, Unroll, ACT_Config) as sweep:
    Unroll.checkpoint_host = "http://escher.csail.mit.edu:4000"

    Unroll.render = True
    Unroll.log_metrics = True
    Unroll.max_steps = 500
    # important
    Unroll.load_from_cache = False
    Unroll.overwrite = True

    with sweep.product:
        with sweep.zip:
            Unroll.env_name = ["PickPlaceRobotRoom-single_random-v1", "PickPlaceRobotRoom-fixed-v1"]
            Unroll.image_keys = [["right/rgb", "wrist/rgb", "left/rgb"], ["right/rgb", "wrist/rgb", "left/rgb"]]
        Unroll.seed = [*range(5)]


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
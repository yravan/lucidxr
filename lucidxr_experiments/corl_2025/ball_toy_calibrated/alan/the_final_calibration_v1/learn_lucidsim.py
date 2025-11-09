from pathlib import Path

from params_proto.hyper import Sweep

from lucidxr_experiments import RUN
from lucidxr.learning.act_config import ACT_Config
from lucidxr.learning.train import TrainArgs

with Sweep(RUN, TrainArgs, ACT_Config) as sweep:
    ACT_Config.normalize_actions = True
    ACT_Config.normalize_obs = True

    # TrainArgs.dataset_prefix = ["lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_calibrated/2025/07/01/23.59.36/"]
    TrainArgs.dataset_prefix = ["/lucidxr/lucidxr/datasets/lucidxr/corl-2025/the_final_calibration/2025/07/23/21.51.42/"]
    TrainArgs.prune_local_cache = False
    TrainArgs.lucid_mode = True
    TrainArgs.local_load = False

    TrainArgs.load_checkpoint = None
    TrainArgs.num_steps = 50000
    TrainArgs.batch_size_train = 48
    TrainArgs.batch_size_eval = 32

    TrainArgs.seed = 42

    ACT_Config.kl_weight = 10
    ACT_Config.lr = 5e-5
    ACT_Config.lr_backbone = 5e-6
    with sweep.product:
        ACT_Config.image_keys = [
            ["wrist/lucid", "left/lucid", "right/lucid"],
            ["wrist/lucid"],
            # ["wrist/rgb", "right/rgb"],
        ]
        TrainArgs.aug_camera_randomization = [
            True,
            False,
        ]
        ACT_Config.chunk_size = [
            # 50,
            100,
        ]


from datetime import datetime

time = datetime.now()


@sweep.each
def tail(RUN, TrainArgs, ACT_Config):
    RUN.prefix, RUN.job_name, _ = RUN(
        script_path=__file__,
        job_name=f"{time:%Y/%m/%d/%H-%M-%S}/cam_aug-{TrainArgs.aug_camera_randomization}/chunksize-{ACT_Config.chunk_size}/lr-{ACT_Config.lr:0.0e}/kl-{ACT_Config.kl_weight:0.0e}/{TrainArgs.seed}/image_keys-{ACT_Config.image_keys}",
    )


sweep.save(Path(__file__).stem + ".jsonl")

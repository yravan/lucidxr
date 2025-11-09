from pathlib import Path

from params_proto.hyper import Sweep

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

    TrainArgs.aug_camera_randomization = False

    TrainArgs.load_checkpoint = None
    TrainArgs.num_steps = 50000

    TrainArgs.seed = 42

    with sweep.product:
        ACT_Config.image_keys = [
            ["wrist/rgb", "left/rgb", "right/rgb"],
            ["wrist/rgb"],
        ]
        TrainArgs.aug_camera_randomization = [True, False]
        with sweep.zip:
            TrainArgs.batch_size_train = [64, 48]
            TrainArgs.batch_size_eval = [64, 32]
            ACT_Config.kl_weight = [1e-4, 10]
            ACT_Config.lr = [1e-4, 5e-5]
            ACT_Config.lr_backbone = [1e-5, 5e-6]
        ACT_Config.chunk_size = [
            50,
            # 100,
            # 150,
            # 200,
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

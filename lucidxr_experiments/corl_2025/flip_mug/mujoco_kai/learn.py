from pathlib import Path

from params_proto.hyper import Sweep

from lucidxr_experiments import RUN
from lucidxr.learning.act_config import ACT_Config
from lucidxr.learning.train import TrainArgs

with Sweep(RUN, TrainArgs, ACT_Config) as sweep:
    ACT_Config.normalize_actions = True
    ACT_Config.normalize_obs = True

    TrainArgs.dataset_prefix = [
        "lucidxr/lucidxr/datasets/lucidxr/corl-2025/flip_mug/2025/07/02/00.25.57/"
    ]
    TrainArgs.prune_local_cache = False
    TrainArgs.lucid_mode = False
    TrainArgs.local_load = False
    TrainArgs.load_checkpoint = None
    TrainArgs.num_steps = 50000
    TrainArgs.batch_size_train = 32
    TrainArgs.batch_size_eval = 32

    TrainArgs.seed = 42

    ACT_Config.kl_weight = 10
    ACT_Config.lr = 5e-5
    ACT_Config.lr_backbone = 5e-6
    with sweep.product:
        ACT_Config.chunk_size = [50, 100, 150]
        with sweep.product:
            ACT_Config.image_keys = [("back/rgb", "wrist/rgb", "right/rgb")]

from datetime import datetime

time = datetime.now()


@sweep.each
def tail(RUN, TrainArgs, ACT_Config):
    cam_id = 0
    if ACT_Config.image_keys == ("back/rgb", "wrist/rgb", "right/rgb"):
        cam_id = 1
    RUN.prefix, RUN.job_name, _ = RUN(
        script_path=__file__,
        job_name=f"corl_2025/flip_mug/{time:%Y/%m/%d/%H-%M-%S}/chunksize-{ACT_Config.chunk_size}/lr-{ACT_Config.lr:0.0e}/kl-{ACT_Config.kl_weight:0.0e}/{cam_id}/{TrainArgs.seed}",
    )


sweep.save(Path(__file__).stem + ".jsonl")
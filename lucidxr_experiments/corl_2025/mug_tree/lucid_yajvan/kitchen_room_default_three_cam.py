from pathlib import Path

from params_proto.hyper import Sweep

from lucidxr_experiments import RUN
from lucidxr.learning.act_config import ACT_Config
from lucidxr.learning.train import TrainArgs

with Sweep(RUN, TrainArgs, ACT_Config) as sweep:
    TrainArgs.dataset_prefix = [
        "lucidxr/lucidxr/datasets/lucidxr/rss-demos/kitchen_room/2025/04/28/21.46.21",
    ]
    ACT_Config.image_keys = ["right/rgb", "wrist/rgb", "right_r/rgb"]

    TrainArgs.prune_local_cache = False
    TrainArgs.load_checkpoint = None
    TrainArgs.lucid_mode = False

    ACT_Config.normalize_actions = True
    ACT_Config.normalize_obs = True

    ACT_Config.kl_weight = 10
    ACT_Config.lr = 5e-5
    ACT_Config.lr_backbone = 5e-6

    with sweep.zip:
        ACT_Config.chunk_size = [10,25,50,100]
        ACT_Config.kl_weight = [10, 25, 50, 100]
    TrainArgs.seed = 100

from datetime import datetime
time = datetime.now()

@sweep.each
def tail(RUN, TrainArgs, ACT_Config):
    RUN.prefix, RUN.job_name, _ = RUN(
        script_path=__file__,
        job_name=f"kitchen_room_default_three_cam/{time:%Y/%m/%d/%H-%M-%S}/chunk-{ACT_Config.chunk_size:03d}/{TrainArgs.seed}",
    )

sweep.save(Path(__file__).stem + ".jsonl")






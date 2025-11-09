from pathlib import Path

from params_proto.hyper import Sweep

from lucidxr_experiments import RUN
from lucidxr.learning.act_config import ACT_Config
from lucidxr.learning.train import TrainArgs

with Sweep(RUN, TrainArgs, ACT_Config) as sweep:
    TrainArgs.dataset_prefix = [
        "lucidxr/lucidxr/datasets/lucidxr/rss-demos/pick_block/2025/03",
        "lucidxr/lucidxr/datasets/lucidxr/rss-demos/pick_place/2025/03",
        "lucidxr/lucidxr/datasets/lucidxr/rss-demos/flip_mug/2025/03",
    ]

    TrainArgs.prune_local_cache = False
    TrainArgs.load_checkpoint = None

    ACT_Config.normalize_actions = True
    ACT_Config.normalize_obs = True

    ACT_Config.kl_weight = 10
    ACT_Config.lr = 5e-5
    ACT_Config.lr_backbone = 5e-6

    with sweep.product:
        ACT_Config.chunk_size = [4, 10, 25, 50,]
        TrainArgs.seed = [100, 200, 300]

from datetime import datetime
time = datetime.now()

@sweep.each
def tail(RUN, TrainArgs, ACT_Config):
    RUN.prefix, RUN.job_name, _ = RUN(
        script_path=__file__,
        job_name=f"{time:%Y/%m/%d/%H-%M-%S}/chunk-{ACT_Config.chunk_size:03d}/{TrainArgs.seed}",
    )

sweep.save(Path(__file__).stem + ".jsonl")






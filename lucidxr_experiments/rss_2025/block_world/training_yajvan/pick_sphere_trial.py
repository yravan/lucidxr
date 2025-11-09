from pathlib import Path

from params_proto.hyper import Sweep

from lucidxr_experiments import RUN
from lucidxr.learning.act_config import ACT_Config
from lucidxr.learning.train import TrainArgs

with Sweep(RUN, TrainArgs, ACT_Config) as sweep:
    TrainArgs.dataset_prefix = [
        "lucidxr/lucidxr/datasets/lucidxr/rss-demos/pick_sphere/2025/04",
    ]
    ACT_Config.image_keys = ["front/rgb", "left/rgb", "wrist/rgb"]

    TrainArgs.prune_local_cache = True
    TrainArgs.load_checkpoint = None

    ACT_Config.normalize_actions = True
    ACT_Config.normalize_obs = True

    with sweep.product:
        ACT_Config.kl_weight = [1, 0.1]

        with sweep.zip:
            ACT_Config.lr = [1e-5, 5e-5]
            ACT_Config.lr_backbone = [5e-6, 5e-5]

        TrainArgs.seed = [100, 200, 300]

from datetime import datetime
time = datetime.now()

@sweep.each
def tail(RUN, TrainArgs, ACT_Config):
    RUN.prefix, RUN.job_name, _ = RUN(
        script_path=__file__,
        job_name=f"pick_sphere_trial/{time:%Y/%m/%d/%H-%M-%S}/lr-{ACT_Config.lr:0.0e}/kl-{ACT_Config.kl_weight:0.0e}/{TrainArgs.seed}",
    )

sweep.save(Path(__file__).stem + ".jsonl")






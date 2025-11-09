from pathlib import Path

from params_proto.hyper import Sweep

from lucidxr_experiments import RUN
from lucidxr.learning.act_config import ACT_Config
from lucidxr.learning.train import TrainArgs

with Sweep(RUN, TrainArgs, ACT_Config) as sweep:
    TrainArgs.dataset_prefix = [
        "lucidxr/lucidxr/datasets/lucidxr/rss-demos/mug_tree/2025/04/29/18.46.35/",
    ]
    ACT_Config.image_keys = ["right/rgb", "wrist/rgb", "right_r/rgb"]

    TrainArgs.prune_local_cache = False
    TrainArgs.lucid_mode = False

    ACT_Config.normalize_actions = True
    ACT_Config.normalize_obs = True

    TrainArgs.seed = 101

    with sweep.zip:
      ACT_Config.kl_weight = [0.01, 0.1, 1, 5]
    ACT_Config.chunk_size = 50
    ACT_Config.lr = 5e-5



from datetime import datetime
time = datetime.now()

@sweep.each
def tail(RUN, TrainArgs, ACT_Config):
    RUN.prefix, RUN.job_name, _ = RUN(
        script_path=__file__,
        job_name=f"mug_tree_low_kl/{time:%Y/%m/%d/%H-%M-%S}/lr-{ACT_Config.lr:0.0e}/kl-{ACT_Config.kl_weight:0.0e}/{TrainArgs.seed}/{'_'.join([key.split('/')[0] for key in ACT_Config.image_keys])}",
    )

sweep.save(Path(__file__).stem + ".jsonl")






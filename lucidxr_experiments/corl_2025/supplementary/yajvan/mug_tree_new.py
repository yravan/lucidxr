from pathlib import Path

from params_proto.hyper import Sweep

from lucidxr_experiments import RUN
from lucidxr.learning.act_config import ACT_Config
from lucidxr.learning.train import TrainArgs

with Sweep(RUN, TrainArgs, ACT_Config) as sweep:
    TrainArgs.dataset_prefix = [
        "lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/05/06/15.35.08/",
    ]
    ACT_Config.image_keys = ["right/rgb", "wrist/rgb", "front/rgb"]

    TrainArgs.prune_local_cache = False
    TrainArgs.lucid_mode = False
    TrainArgs.local_load = False
    TrainArgs.load_checkpoint = "/lucidxr/lucidxr/corl_2025/supplementary/yajvan/mug_tree_new/corl_2025/mug_tree_new/2025/05/06/22-54-35/lr-6e-05/kl-1e+01/101/checkpoints/policy_last.pt"
    TrainArgs.num_steps = 50000

    ACT_Config.normalize_actions = True
    ACT_Config.normalize_obs = True

    TrainArgs.seed = 101

    # TrainArgs.batch_size_train = 200
    # TrainArgs.batch_size_val = 200
    ACT_Config.kl_weight = 10
    ACT_Config.chunk_size = 150
    ACT_Config.lr = 1e-4
    ACT_Config.lr_backbone = 1e-5

from datetime import datetime

time = datetime.now()


@sweep.each
def tail(RUN, TrainArgs, ACT_Config):
    RUN.prefix, RUN.job_name, _ = RUN(
        script_path=__file__,
        job_name=f"corl_2025/mug_tree_new/{time:%Y/%m/%d/%H-%M-%S}/lr-{ACT_Config.lr:0.0e}/kl-{ACT_Config.kl_weight:0.0e}/{TrainArgs.seed}",
    )


sweep.save(Path(__file__).stem + ".jsonl")

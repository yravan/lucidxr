from pathlib import Path

from params_proto.hyper import Sweep

from lucidxr_experiments import RUN
from lucidxr.learning.act_config import ACT_Config
from lucidxr.learning.train import TrainArgs

with Sweep(RUN, TrainArgs, ACT_Config) as sweep:
    ACT_Config.normalize_actions = True
    ACT_Config.normalize_obs = True

    TrainArgs.dataset_prefix = [
        "lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/01/12.45.07/",
    ]
    TrainArgs.prune_local_cache = False
    TrainArgs.lucid_mode = False
    TrainArgs.local_load = False
    TrainArgs.load_checkpoint = None
    TrainArgs.num_steps = 20000
    TrainArgs.batch_size_train = 48
    TrainArgs.batch_size_eval = 32

    TrainArgs.seed = 42

    ACT_Config.kl_weight = 10
    ACT_Config.lr = 5e-5
    ACT_Config.lr_backbone = 5e-6
    ACT_Config.image_keys = ["left/domain_rand", "wrist/domain_rand", "right/domain_rand"]
    with sweep.product:
        ACT_Config.chunk_size = [100]


from datetime import datetime
time = datetime.now()

@sweep.each
def tail(RUN, TrainArgs, ACT_Config):
    RUN.prefix, RUN.job_name, _ = RUN(
        script_path=__file__,
        job_name=f"{time:%Y/%m/%d/%H-%M-%S}/chunksize-{ACT_Config.chunk_size}/lr-{ACT_Config.lr:0.0e}/kl-{ACT_Config.kl_weight:0.0e}/{TrainArgs.seed}",
    )


sweep.save(Path(__file__).stem + ".jsonl")

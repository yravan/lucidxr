from pathlib import Path

from params_proto.hyper import Sweep

from lucidxr_experiments import RUN
from lucidxr.learning.act_config import ACT_Config
from lucidxr.learning.train import TrainArgs

with Sweep(RUN, TrainArgs, ACT_Config) as sweep:
    TrainArgs.dataset_prefix=[
        "lucidxr/lucidxr/datasets/lucidxr/rss-demos/pick_block",
    ]
    TrainArgs.load_checkpoint=None

    ACT_Config.normalize_actions = True
    ACT_Config.normalize_obs = True

    # ACT_Config.lr = 1e-4
    # ACT_Config.lr_backbone = 5e-6
    # ACT_Config.kl_weight = 100

    with sweep.product:
        TrainArgs.seed = [100]

@sweep.each
def tail(RUN, TrainArgs, ACT_Config):
    # env_key = TrainArgs.env_name.split("-")[0].lower()
    RUN.prefix, RUN.job_name, _ = RUN(
        script_path=__file__,
        job_name=f"lr-{ACT_Config.lr:0.0e}/{TrainArgs.seed}",
    )

sweep.save(Path(__file__).stem + ".jsonl")






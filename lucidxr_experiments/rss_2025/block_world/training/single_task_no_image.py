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
    TrainArgs.checkpoint_interval=5000
    TrainArgs.action_space="absolute"

    ACT_Config.normalize_actions = True
    ACT_Config.normalize_obs = True
    ACT_Config.image_keys = []

    ACT_Config.lr_backbone = 5e-6

    TrainArgs.seed = 10

    with sweep.product:
        ACT_Config.kl_weight = [10, 50]
        ACT_Config.lr = [1e-4, 1e-5]
        TrainArgs.seed = [10, 20]

from datetime import datetime
time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

@sweep.each
def tail(RUN, TrainArgs, ACT_Config):
    RUN.prefix, RUN.job_name, _ = RUN(
        script_path=__file__,
        job_name=f"single_task_no_image/{time}/lr-{ACT_Config.lr:0.0e}/kl-{ACT_Config.kl_weight:0.0e}/{TrainArgs.seed}",
    )

sweep.save(Path(__file__).stem + ".jsonl")






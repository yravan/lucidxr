from pathlib import Path

from params_proto.hyper import Sweep

from lucidxr_experiments import RUN
from lucidxr.learning.act_config import ACT_Config
from lucidxr.learning.train import TrainArgs
from lucidxr.learning.unroll_eval import UnrollEval as Unroll
from lucidxr.learning.act_config import ACT_Config




demo_prefixes = [
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/21/14.18.42/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/25/11.08.50/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/28/15.18.01/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/28/15.45.15/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/28/17.00.58/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/28/17.29.57/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/28/17.57.54/",
    "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/28/18.21.00/",
    ]

with Sweep(RUN, TrainArgs, ACT_Config) as sweep:
    ACT_Config.normalize_actions = True
    ACT_Config.normalize_obs = True

    TrainArgs.eval_interval = 3000
    TrainArgs.checkpoint_interval = 3000
    TrainArgs.prune_local_cache = False
    TrainArgs.lucid_mode = False
    TrainArgs.local_load = False
    TrainArgs.load_checkpoint = None
    TrainArgs.max_epochs = 0
    TrainArgs.eval_arg_file = f"{Path(*Path(__file__).parts[-5:-1])}/{Path(__file__).stem}_eval.jsonl"

    ACT_Config.chunk_size = 50
    ACT_Config.lr = 5e-5
    ACT_Config.lr_backbone = 5e-6
    ACT_Config.image_keys = ["right/rgb", "wrist/rgb", "left/rgb"]
    ACT_Config.kl_weight = 1e-3
    TrainArgs.batch_size_train = 64
    TrainArgs.batch_size_eval = 64
    TrainArgs.dataset_prefix = demo_prefixes


from datetime import datetime

time = datetime.now()

checkpoints = {}


@sweep.each
def tail(RUN, TrainArgs, ACT_Config):
    RUN.prefix, RUN.job_name, _ = RUN(
        script_path=__file__,
        job_name=f"{time:%Y/%m/%d/%H-%M-%S}/num_demos-{len(TrainArgs.dataset_prefix)*50}"
    )
    checkpoints[RUN.prefix + "/checkpoints/policy_last.pt"] = f"chunksize-{ACT_Config.chunk_size}/{TrainArgs.seed}"


sweep.save(Path(__file__).stem + ".jsonl")
print(checkpoints)

with Sweep(RUN, Unroll, ACT_Config) as sweep:
    Unroll.checkpoint_host = "http://escher.csail.mit.edu:4000"

    Unroll.render = False
    Unroll.log_metrics = True
    Unroll.max_steps = 500
    # important
    Unroll.load_from_cache = False
    Unroll.overwrite = True
    Unroll.action_smoothing = False

    Unroll.env_name = "MugTree-mug_rand-v1"
    Unroll.image_keys = ["right/rgb", "wrist/rgb", "left/rgb"]
    with sweep.product:
        Unroll.seed = [*range(10)]


@sweep.each
def tail(RUN, Unroll, ACT_Config):
    RUN.prefix, RUN.job_name, _ = RUN(
        script_path=__file__,
    )
    print(RUN.prefix)


from ml_logger.job import RUN, instr  # noqa

RUN.job_name = "{now:%Y/%m-%d}"
RUN.prefix = "lucidxr/lucidxr/{file_stem}/{job_name}"
# this sets the root for calculating the prefix
RUN.script_root = Path(__file__).parent
sweep.save(f"{Path(__file__).stem}_eval.jsonl")
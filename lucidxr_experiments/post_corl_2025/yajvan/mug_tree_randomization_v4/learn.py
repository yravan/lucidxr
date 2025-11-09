from pathlib import Path

from params_proto.hyper import Sweep

from lucidxr_experiments import RUN
from lucidxr.learning.act_config import ACT_Config
from lucidxr.learning.train import TrainArgs
from lucidxr.learning.unroll_eval import UnrollEval as Unroll
from lucidxr.learning.act_config import ACT_Config




with Sweep(RUN, TrainArgs, ACT_Config) as sweep:
    ACT_Config.normalize_actions = True
    ACT_Config.normalize_obs = True

    TrainArgs.dataset_prefix = [
        "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/16/11.02.57/"
    ]
    TrainArgs.eval_interval = 3000
    TrainArgs.checkpoint_interval = 3000
    TrainArgs.prune_local_cache = False
    TrainArgs.lucid_mode = False
    TrainArgs.local_load = False
    TrainArgs.load_checkpoint = None
    TrainArgs.num_steps = 30000
    TrainArgs.batch_size_train = 64
    TrainArgs.batch_size_eval = 64
    TrainArgs.eval_arg_file = f"{Path(*Path(__file__).parts[-5:-1])}/{Path(__file__).stem}_eval.jsonl"


    ACT_Config.kl_weight = 10
    ACT_Config.lr = 1e-4
    ACT_Config.lr_backbone = 1e-5
    ACT_Config.chunk_size = 100
    with sweep.product:
        ACT_Config.image_keys = [ ["wrist/rgb"], ["wrist/rgb", "right/rgb"], ["left/rgb", "wrist/rgb", "right/rgb"]]
        TrainArgs.seed = [0]


from datetime import datetime
time = datetime.now()

checkpoints = {}
@sweep.each
def tail(RUN, TrainArgs, ACT_Config):
    RUN.prefix, RUN.job_name, _ = RUN(
        script_path=__file__,
        job_name=f"{time:%Y/%m/%d/%H-%M-%S}/image_keys-{'-'.join(ACT_Config.image_keys).replace('/rgb','')}/{TrainArgs.seed}",
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

    with sweep.product:
        with sweep.zip:
            Unroll.env_name = ["MugTree-rand-v2", "MugTree-fixed-v1"]
            Unroll.image_keys = [["right/rgb", "wrist/rgb", "left/rgb"], ["right/rgb", "wrist/rgb", "left/rgb"]]
            ACT_Config.image_keys = [
                ["right/rgb", "wrist/rgb", "left/rgb"],
                ["right/rgb", "wrist/rgb", "left/rgb"],
            ]
        Unroll.seed = [*range(5)]


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

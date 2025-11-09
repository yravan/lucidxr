from pathlib import Path

from params_proto.hyper import Sweep

from lucidxr_experiments import RUN
from diffusion.train_policy_conditional import Args as TrainArgs
from diffusion.models.policy import DiffusionPolicyArgs
from lucidxr.learning.unroll_eval import UnrollEval as Unroll


with Sweep(RUN, TrainArgs, DiffusionPolicyArgs) as sweep:
    TrainArgs.dataset_host = '/home/ravan/datasets/escher_snapshot'

    TrainArgs.prune_cache = True

    TrainArgs.eval_arg_file = f"{Path(*Path(__file__).parts[-6:-1])}/{Path(__file__).stem}_eval.jsonl"

    TrainArgs.dataset_prefix = ["/lucidxr/lucidxr/datasets/lucidxr/corl-2025/pick_place_robot_room/2025/08/07/15.58.28/",]
    TrainArgs.n_epochs = 200
    TrainArgs.epoch_checkpoint_interval = 50
    TrainArgs.chunk_size = 24
    TrainArgs.debug = False
    TrainArgs.vis_dim = 1024

    TrainArgs.aug_camera_randomization = True
    TrainArgs.p_cam_rand = 1.0
    TrainArgs.randomize_wrist = True
    with sweep.product:
        TrainArgs.embed_dim = [128, 512]
        with sweep.zip:
            TrainArgs.batch_size = [20, 64]
            TrainArgs.image_keys = [["wrist/lucid", "right/lucid", "left/lucid"], ["wrist/lucid"]]


from datetime import datetime

time = datetime.now()

checkpoints = {}


@sweep.each
def tail(RUN, TrainArgs, DiffusionPolicyArgs):
    RUN.prefix, RUN.job_name, _ = RUN(
        script_path=__file__,
        job_name=f"{time:%Y/%m/%d/%H-%M-%S}/{'wrist-only' if len(TrainArgs.image_keys)==1 else 'all-three'}/embed_dim-{TrainArgs.embed_dim}",
    )
    checkpoints[RUN.prefix + "/checkpoints/policy_last.pt"] = f"chunksize-{DiffusionPolicyArgs.chunk_size}/{TrainArgs.seed}"


sweep.save(Path(__file__).stem + ".jsonl")
print(checkpoints)
print("Num checkpoints:", len(checkpoints))

with Sweep(RUN, Unroll, TrainArgs) as sweep:
    Unroll.checkpoint_host = "http://escher.csail.mit.edu:4000"

    Unroll.log_metrics = True
    Unroll.max_steps = 500
    # important
    Unroll.load_from_cache = False
    Unroll.overwrite = True
    Unroll.action_smoothing = True

    with sweep.product:
        with sweep.zip:
            Unroll.env_name = ["PickPlaceRobotRoom-single_random-v1",
                               "PickPlaceRobotRoom-single_random-domain_rand-v1",
                               "PickPlaceRobotRoom-single_random-domain_rand-v2",
                               "PickPlaceEval-single_random-gsplat-v1"]
            Unroll.image_keys = [
                ["right/rgb", "wrist/rgb", "left/rgb"],
                ["right/domain_rand", "wrist/domain_rand", "left/domain_rand"],
                ["right/domain_rand", "wrist/domain_rand", "left/domain_rand"],
                ["right/splat_rgb", "wrist/splat_rgb", "left/splat_rgb"],
            ]

        with sweep.zip:
            Unroll.seed = [*range(10)]
            Unroll.render = [True for _ in range(10)] + [False for _ in range(0)]  # only render 10% of the runs

@sweep.each
def tail(RUN, Unroll, TrainArgs):
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
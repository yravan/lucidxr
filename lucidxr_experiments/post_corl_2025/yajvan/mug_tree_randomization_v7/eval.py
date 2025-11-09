from pathlib import Path

from params_proto.hyper import Sweep
from lucidxr_experiments import RUN
from lucidxr.learning.unroll_eval import UnrollEval as Unroll
from lucidxr.learning.act_config import ACT_Config


checkpoints = {
    "/lucidxr/lucidxr/post_corl_2025/yajvan/mug_tree_randomization_v7/learn/2025/07/23/23-54-14/image_keys-left-wrist-right/chunksize-100/kl-3e-05/lr-0.0001/0/checkpoints/policy_last.pt": "kl-3e-05-lr-0.0001",
    "/lucidxr/lucidxr/post_corl_2025/yajvan/mug_tree_randomization_v7/learn/2025/07/23/23-54-14/image_keys-left-wrist-right/chunksize-100/kl-0.0003/lr-0.0001/0/checkpoints/policy_last.pt": "kl-0.0003-lr-0.0001",
    "/lucidxr/lucidxr/post_corl_2025/yajvan/mug_tree_randomization_v7/learn/2025/07/23/23-54-14/image_keys-left-wrist-right/chunksize-100/kl-0.0001/lr-0.0001/0/checkpoints/policy_last.pt": "kl-0.0001-lr-0.0001",
}

if __name__ == "__main__":
    with Sweep(RUN, Unroll, ACT_Config) as sweep:
        Unroll.checkpoint_host = "http://escher.csail.mit.edu:4000"
        
        Unroll.render = True
        Unroll.log_metrics = True
        Unroll.max_steps = 700
        Unroll.load_from_cache = True

        Unroll.image_keys = ["right/rgb", "wrist/rgb", "left/rgb"]
        with sweep.product:
            Unroll.env_name = ["MugTree-fixed-v1", "MugTree-rand-v2"]
            with sweep.zip:
                Unroll.action_smoothing = [False, True, True, True]
                ACT_Config.action_weighting_factor = [0.0, 0.01, 0.1, 1]
            Unroll.load_checkpoint = list(checkpoints.keys())
            Unroll.seed = [*range(5)]

    @sweep.each
    def tail(RUN, Unroll, ACT_Config):

        RUN.prefix, RUN.job_name, _ = RUN(
            script_path=__file__,
            job_name=f"{Unroll.env_name}/{checkpoints[Unroll.load_checkpoint]}/{ACT_Config.action_weighting_factor}",
        )
        print(RUN.prefix)

    sweep.save(f"{Path(__file__).stem}.jsonl")

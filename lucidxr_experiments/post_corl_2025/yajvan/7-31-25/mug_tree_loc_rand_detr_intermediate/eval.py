from pathlib import Path

from params_proto.hyper import Sweep
from lucidxr_experiments import RUN
from lucidxr.learning.unroll_eval import UnrollEval as Unroll
from lucidxr.learning.act_config import ACT_Config


checkpoints = {
    "/lucidxr/lucidxr/post_corl_2025/yajvan/7-31-25/mug_tree_loc_rand_detr_intermediate/learn/2025/07/31/14-10-28/lr-0.0001/kl-0.0001/0/checkpoints/policy_0002000.pt": "2000 steps",
    "/lucidxr/lucidxr/post_corl_2025/yajvan/7-31-25/mug_tree_loc_rand_detr_intermediate/learn/2025/07/31/14-10-28/lr-0.0001/kl-0.0001/0/checkpoints/policy_0004000.pt": "4000 steps",
    "/lucidxr/lucidxr/post_corl_2025/yajvan/7-31-25/mug_tree_loc_rand_detr_intermediate/learn/2025/07/31/14-10-28/lr-0.0001/kl-0.0001/0/checkpoints/policy_0006000.pt": "6000 steps",
    "/lucidxr/lucidxr/post_corl_2025/yajvan/7-31-25/mug_tree_loc_rand_detr_intermediate/learn/2025/07/31/14-10-28/lr-0.0001/kl-0.0001/0/checkpoints/policy_0008000.pt": "8000 steps",
    "/lucidxr/lucidxr/post_corl_2025/yajvan/7-31-25/mug_tree_loc_rand_detr_intermediate/learn/2025/07/31/14-10-28/lr-0.0001/kl-0.0001/0/checkpoints/policy_0010000.pt": "10000 steps",
    # "/lucidxr/lucidxr/post_corl_2025/yajvan/7-31-25/mug_tree_loc_rand_detr_intermediate/learn/2025/07/31/14-10-28/lr-0.0001/kl-0.0001/0/checkpoints/policy_0012000.pt": "12000 steps",
    # "/lucidxr/lucidxr/post_corl_2025/yajvan/7-31-25/mug_tree_loc_rand_detr_intermediate/learn/2025/07/31/14-10-28/lr-0.0001/kl-0.0001/0/checkpoints/policy_0014000.pt": "14000 steps",
    # "/lucidxr/lucidxr/post_corl_2025/yajvan/7-31-25/mug_tree_loc_rand_detr_intermediate/learn/2025/07/31/14-10-28/lr-0.0001/kl-0.0001/0/checkpoints/policy_0016000.pt": "16000 steps",
    # "/lucidxr/lucidxr/post_corl_2025/yajvan/7-31-25/mug_tree_loc_rand_detr_intermediate/learn/2025/07/31/14-10-28/lr-0.0001/kl-0.0001/0/checkpoints/policy_0018000.pt": "18000 steps",

}

if __name__ == "__main__":
    with Sweep(RUN, Unroll, ACT_Config) as sweep:
        Unroll.env_name = "TieKnot-v1"
        Unroll.checkpoint_host = "http://escher.csail.mit.edu:4000"
        
        Unroll.render = False
        Unroll.log_metrics = True
        Unroll.max_steps = 500
        Unroll.load_from_cache = True

        Unroll.env_name = "MugTree-mug_rand-v1"
        Unroll.image_keys = ["right/rgb", "wrist/rgb", "left/rgb"]

        Unroll.train_step = None
        Unroll.results_file = "episode_metrics.pkl"

        with sweep.product:
            Unroll.load_checkpoint = list(checkpoints.keys())
            Unroll.seed = [*range(50)]

    @sweep.each
    def tail(RUN, Unroll, ACT_Config):


        RUN.prefix, RUN.job_name, _ = RUN(
            script_path=__file__,
            job_name=f"{Unroll.env_name}/{checkpoints[Unroll.load_checkpoint]}/",
        )
        print(RUN.prefix)

    sweep.save(f"{Path(__file__).stem}.jsonl")

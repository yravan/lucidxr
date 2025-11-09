from pathlib import Path

from params_proto.hyper import Sweep
from lucidxr_experiments import RUN
from lucidxr.learning.unroll_eval import UnrollEval as Unroll
from lucidxr.learning.act_config import ACT_Config


checkpoints = {
    "/lucidxr/lucidxr/post_corl_2025/yajvan/mug_tree_randomization_v3/learn/2025/07/18/17-56-02/image_keys-wrist-right/0/checkpoints/policy_last.pt": "wrist",
    "/lucidxr/lucidxr/post_corl_2025/yajvan/mug_tree_randomization_v3/learn/2025/07/18/17-56-02/image_keys-wrist/0/checkpoints/policy_last.pt": "wrist_right",
    "/lucidxr/lucidxr/post_corl_2025/yajvan/mug_tree_randomization_v3/learn/2025/07/18/17-56-02/image_keys-left-wrist-right/0/checkpoints/policy_last.pt": "left_wrist_right",
}

if __name__ == "__main__":
    with Sweep(RUN, Unroll, ACT_Config) as sweep:
        Unroll.checkpoint_host = "http://escher.csail.mit.edu:4000"
        
        Unroll.render = True
        Unroll.log_metrics = True
        Unroll.max_steps = 500
        Unroll.load_from_cache = True

        with sweep.product:
            with sweep.zip:
                Unroll.env_name = ["MugTree-fixed-v1"]
                Unroll.image_keys = [["right/rgb", "wrist/rgb", "left/rgb"]]
            Unroll.load_checkpoint = list(checkpoints.keys())
            Unroll.seed = [*range(3)]

    @sweep.each
    def tail(RUN, Unroll, ACT_Config):
        
        RUN.prefix, RUN.job_name, _ = RUN(
            script_path=__file__,
            job_name=f"eval_encoded_latent/{Unroll.env_name}/{checkpoints[Unroll.load_checkpoint]}",
        )
        print(RUN.prefix)

    sweep.save(f"{Path(__file__).stem}.jsonl")

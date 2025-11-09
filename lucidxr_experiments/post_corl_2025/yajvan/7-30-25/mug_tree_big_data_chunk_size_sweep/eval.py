from pathlib import Path

from params_proto.hyper import Sweep
from lucidxr_experiments import RUN
from lucidxr.learning.unroll_eval import UnrollEval as Unroll
from lucidxr.learning.act_config import ACT_Config


checkpoints = {
    "/lucidxr/lucidxr/post_corl_2025/yajvan/7-31-25/../7-30-25/mug_tree_big_data_chunk_size_sweep/learn/2025/07/30/16-30-28/chunksize-75/kl-0.0001/image_keys-right-wrist-left/checkpoints/policy_last.pt": "kl-0.0001",
    "/lucidxr/lucidxr/post_corl_2025/yajvan/7-31-25/../7-30-25/mug_tree_big_data_chunk_size_sweep/learn/2025/07/30/16-30-28/chunksize-25/kl-0.0001/image_keys-right-wrist-left/checkpoints/policy_last.pt": "kl-0.001",
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
        Unroll.results_file = "episode_metrics_no_tagg.pkl"
        Unroll.action_smoothing = False

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

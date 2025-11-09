from pathlib import Path

from params_proto.hyper import Sweep
from lucidxr_experiments import RUN
from lucidxr.learning.unroll_eval import UnrollEval as Unroll
from lucidxr.learning.act_config import ACT_Config


checkpoints = {
    # "/lucidxr/lucidxr/corl_2025/mug_tree/mujoco_yajvan/randomized_v3/learn/2025/06/29/17-12-56/chunksize-50/lr-5e-05/kl-1e+01/42/checkpoints/policy_last.pt": "chunksize-50",
    "/lucidxr/lucidxr/corl_2025/mug_tree_ur/lucid_yajvan/randomized_v4/learn/2025/07/02/18-48-28/chunksize-150/lr-5e-05/kl-1e+01/42/checkpoints/policy_last.pt": "chunksize-150",
    # "/lucidxr/lucidxr/corl_2025/mug_tree/mujoco_yajvan/randomized_v3/learn/2025/06/29/17-12-56/chunksize-150/lr-5e-05/kl-1e+01/42/checkpoints/policy_last.pt": "chunksize-150",
}

if __name__ == "__main__":
    with Sweep(RUN, Unroll, ACT_Config) as sweep:
        Unroll.env_name = "MugTree-mug_rand-v1"
        Unroll.checkpoint_host = "http://escher.csail.mit.edu:4000"
        
        Unroll.render = False
        Unroll.log_metrics = True
        Unroll.max_steps = 800
        Unroll.load_from_cache = False

        with sweep.product:
            with sweep.zip:
                Unroll.env_name = ["MugTreeUr-mug_rand-v1", "MugTreeUr-mug_rand-domain_rand-eval-v1"]
                Unroll.image_keys = [["right/rgb", "wrist/rgb", "left/rgb"],
                                     ["right/domain_rand", "wrist/domain_rand", "left/domain_rand"]]
                ACT_Config.image_keys = [["right/rgb", "wrist/rgb", "left/rgb"],
                                         ["right/domain_rand", "wrist/domain_rand", "left/domain_rand"]]
            Unroll.load_checkpoint = list(checkpoints.keys())
            Unroll.seed = [*range(50)]

    @sweep.each
    def tail(RUN, Unroll, ACT_Config):
        ckpt_meta = checkpoints[Unroll.load_checkpoint]

        chunk_size = int(ckpt_meta.split("chunksize-")[-1].split("/")[0])
        ACT_Config.chunk_size = chunk_size
        
        RUN.prefix, RUN.job_name, _ = RUN(
            script_path=__file__,
            job_name=f"{Unroll.env_name}/{checkpoints[Unroll.load_checkpoint]}/",
        )
        print(RUN.prefix)

    sweep.save(f"{Path(__file__).stem}.jsonl")

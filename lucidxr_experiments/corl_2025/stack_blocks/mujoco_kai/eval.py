from pathlib import Path

from params_proto.hyper import Sweep
from lucidxr_experiments import RUN
from lucidxr.learning.unroll_eval import UnrollEval as Unroll
from lucidxr.learning.act_config import ACT_Config


checkpoints = {
    "/lucidxr/lucidxr/corl_2025/stack_blocks/mujoco_kai/learn/corl_2025/pick_place_v1/2025/06/30/11-51-00/chunksize-100/lr-5e-05/kl-1e+01/1/42/checkpoints/policy_last.pt": "chunksize-100/",
    "/lucidxr/lucidxr/corl_2025/stack_blocks/mujoco_kai/learn/corl_2025/pick_place_v1/2025/06/30/11-51-00/chunksize-50/lr-5e-05/kl-1e+01/1/42/checkpoints/policy_last.pt": "chunksize-50/",
}

if __name__ == "__main__":
    with Sweep(RUN, Unroll, ACT_Config) as sweep:
        Unroll.env_name = "StackBlocks-random-v1"
        Unroll.checkpoint_host = "http://escher.csail.mit.edu:4000"
        
        Unroll.render = False
        Unroll.log_metrics = True
        Unroll.max_steps = 500
        Unroll.load_from_cache = True
        
        with sweep.product:
            Unroll.load_checkpoint = list(checkpoints.keys())
            Unroll.seed = [*range(100)]

    @sweep.each
    def tail(RUN, Unroll, ACT_Config):
        ckpt_meta = checkpoints[Unroll.load_checkpoint]
        
        # if "cameras-1" in ckpt_meta:
        #     ACT_Config.image_keys = ["right/rgb", "wrist/rgb", "front/rgb"]
        #     Unroll.image_keys = ["right/rgb", "wrist/rgb", "front/rgb"]
        # elif "cameras-0" in ckpt_meta:
        ACT_Config.image_keys = ["right/rgb", "wrist/rgb", "front/rgb"]
        Unroll.image_keys = ["right/rgb", "wrist/rgb", "front/rgb"]
        # else:
        #     raise ValueError(f"Unknown checkpoint meta: {ckpt_meta}")
        
        chunk_size = int(ckpt_meta.split("chunksize-")[-1].split("/")[0])
        ACT_Config.chunk_size = chunk_size
        
        RUN.prefix, RUN.job_name, _ = RUN(
            script_path=__file__,
            job_name=f"{Unroll.env_name}/{checkpoints[Unroll.load_checkpoint]}/",
        )
        print(RUN.prefix)

    sweep.save(f"{Path(__file__).stem}.jsonl")

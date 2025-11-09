from pathlib import Path

from params_proto.hyper import Sweep
from lucidxr_experiments import RUN
from lucidxr.learning.unroll_eval import UnrollEval as Unroll
from lucidxr.learning.act_config import ACT_Config


checkpoints = {
    "/lucidxr/lucidxr/post_corl_2025/yajvan/8-18-25/pick_block_sim_real_cotrain/learn/2025/08/18/19-18-38/real-data-fraction-1.0/wrist-only-True/resnet_layer-4/color_jitter-True/checkpoints/policy_last.pt": 0,
    "/lucidxr/lucidxr/post_corl_2025/yajvan/8-18-25/pick_block_sim_real_cotrain/learn/2025/08/18/19-18-38/real-data-fraction-1.0/wrist-only-True/resnet_layer-4/color_jitter-False/checkpoints/policy_last.pt": 0,
    "/lucidxr/lucidxr/post_corl_2025/yajvan/8-18-25/pick_block_sim_real_cotrain/learn/2025/08/18/19-18-38/real-data-fraction-1.0/wrist-only-True/resnet_layer-3/color_jitter-True/checkpoints/policy_last.pt": 0,
    "/lucidxr/lucidxr/post_corl_2025/yajvan/8-18-25/pick_block_sim_real_cotrain/learn/2025/08/18/19-18-38/real-data-fraction-1.0/wrist-only-True/resnet_layer-3/color_jitter-False/checkpoints/policy_last.pt": 0,
    "/lucidxr/lucidxr/post_corl_2025/yajvan/8-18-25/pick_block_sim_real_cotrain/learn/2025/08/18/19-18-38/real-data-fraction-1.0/wrist-only-False/resnet_layer-4/color_jitter-True/checkpoints/policy_last.pt": 0,
    "/lucidxr/lucidxr/post_corl_2025/yajvan/8-18-25/pick_block_sim_real_cotrain/learn/2025/08/18/19-18-38/real-data-fraction-1.0/wrist-only-False/resnet_layer-4/color_jitter-False/checkpoints/policy_last.pt": 0,
    "/lucidxr/lucidxr/post_corl_2025/yajvan/8-18-25/pick_block_sim_real_cotrain/learn/2025/08/18/19-18-38/real-data-fraction-1.0/wrist-only-False/resnet_layer-3/color_jitter-True/checkpoints/policy_last.pt": 0,
    "/lucidxr/lucidxr/post_corl_2025/yajvan/8-18-25/pick_block_sim_real_cotrain/learn/2025/08/18/19-18-38/real-data-fraction-1.0/wrist-only-False/resnet_layer-3/color_jitter-False/checkpoints/policy_last.pt": 0,
    "/lucidxr/lucidxr/post_corl_2025/yajvan/8-18-25/pick_block_sim_real_cotrain/learn/2025/08/18/19-18-38/real-data-fraction-0.5/wrist-only-True/resnet_layer-4/color_jitter-True/checkpoints/policy_last.pt": 0,
    "/lucidxr/lucidxr/post_corl_2025/yajvan/8-18-25/pick_block_sim_real_cotrain/learn/2025/08/18/19-18-38/real-data-fraction-0.5/wrist-only-True/resnet_layer-4/color_jitter-False/checkpoints/policy_last.pt": 0,
    "/lucidxr/lucidxr/post_corl_2025/yajvan/8-18-25/pick_block_sim_real_cotrain/learn/2025/08/18/19-18-38/real-data-fraction-0.5/wrist-only-True/resnet_layer-3/color_jitter-True/checkpoints/policy_last.pt": 0,
    "/lucidxr/lucidxr/post_corl_2025/yajvan/8-18-25/pick_block_sim_real_cotrain/learn/2025/08/18/19-18-38/real-data-fraction-0.5/wrist-only-True/resnet_layer-3/color_jitter-False/checkpoints/policy_last.pt": 0,
    "/lucidxr/lucidxr/post_corl_2025/yajvan/8-18-25/pick_block_sim_real_cotrain/learn/2025/08/18/19-18-38/real-data-fraction-0.5/wrist-only-False/resnet_layer-4/color_jitter-True/checkpoints/policy_last.pt": 0,
    "/lucidxr/lucidxr/post_corl_2025/yajvan/8-18-25/pick_block_sim_real_cotrain/learn/2025/08/18/19-18-38/real-data-fraction-0.5/wrist-only-False/resnet_layer-4/color_jitter-False/checkpoints/policy_last.pt": 0,
    "/lucidxr/lucidxr/post_corl_2025/yajvan/8-18-25/pick_block_sim_real_cotrain/learn/2025/08/18/19-18-38/real-data-fraction-0.5/wrist-only-False/resnet_layer-3/color_jitter-True/checkpoints/policy_last.pt": 0,
    "/lucidxr/lucidxr/post_corl_2025/yajvan/8-18-25/pick_block_sim_real_cotrain/learn/2025/08/18/19-18-38/real-data-fraction-0.5/wrist-only-False/resnet_layer-3/color_jitter-False/checkpoints/policy_last.pt": 0,
    "/lucidxr/lucidxr/post_corl_2025/yajvan/8-18-25/pick_block_sim_real_cotrain/learn/2025/08/18/19-18-38/real-data-fraction-0.0/wrist-only-True/resnet_layer-4/color_jitter-True/checkpoints/policy_last.pt": 0,
    "/lucidxr/lucidxr/post_corl_2025/yajvan/8-18-25/pick_block_sim_real_cotrain/learn/2025/08/18/19-18-38/real-data-fraction-0.0/wrist-only-True/resnet_layer-4/color_jitter-False/checkpoints/policy_last.pt": 0,
    "/lucidxr/lucidxr/post_corl_2025/yajvan/8-18-25/pick_block_sim_real_cotrain/learn/2025/08/18/19-18-38/real-data-fraction-0.0/wrist-only-True/resnet_layer-3/color_jitter-True/checkpoints/policy_last.pt": 0,
    "/lucidxr/lucidxr/post_corl_2025/yajvan/8-18-25/pick_block_sim_real_cotrain/learn/2025/08/18/19-18-38/real-data-fraction-0.0/wrist-only-True/resnet_layer-3/color_jitter-False/checkpoints/policy_last.pt": 0,
    "/lucidxr/lucidxr/post_corl_2025/yajvan/8-18-25/pick_block_sim_real_cotrain/learn/2025/08/18/19-18-38/real-data-fraction-0.0/wrist-only-False/resnet_layer-4/color_jitter-True/checkpoints/policy_last.pt": 0,
    "/lucidxr/lucidxr/post_corl_2025/yajvan/8-18-25/pick_block_sim_real_cotrain/learn/2025/08/18/19-18-38/real-data-fraction-0.0/wrist-only-False/resnet_layer-4/color_jitter-False/checkpoints/policy_last.pt": 0,
    "/lucidxr/lucidxr/post_corl_2025/yajvan/8-18-25/pick_block_sim_real_cotrain/learn/2025/08/18/19-18-38/real-data-fraction-0.0/wrist-only-False/resnet_layer-3/color_jitter-True/checkpoints/policy_last.pt": 0,
    "/lucidxr/lucidxr/post_corl_2025/yajvan/8-18-25/pick_block_sim_real_cotrain/learn/2025/08/18/19-18-38/real-data-fraction-0.0/wrist-only-False/resnet_layer-3/color_jitter-False/checkpoints/policy_last.pt": 0,
}

if __name__ == "__main__":
    with Sweep(RUN, Unroll, ACT_Config) as sweep:

        Unroll.log_metrics = True
        Unroll.max_steps = 500
        # important
        Unroll.load_from_cache = False
        Unroll.overwrite = True
        Unroll.action_smoothing = True

        with sweep.product:
            Unroll.load_checkpoint = list(checkpoints.keys())
            with sweep.zip:
                Unroll.env_name = ["PickPlaceRobotRoom-single_random-v1",
                                   "PickPlaceRobotRoom-single_random-domain_rand-v2",
                                   "PickPlaceEval-single_random-gsplat-v1"]
                Unroll.image_keys = [
                    ["right/rgb", "wrist/rgb", "left/rgb"],
                    ["right/domain_rand", "wrist/domain_rand", "left/domain_rand"],
                    ["right/splat_rgb", "wrist/splat_rgb", "left/splat_rgb"],
                ]

            with sweep.zip:
                Unroll.seed = [*range(10)]
                Unroll.render = [True for _ in range(10)] + [False for _ in range(0)]  # only render 10% of the runs

    @sweep.each
    def tail(RUN, Unroll, ACT_Config):
        RUN.prefix, RUN.job_name, _ = RUN(
            script_path=__file__,
            job_name=f"{Unroll.env_name}/{checkpoints[Unroll.load_checkpoint]}/",
        )
        print(RUN.prefix)

    sweep.save(f"{Path(__file__).stem}.jsonl")

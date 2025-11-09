from jaynes import Jaynes
from params_proto.hyper import Sweep
from diffusion.train_policy_conditional import main

import jaynes
import zarr.core.sync as zsync
zsync.reset_resources_after_fork()

# jobs = Sweep.read("post_corl_2025/yajvan/9-14-25/utensil_drawer_mujoco_dunet/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-14-25/microwave_muffin_mujoco_dunet/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-14-25/mug_tree_mujoco_dunet/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-14-25/ball_toy_mujoco_dunet/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-14-25/pour_liquid_mujoco_dunet/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-14-25/tie_knot_mujoco_dunet/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-14-25/pick_block_mujoco_dunet/learn.jsonl")

# jobs = Sweep.read("post_corl_2025/yajvan/9-14-25/utensil_drawer_mujoco_dit/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-14-25/microwave_muffin_mujoco_dit/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-14-25/mug_tree_mujoco_dit/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-14-25/ball_toy_mujoco_dit/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-14-25/pour_liquid_mujoco_dit/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-14-25/tie_knot_mujoco_dit/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-14-25/pick_block_mujoco_dit/learn.jsonl")


# jobs = Sweep.read("post_corl_2025/yajvan/9-15-25/utensil_drawer_mujoco_dunet/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-15-25/microwave_muffin_mujoco_dunet/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-15-25/mug_tree_mujoco_dit/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-14-25/ball_toy_mujoco_dit/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-15-25/pour_liquid_mujoco_dunet/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-15-25/tie_knot_mujoco_dit/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-15-25/pick_block_mujoco_dit/learn.jsonl")

# jobs = Sweep.read("post_corl_2025/yajvan/9-16-25/pour_liquid_mujoco_dunet/learn.jsonl")
jobs = Sweep.read("post_corl_2025/yajvan/9-17-25/ball_toy_mujoco_dunet/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-17-25/microwave_muffin_mujoco_dunet/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-17-25/utensil_drawer_mujoco_dunet/learn.jsonl")
jobs = Sweep.read("post_corl_2025/yajvan/9-18-25/ball_toy_mujoco_dunet/learn.jsonl")
jobs = Sweep.read("post_corl_2025/yajvan/9-18-25/utensil_drawer_mujoco_dunet/learn.jsonl")
jobs = Sweep.read("post_corl_2025/yajvan/9-18-25/microwave_muffin_mujoco_dunet/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-18-25/pour_liquid_mujoco_dunet/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-18-25/ball_toy_lucid_dunet/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-18-25/tie_knot_mujoco_dunet/learn.jsonl")

# jobs = Sweep.read("post_corl_2025/yajvan/9-19-25/utensil_drawer_mujoco_dunet/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-19-25/tie_knot_mujoco_dunet/learn.jsonl")
jobs = Sweep.read("post_corl_2025/yajvan/9-19-25/ball_toy_lucid_dunet/learn.jsonl")
jobs = Sweep.read("post_corl_2025/yajvan/9-19-25/pour_liquid_mujoco_dunet_muon/learn.jsonl")
jobs = Sweep.read("post_corl_2025/yajvan/9-19-25/ball_toy_lucid_dit/learn.jsonl")
jobs = Sweep.read("post_corl_2025/yajvan/9-20-25/ball_toy_lucid_dit/learn.jsonl")
jobs = Sweep.read("post_corl_2025/yajvan/9-20-25/microwave_muffin_mujoco_dunet/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-20-25/ball_toy_mujoco_dunet/learn.jsonl")
jobs = Sweep.read("post_corl_2025/yajvan/9-20-25/pour_liquid_mujoco_dunet/learn.jsonl")
jobs = Sweep.read("post_corl_2025/yajvan/9-21-25/mug_tree_lucid_dunet/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-21-25/microwave_muffin_mujoco_dunet/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-21-25/ball_toy_lucid_dunet/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-21-25/pick_place_lucid_dunet/learn.jsonl")
jobs = Sweep.read("post_corl_2025/yajvan/9-21-25/microwave_muffin_lucid_dunet/learn.jsonl")
jobs = Sweep.read("post_corl_2025/yajvan/9-22-25/tie_knot_lucid_dunet/learn.jsonl")
jobs = Sweep.read("post_corl_2025/yajvan/9-22-25/utensil_drawer_lucid_unet/learn.jsonl")
jobs = Sweep.read("post_corl_2025/yajvan/9-22-25/microwave_muffin_lucid_dunet/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-22-25/microwave_muffin_lucid_dit/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-22-25/mug_tree_lucid_dit/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-22-25/ball_toy_lucid_dit/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-22-25/pick_place_lucid_dit/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-22-25/utensil_drawer_lucid_dit/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-22-25/tie_knot_lucid_dit/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-22-25/mug_tree_lucid_dunet_augmentation/learn.jsonl")
jobs = Sweep.read("post_corl_2025/yajvan/9-22-25/mug_tree_ddpm_trial/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-22-25/ball_toy_lucid_dunet/learn.jsonl")
jobs = Sweep.read("post_corl_2025/yajvan/9-22-25/mug_tree_ddpm_lucid/learn.jsonl")
jobs = Sweep.read("post_corl_2025/yajvan/9-23-25/microwave_muffin/learn.jsonl")
jobs = Sweep.read("post_corl_2025/yajvan/9-23-25/utensil_drawer/learn.jsonl")
jobs = Sweep.read("post_corl_2025/yajvan/9-26-25/microwave_muffin/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-26-25/utensil_drawer/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-26-25/microwave_muffin_lucid/learn.jsonl")
jobs = Sweep.read("post_corl_2025/yajvan/9-26-25/microwave_muffin_v2/learn.jsonl")
# jobs = Sweep.read("post_corl_2025/yajvan/9-26-25/microwave_muffin_lucid_transformer/learn.jsonl")

for jid, job in enumerate(jobs):
    print(f"running {job}")
    Jaynes.runner_config = None
    jaynes.config(mode="train", runner=dict(name=f"trainer-{jid}"),
                  config_path="../.jaynes_fortyfive.yml")
    # jaynes.config(mode="local")
    jaynes.add(
        main,
        job,
        # prune_local_cache=True,
    )
    # break


jaynes.execute()
jaynes.listen()

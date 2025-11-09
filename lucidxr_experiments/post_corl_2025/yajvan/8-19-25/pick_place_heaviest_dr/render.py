import jaynes
from jaynes import Jaynes
from dotvar import auto_load  # noqa

from lucidxr.traj_samplers.process_steps.render_worker import mujoco_render_entrypoint
import time

from vuer_mujoco.wrappers.domain_randomization_wrapper import DEFAULT_COLOR_ARGS


def keep_retrying(fn):
    """Decorator to keep retrying a function until it succeeds."""

    def wrapper(*args, **kwargs):
        while True:
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                print(f"Error: {e}. Retrying...")
                time.sleep(1.0)

    return wrapper

DEFAULT_COLOR_ARGS["randomize_local_geom_prefixes"] = ["box", "goal-area"]
DEFAULT_COLOR_ARGS["local_rgb_interpolation"] = 0.6


DEFAULT_CAMERA_ARGS = {
    "camera_names": ["left", "right", "wrist"],  # all cameras are randomized #TODO Hardcoded for now
    "randomize_position": True,
    "randomize_rotation": True,
    "randomize_fovy": True,
    "position_perturbation_size": 0.015,
    "rotation_perturbation_size": 0.09,
    "fovy_perturbation_size": 5.0,
}

DEFAULT_LIGHTING_ARGS = {
    "light_idxs": None,  # all lights are randomized
    "randomize_position": True,
    "randomize_direction": True,
    "randomize_specular": True,
    "randomize_ambient": True,
    "randomize_diffuse": True,
    "randomize_active": True,
    "position_perturbation_size": 0.3,
    "direction_perturbation_size": 0.9,
    "specular_perturbation_size": 0.3,
    "ambient_perturbation_size": 0.3,
    "diffuse_perturbation_size": 0.3,
}

config = dict(
    name="pick_place_robot_room",
    env_name="PickPlaceRobotRoom-single_random-domain_rand-v1",
    camera_keys=["wrist/domain_rand", "left/domain_rand", "right/domain_rand"],
    multiplicity=5,
    env_args=dict(
        color_randomization_args = DEFAULT_COLOR_ARGS,
        camera_randomization_args = DEFAULT_CAMERA_ARGS,
        lighting_randomization_args = DEFAULT_LIGHTING_ARGS,
    ),
)


demo_prefix = "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/pick_place_robot_room/2025/08/07/15.58.28/"
demo_ep_start = 1
demo_ep_end = 125

num_render_workers = 60
render_worker_chain_length = 6
overwrite = True

from zaku import TaskQ

mujoco_queue_name = "yravan:lucidxr:mujoco-queue-1"
mujoco_queue = TaskQ(name=mujoco_queue_name)
mujoco_queue.clear_queue()

for i in range(demo_ep_start, demo_ep_end + 1):
    mujoco_queue.add(
        dict(
            ep_ind=i,
            demo_prefix=demo_prefix.format(**config),
            **config,
            overwrite=overwrite,
            lucid_mode=False,
            dry_run=False,
        )
    )
print(f"{mujoco_queue.count()} jobs added to {mujoco_queue_name} queue.")
# exit()
# exit()
Jaynes.runner_config = None
for i in range(1, num_render_workers + 1, render_worker_chain_length):
    jaynes.config(mode="render", runner=dict(name=f"render_worker-{i}"))

    job = jaynes.add(
        keep_retrying(mujoco_render_entrypoint),
        queue_name=mujoco_queue_name,
    )

    for j in range(1, render_worker_chain_length):
        if i + j <= num_render_workers:
            job = job.chain(
                keep_retrying(mujoco_render_entrypoint),
                queue_name=mujoco_queue_name,
            )

jaynes.execute()
jaynes.listen()

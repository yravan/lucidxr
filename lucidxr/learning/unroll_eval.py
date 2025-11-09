import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
import torchvision.transforms
from dotvar import auto_load  # noqa
from ml_logger import logger, ML_Logger
from params_proto import Flag, Proto, PrefixProto
from torchvision.transforms import InterpolationMode
from tqdm import trange

from diffusion.ddpm.policy_ddpm import DDPMPolicy
from diffusion.models.policy import DiffusionPolicyArgs
from lucidxr.learning.act_config import ACT_Config
from lucidxr.learning.models.detr_vae import reparametrize
from lucidxr.learning.utils import set_seed
from lucidxr.learning.models.policy import ACTPolicy
from lucidxr.learning.playback_policy import PlaybackPolicy
from vuer_mujoco.tasks import make

from vuer_mujoco.schemas.se3.rot_gs6 import quat2gs6
import time

PROJECT_ROOT = Path(__file__).parent.parent.parent
# print("CUDA available:", torch.cuda.is_available())


def get_metrics(loader, path):
    metrics = loader.read_metrics(
        "success",
        path=path,
        num_bins=1,
    )

    succ = np.array(metrics.str[0].tolist())
    return succ.mean(), len(succ)


def log_state(logger, env, policy, observation, cam_views, step):
    """
    Log the current state of the environment and policy at a given step.
    """

    for _ in range(1):
        action_1, *_ = policy(observation=observation, cam_views=cam_views)
        action_2, *_ = policy(observation=observation, cam_views=cam_views)
        action_1 = action_1.flatten()[: ACT_Config.action_dim]
        action_2 = action_2.flatten()[: ACT_Config.action_dim]
        print(torch.max(torch.abs(action_1 - action_2)))

    physics = env.unwrapped.env.physics
    qpos = physics.data.qpos.ravel()
    qvel = physics.data.qvel.ravel()

    # Compute deterministic action
    with torch.no_grad():
        action, *_ = policy(observation=observation, cam_views=cam_views)
        action = action.flatten()[: ACT_Config.action_dim]

    # Convert obs and action to numpy arrays
    obs_np = observation.cpu().numpy().ravel() if hasattr(observation, "cpu") else observation.ravel()
    action_np = action.cpu().numpy().ravel() if hasattr(action, "cpu") else action.ravel()

    # Format cam_views: fixed chunk from each image
    cam_view_snippets = {}
    for key, img in cam_views.items():
        img_np = img.cpu().numpy() if hasattr(img, "cpu") else img
        snippet = img_np[:, :2, :2]  # 2x2 patch from top-left corner
        cam_view_snippets[key] = snippet.tolist()

    # Parameter summary
    param_summary = []
    total_sum = 0.0
    total_count = 0
    for name, param in policy.named_parameters():
        param_data = param.detach().cpu().numpy()
        layer_sum = float(param_data.sum())
        layer_count = param_data.size
        param_summary.append(f"{name}: sum={layer_sum:.4f}, mean={layer_sum / layer_count:.6f}")
        total_sum += layer_sum
        total_count += layer_count

    # Assemble log string
    log_str = (
        f"\nStep {step}\n"
        f"{'-' * 60}\n"
        f"qpos:   [{', '.join(f'{v:.6f}' for v in qpos)}]\n"
        f"qvel:   [{', '.join(f'{v:.6f}' for v in qvel)}]\n"
        f"obs:    [{', '.join(f'{v:.6f}' for v in obs_np)}]\n"
        f"action: [{', '.join(f'{v:.6f}' for v in action_np)}]\n"
        f"cam_view snippets:\n"
    )

    for key, snippet in cam_view_snippets.items():
        log_str += f"  {key}: {snippet}\n"

    log_str += "\nModel parameter summary (layer-wise sums):\n"
    log_str += "\n".join(param_summary[:10])  # limit to first 10 layers
    log_str += f"\nTOTAL PARAM SUM: {total_sum:.4f} | MEAN: {total_sum / total_count:.6f}\n"
    log_str += "-" * 60

    logger.print(log_str)


def _resolve_loader(default) -> tuple["ML_Logger", bool]:
    """
    Returns (loader, is_cache_hit)
    - Try cache first if enabled.
    - Fall back to checkpoint_host or default `logger`.
    """
    if UnrollEval.load_from_cache:
        cache_loader = ML_Logger(root=UnrollEval.cache_root)
        if cache_loader.glob(UnrollEval.load_checkpoint.lstrip("/")):  # remove leading slash for local paths
            return cache_loader, True  # ✓ found in cache
        print("Cached checkpoint not found; falling back to server.")

    if UnrollEval.checkpoint_host:
        return ML_Logger(root=UnrollEval.checkpoint_host), False

    return default, False  # default loader


def img_to_tensor(img):
    img_tensor = torch.Tensor(img / 255.0).float().permute(2, 0, 1)[None, ...]
    interp_mode = InterpolationMode.BILINEAR if ACT_Config.downsample_images > 1 else InterpolationMode.NEAREST
    img_tensor = torchvision.transforms.functional.resize(img_tensor, 360 // ACT_Config.downsample_images,interpolation=interp_mode)
    if ACT_Config.blur_images:
        img_tensor = torchvision.transforms.functional.gaussian_blur(img_tensor, kernel_size=5)
    return img_tensor



class UnrollEval(PrefixProto, cli_parse=False):
    env_name: str = "Pick_block-v1"

    ### ckpt params
    checkpoint_host = Proto(help="host for the data loader. Default is escher.", default="http://escher.csail.mit.edu:4000")
    load_checkpoint = Proto(str, help="Path to the model checkpoint")
    overwrite = Proto(False, help="overwrite the checkpoint if it exists")
    results_file = Proto("episode_metrics.pkl", help="file to save the results to")
    num_evals = Proto(1, help="number of evaluations to run")

    eval_ema = Flag("evaluate the ema weights of the model", default=False)

    verbose = Flag("Print verbose output during evaluation.", default=False)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    policy: str = 'act'
    load_from_cache = Flag("load the policy from the cache. If it doesn't exist yet, it will download")
    cache_root = Proto(PROJECT_ROOT / ".cache", env="LUCIDXR_CACHE")


    strict = Flag("During registration, raise an error if the environment is already registered.", default=True)

    seed = 101
    max_steps = 1000
    action_smoothing = Flag("smooth the actions with a moving average filter.", default=True)
    train_step = Proto(None, help="the training step to use for the evaluation")

    render = Flag("render the video of the evaluation.", default=True)
    log_metrics = Flag("log metrics to logging server. mainly used for experiment metrics")

    show_images = Flag("show images in the window.")
    image_keys = Proto(["wrist/rgb", "left/rgb", "front/rgb"], help="camera keys to use for the action.")


def plot_images(obs, action_history):
    plt.figure(figsize=[7, 4])
    # action.shape
    plt.subplot(221)
    plt.title("mocap-Z")
    plt.plot([a[2] for a in action_history])

    plt.subplot(222)
    if "wrist/rgb" in obs:
        plt.imshow(obs["wrist/rgb"])
    elif "wrist/depth" in obs:
        plt.imshow(obs["wrist/depth"])
    plt.title("wrist")
    plt.axis("off")

    plt.subplot(223)
    if "left/rgb" in obs:
        plt.imshow(obs["left/rgb"])
    elif "left/depth" in obs:
        plt.imshow(obs["left/depth"])
    plt.title("left")
    plt.axis("off")

    plt.subplot(224)
    if "right/rgb" in obs:
        plt.imshow(obs["right/rgb"])
    elif "right/depth" in obs:
        plt.imshow(obs["right/depth"])
    plt.title("right")
    plt.axis("off")

    plt.tight_layout()
    plt.show()

def preprocess_cam_views(obs):
    cam_views = {}
    for cam_key in UnrollEval.image_keys:
        if cam_key in obs:
            key_name = re.sub(r"splat_rgb-.*", "rgb", cam_key)
            key_name = key_name.replace("domain_rand", "rgb")
            cam_views[key_name] = img_to_tensor(obs[cam_key]).to(UnrollEval.device)
    return cam_views


class ActionGenerator:
    def __init__(self, policy):
        self.policy = policy
        if UnrollEval.action_smoothing:
            self.action_buffer = torch.full((ACT_Config.chunk_size, ACT_Config.chunk_size, ACT_Config.action_dim), float("nan"))
        self.current_chunk = None
        self.step = None
        self.prev_chunk = reparametrize(
            torch.zeros((ACT_Config.chunk_size, ACT_Config.action_dim)), torch.ones((ACT_Config.chunk_size, ACT_Config.action_dim))
        ).to(UnrollEval.device)
        self.is_pad = torch.zeros((ACT_Config.chunk_size), dtype=torch.bool, device=UnrollEval.device)

    def __call__(self, obs, **kwargs):
        with torch.inference_mode():
            return self.get_action(obs, **kwargs)

    def get_action(self, obs, **kwargs):
        if UnrollEval.action_smoothing or self.current_chunk is None or self.step >= (ACT_Config.chunk_size - 1):
            observation = torch.Tensor(obs["state"][None, ...]).to(UnrollEval.device)
            obs = {k: v[..., None] if k.endswith("depth") else v for k, v in obs.items()}
            cam_views = preprocess_cam_views(obs)
            action, *_, metrics = self.policy(
                observation=observation, cam_views=cam_views, **kwargs
            )
            # print(metrics)
            if action is None:
                return None
            self.step = 0
            self.current_chunk = action.squeeze()
        else:
            self.step += 1
        if UnrollEval.action_smoothing:
            if self.action_buffer.isnan().all():
                self.action_buffer[:] = self.current_chunk.unsqueeze(0).repeat(ACT_Config.chunk_size, 1, 1)
            else:
                self.action_buffer[:-1, :-1] = self.action_buffer[1:, 1:]  # shift buffer & timesteps
                self.action_buffer[-1] = self.current_chunk

            exponential_weights = torch.exp(-torch.arange(ACT_Config.chunk_size).float() * ACT_Config.action_weighting_factor)
            self.current_chunk = (self.action_buffer * exponential_weights[:, None, None] / exponential_weights.sum()).sum(dim=0)
        self.prev_chunk = self.current_chunk.to(UnrollEval.device)

        return self.current_chunk[self.step].cpu().numpy().squeeze(), self.current_chunk.cpu().numpy().squeeze()


class DiffusionActionGenerator:
    def __init__(self, policy, action_len):
        self.policy = policy
        self.action_len = 12 # HARDCODED
        self.policy.eval()
        self.observation_buffer = torch.full((DiffusionPolicyArgs.history_length, DiffusionPolicyArgs.obs_dim), float("nan")).to(UnrollEval.device)
        self.current_chunk = None
        self.step = None

    def __call__(self, obs, **kwargs):
        with torch.inference_mode():
            return self.get_action(obs, **kwargs)

    def get_action(self, obs, **_):
        if self.current_chunk is None or self.step >= (self.action_len - 1):
            observation = torch.Tensor(obs["state"][None, ...]).to(UnrollEval.device)
            if self.observation_buffer.isnan().all():
                self.observation_buffer[:] = observation.repeat(DiffusionPolicyArgs.history_length, 1)
            else:
                self.observation_buffer[:-1] = self.observation_buffer[1:]
                self.observation_buffer[-1] = observation
            observation = self.observation_buffer.flatten()[None, ...]
            cam_views = preprocess_cam_views(obs)
            actions = self.policy.predict_action(
                batch_size=1,
                device=UnrollEval.device,
                obs_prop=observation,
                camera_views=cam_views,
            )
            self.step = 0
            self.current_chunk = actions.squeeze()
        else:
            self.step += 1

        return self.current_chunk[self.step].cpu().numpy().squeeze(), None


def load_policy(_deps=None, **deps):
    if UnrollEval.policy == "playback":
        policy = PlaybackPolicy(UnrollEval.load_checkpoint, verbose=UnrollEval.verbose)
    else:
        assert UnrollEval.policy in ["act", "diffusion"], "policy must be either 'act' or 'diffusion'"
        default_loader = logger if UnrollEval.checkpoint_host is None else ML_Logger(root=UnrollEval.checkpoint_host)
        loader, from_cache = _resolve_loader(default=default_loader)

        load_path = (UnrollEval.load_checkpoint.lstrip("/") if from_cache else UnrollEval.load_checkpoint)
        if UnrollEval.eval_ema:
            load_path = load_path.replace(".pt", "_ema.pt")
        print(f"Loading '{load_path}' from {loader.root}")

          # remove leading slash for local paths
        state_dict = loader.load_torch(
            load_path,
            weights_only=False,
            map_location=torch.device(UnrollEval.device),
        )
        logger = ML_Logger(prefix=Path("/" + load_path if from_cache else load_path).parent.parent)
        if UnrollEval.policy == "act":
            params = logger.load_pkl("parameters.pkl")[0]["ACT_Config"]

            ACT_Config._update(**params)
            for i, key in enumerate(ACT_Config.image_keys):
                ACT_Config.image_keys[i] = key.replace("lucid", "rgb")
                ACT_Config.image_keys[i] = ACT_Config.image_keys[i].replace("domain_rand", "rgb")
            policy = ACTPolicy()
        else:
            from diffusion.models.policy import build_diffusion_policy, DiffusionPolicyArgs
            try:
                params = logger.load_pkl("parameters.pkl")[0]["DiffusionPolicyArgs"]
            except KeyError:
                print("No DiffusionPolicyArgs found in parameters.pkl, not updating")
                params = {}

            DiffusionPolicyArgs._update(**params)
            for i, key in enumerate(DiffusionPolicyArgs.image_keys):
                DiffusionPolicyArgs.image_keys[i] = key.replace("lucid", "rgb")
                DiffusionPolicyArgs.image_keys[i] = DiffusionPolicyArgs.image_keys[i].replace("domain_rand", "rgb")

            if DiffusionPolicyArgs.score_net == "unet" or DiffusionPolicyArgs.score_net == "causal_transformer":
                policy = build_diffusion_policy()
            elif DiffusionPolicyArgs.score_net == "ddpm_transformer":
                policy = DDPMPolicy(
                    act_dim=DiffusionPolicyArgs.action_dim,
                    seq_len=DiffusionPolicyArgs.chunk_size,
                    obs_dim=DiffusionPolicyArgs.obs_dim,
                    image_keys=DiffusionPolicyArgs.image_keys,
                    vision_dim=DiffusionPolicyArgs.vis_dim,
                    d_model=DiffusionPolicyArgs.transformer_hidden_size,
                    depth=DiffusionPolicyArgs.transformer_depth,
                    num_heads=DiffusionPolicyArgs.transformer_num_heads,
                    mlp_ratio=DiffusionPolicyArgs.transformer_mlp_ratio,
                    T=DiffusionPolicyArgs.ddpm_timesteps,
                    dropout=DiffusionPolicyArgs.transformer_dropout,
                    schedule="cosine",
                )

        if UnrollEval.load_from_cache and not from_cache:
            # lazily create the cache loader if we didn’t already
            cache_loader = ML_Logger(root=UnrollEval.cache_root)
            cache_loader.torch_save(
                state_dict,
                UnrollEval.load_checkpoint.lstrip("/"),
            )

            print(f"Wrote checkpoint back to cache at {cache_loader.root}")

        if UnrollEval.policy == "diffusion":
            # for ema
            state_dict = {k.replace("module.", ""): v for k, v in state_dict.items()}
            state_dict = {k.replace("lucid", "rgb"): v for k, v in state_dict.items()}
            state_dict = {k.replace("domain_rand", "rgb"): v for k, v in state_dict.items()}
            state_dict.pop("n_averaged", None)

        policy.load_state_dict(state_dict, strict=True)
        print("loaded from the checkpoint", UnrollEval.load_checkpoint)

        policy.to(UnrollEval.device)
        policy.eval()

    return policy


def main(_deps=None, **deps):
    from params_proto import ARGS

    ARGS.parse_args()

    from ml_logger import logger

    from lucidxr_experiments import RUN

    UnrollEval._update(_deps, **deps)
    ACT_Config._update(_deps, **deps)
    set_seed(UnrollEval.seed)
    if UnrollEval.policy == "diffusion":
        from diffusion.models.policy import DiffusionPolicyArgs

        DiffusionPolicyArgs._update(_deps, **deps)

    # validation
    assert UnrollEval.load_checkpoint is not None, "Checkpoint not found"

    try:
        RUN._update(_deps, **deps)
        if "file_stem" in deps and "job_name" in deps:
            ckpt = f"lucidxr/lucidxr/{deps['file_stem']}/{deps['job_name']}"
        else:
            ckpt = RUN.prefix
        logger.configure(ckpt)
    except KeyError:
        pass

    if UnrollEval.overwrite:
        logger.remove(UnrollEval.results_file)

    # logger.prefix = UnrollEval.logging_prefix
    # logger.job_started(
    #     TrainArgs=vars(UnrollEval),
    #     ACT_Config=vars(ACT_Config) if UnrollEval.policy == "act" else None,
    #     DiffusionPolicyArgs=vars(DiffusionPolicyArgs) if UnrollEval.policy == "diffusion" else None,
    # )
    logger.print(
        vars(UnrollEval),
        vars(ACT_Config) if UnrollEval.policy == "act" else None,
        vars(DiffusionPolicyArgs) if UnrollEval.policy == "diffusion" else None,
    )
    if UnrollEval.policy == "diffusion":
        DiffusionPolicyArgs.sampling_method="pc" # HARCODED
    print("Logging results at", logger.get_dash_url())

    logger.upload_file(__file__)

    print("Training started", logger.get_dash_url())
    prefix = ""
    if UnrollEval.train_step:
        prefix = f"eval/step_{UnrollEval.train_step}/"

    env = make(UnrollEval.env_name, strict=UnrollEval.strict, terminate_on_success=True)

    ACT_Config.normalize_obs = True
    ACT_Config.normalize_actions = True

    policy = load_policy()
    if UnrollEval.policy == "diffusion":
        action_generator = DiffusionActionGenerator(policy, DiffusionPolicyArgs.action_len)
    else:
        action_generator = ActionGenerator(policy)

    logger.split("episode")

    obs, done = env.reset(), False
    prev_action = obs["state"]

    action_history = []


    if UnrollEval.show_images:
        plot_images(obs, action_history)

    if UnrollEval.render:
        logger.remove(f"{prefix}renders_{UnrollEval.seed}/")

    # evaluating on validation sets
    pbar = trange(UnrollEval.max_steps)
    positions = {"mocap_pos": [obs['state']]}
    for step in pbar:
        action, _ = action_generator(obs)
        if ACT_Config.delta_space:
            action = action + prev_action
            prev_action = action
        if action is None:  # when using playback policy
            break
        action_history.append(action)

        if UnrollEval.verbose:
            print(f"Unroll Step {step}: action={action}, obs={obs['state']}")
            print(f"Frame: qpos:{env.unwrapped.env.physics.data.qpos}")
        obs, reward, done, info = env.step(action)
        positions["mocap_pos"].append(obs['state'])

        full_image = np.concatenate([obs[k] for k in UnrollEval.image_keys if k in obs], axis=1)
        if UnrollEval.render:
            logger.save_image(full_image, f"{prefix}renders_{UnrollEval.env_name}_{UnrollEval.seed}/frame-{step:05d}.png")

        if UnrollEval.show_images:
            plot_images(obs, action_history)

        if done:
            pbar.write("episode has completed.")
            break

    logger.save_pkl(positions, "data/rollout.pkl")

    episodic_metrics = env.unwrapped.env.task.get_metrics()
    if UnrollEval.log_metrics:
        with logger.Sync():
            logger.save_pkl(episodic_metrics, UnrollEval.results_file, append=True)
            if UnrollEval.train_step is not None:
                mean, num = get_metrics(logger, UnrollEval.results_file)
                if num == UnrollEval.num_evals:
                    logger.remove(UnrollEval.load_checkpoint)
                    logger.remove(UnrollEval.load_checkpoint[:3] + "_ema.pt")
                    logger.remove(UnrollEval.results_file)
                    file = UnrollEval.cache_root / UnrollEval.load_checkpoint.lstrip("/")
                    file.unlink(missing_ok=True)
                    logger.log(metrics={"success_rate": mean}, step=UnrollEval.train_step, flush=True)
                    logger.flush()

    logger.print(episodic_metrics)

    status = "success" if episodic_metrics["success"] else "failure"
    if reward < 0:
        status = "crash"

    if UnrollEval.render:
        # clean up afterward
        logger.make_video(
            f"{prefix}renders_{UnrollEval.env_name}_{UnrollEval.seed}/frame-*.png",
            f"{prefix}multiview_{UnrollEval.env_name}_{UnrollEval.seed}_{status}.mp4",
            fps=30,
        )
        logger.remove(f"{prefix}renders_{UnrollEval.env_name}_{UnrollEval.seed}/")


if __name__ == "__main__":
    main(
        {
            "UnrollEval.checkpoint_host": "http://escher.csail.mit.edu:4000",
            "UnrollEval.render": True,
            "UnrollEval.log_metrics": True,
            "UnrollEval.max_steps": 4_00,
            "UnrollEval.load_from_cache": False,
            "UnrollEval.env_name": "MugTree-mug_rand-v1",
            # "UnrollEval.image_keys": ["wrist/rgb", "stereo_left/rgb", "stereo_right/rgb"],
            "UnrollEval.image_keys": ["wrist/rgb", "left/rgb", "right/rgb"],
            # "UnrollEval.load_checkpoint":"/lucidxr/lucidxr/post_corl_2025/yajvan/9-19-25/../9-14-25/mug_tree_mujoco_dunet/learn/2025/09/14/02-13-06/unet/wrist-only/300/checkpoints/policy_latest.pt",
            "UnrollEval.load_checkpoint": "/lucidxr/lucidxr/post_corl_2025/yajvan/9-19-25/../9-10-25/dit_test_lucid/learn/2025/09/10/23-05-55/ema/dataset-5/100/checkpoints/policy_latest.pt",
            "UnrollEval.seed": 52,
            "UnrollEval.action_smoothing": True,
            "UnrollEval.policy": "diffusion",
            # "UnrollEval.show_images": True,
            # 'UnrollEval.dry_run': True,
            "UnrollEval.eval_ema": True,
            # "DiffusionPolicyArgs.channels": [64, 128, 256, 512],
            # "DiffusionPolicyArgs.chunk_size": 24,
            "DiffusionPolicyArgs.image_keys": ["wrist/rgb"],
            # "DiffusionPolicyArgs.vis_dim": 1024,
            # "DiffusionPolicyArgs.action_len": 12,
            # "DiffusionPolicyArgs.embed_dim": 128,
            # "ACT_Config.action_weighting_factor": 0.1,
            "device": "mps",
        },
        strict=False,
    )

    # main(
    #     {
    #         "UnrollEval.checkpoint_host": "http://escher.csail.mit.edu:4000",
    #         "UnrollEval.render": True,
    #         "UnrollEval.log_metrics": True,
    #         "UnrollEval.max_steps": 600,
    #         "UnrollEval.load_from_cache": False,
    #         # "UnrollEval.env_name": "MugTree-fixed-v1",
    #         "UnrollEval.env_name": "UtensilDrawer-Random-v1",
    #         # "UnrollEval.env_name": "MicrowaveMuffin-Random-v1",
    #         "UnrollEval.image_keys": ["front/rgb", "front_r/rgb", "wrist/rgb"],
    #         # "UnrollEval.image_keys": ["wrist/rgb"],
    #         # "UnrollEval.image_keys": ["right/rgb", "wrist/rgb", "left/rgb"],
    #         "UnrollEval.policy": "diffusion",
    #         # "UnrollEval.load_checkpoint": "/lucidxr/compositional-sculpting-playground/alan_debug/mug_tree_random_grasps_v2/2025/07/31/14-17-47/lr-1e-03-1e-05/wd-0e+00/vis_dim-512/image_keys-['wrist/rgb']/chunk_size-48/seed-100/checkpoints/latest.pth",
    #         # "UnrollEval.load_checkpoint": "/lucidxr/compositional-sculpting-playground/alan_debug/mug_tree_random_location_fixed_grasp_v1/2025/08/04/12-48-09/lr-1e-03-1e-05/wd-0e+00/vis_dim-512/image_keys-['wrist/rgb']/chunk_size-48/dataset_2/seed-100/checkpoints/latest_ema.pth",
    #         # "UnrollEval.load_checkpoint": "/lucidxr/compositional-sculpting-playground/alan_debug/mug_tree_random_grasps_v2/2025/08/28/23-36-47/lr-1e-03-1e-05/wd-0e+00/vis_dim-512/image_keys-['wrist/rgb']/chunk_size-48/seed-100/checkpoints/latest.pth",
    #         # "UnrollEval.load_checkpoint": "/lucidxr/compositional-sculpting-playground/alan_debug/mug_tree_random_grasps_v2/2025/08/29/00-28-42/lr-1e-03-1e-05/wd-0e+00/vis_dim-512/image_keys-['wrist/rgb']/chunk_size-48/seed-100/checkpoints/latest.pth",
    #         # "UnrollEval.load_checkpoint": "/lucidxr/compositional-sculpting-playground/alan_debug/mug_tree_random_grasps_v2/2025/07/31/14-17-47/lr-1e-03-1e-05/wd-0e+00/vis_dim-512/image_keys-['right/rgb', 'wrist/rgb', 'left/rgb']/chunk_size-48/seed-100/checkpoints/latest.pth",
    #         # "UnrollEval.load_checkpoint": "/lucidxr/compositional-sculpting-playground/alan_debug/utensil_drawer_v0/2025/08/29/00-40-46/lr-1e-03-1e-05/image_keys-['front/rgb', 'front_r/rgb', 'wrist/rgb']/chunk_size-48/seed-100/checkpoints/latest.pth",
    #         # "UnrollEval.load_checkpoint": "/lucidxr/compositional-sculpting-playground/alan_debug/microwave_muffin_v1_gripper/2025/09/01/13-54-43/lr-1e-03-1e-05/image_keys-['front/rgb', 'front_r/rgb', 'wrist/rgb']/chunk_size-48/seed-100/checkpoints/latest.pth",
    #         # "UnrollEval.load_checkpoint": "/lucidxr/compositional-sculpting-playground/alan_debug/utensil_drawer_v0_new_code/2025/09/01/14-56-53/lr-1e-03-1e-05/image_keys-['front/rgb', 'front_r/rgb', 'wrist/rgb']/chunk_size-48/seed-200/checkpoints/policy_latest.pt",
    #         # "UnrollEval.load_checkpoint": "/lucidxr/compositional-sculpting-playground/alan_debug/microwave_muffin_v1_gripper_new_code/2025/09/01/14-56-55/lr-1e-03-1e-05/image_keys-['front/rgb', 'front_r/rgb', 'wrist/rgb']/chunk_size-48/seed-100/checkpoints/policy_latest.pt",
    #         "UnrollEval.load_checkpoint": "/lucidxr/compositional-sculpting-playground/alan_debug/utensil_drawer_v0_new_code/2025/09/02/15-36-17/lr-1e-03-1e-05/image_keys-['front/rgb', 'front_r/rgb', 'wrist/rgb']/chunk_size-48/seed-100/checkpoints/policy_latest.pt",
    #         "UnrollEval.seed": 52,
    #         "DiffusionPolicyArgs.chunk_size": 48,
    #         "DiffusionPolicyArgs.channels": [64, 128, 256, 512],
    #         "DiffusionPolicyArgs.image_keys": ["front/rgb", "front_r/rgb", "wrist/rgb"],
    #         "DiffusionPolicyArgs.backbone": "cnn",
    #         # "DiffusionPolicyArgs.image_keys": ["wrist/rgb"],
    #         # "DiffusionPolicyArgs.image_keys": ["right/rgb", "wrist/rgb", "left/rgb"],
    #         "DiffusionPolicyArgs.action_dim": 10,
    #         "DiffusionPolicyArgs.obs_dim": 10,
    #         "DiffusionPolicyArgs.vis_dim": 512,
    #     },
    # )
    # main(
    #     {
    #         "UnrollEval.checkpoint_host": "http://escher.csail.mit.edu:4000",
    #         "UnrollEval.render": True,
    #         "UnrollEval.log_metrics": True,
    #         "UnrollEval.max_steps": 400,
    #         "UnrollEval.load_from_cache": True,
    #         "UnrollEval.env_name": "PickPlaceRobotRoom-single_random-v1",
    #         "UnrollEval.image_keys": ["wrist/rgb", "left/rgb", "right/rgb"],
    #         "UnrollEval.load_checkpoint":"/lucidxr/lucidxr/post_corl_2025/yajvan/8-26-25/diffusion-policy-test/learn/2025/08/26/12-02-10/wrist-only/embed_dim-128/checkpoints/latest.pth",
    #         "UnrollEval.seed": 0,
    #         "UnrollEval.action_smoothing": True,
    #         "UnrollEval.policy": "diffusion",
    #         "UnrollEval.show_images": False,
    #         "DiffusionPolicyArgs.channels": [64, 128, 256, 512],
    #         "DiffusionPolicyArgs.chunk_size": 24,
    #         "DiffusionPolicyArgs.image_keys": ["wrist/rgb"],
    #         "DiffusionPolicyArgs.vis_dim": 1024,
    #         "DiffusionPolicyArgs.action_len": 12,
    #         "DiffusionPolicyArgs.embed_dim": 128,
    #         "ACT_Config.action_weighting_factor": 0.1,
    #     },
    #     strict=False,
    # )

    # main(
    #     {
    #         "UnrollEval.policy": 'playback',
    #         'UnrollEval.verbose': False,
    #         'UnrollEval.render': True,
    #         "UnrollEval.image_keys": ["wrist/splat_rgb", "left/splat_rgb", "right/splat_rgb"],
    #         "UnrollEval.seed":0,
    #         "UnrollEval.max_steps":600,
    #         "UnrollEval.env_name":"MugTree-fixed-gsplat-v2",
    #         "UnrollEval.load_checkpoint":"/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/29/16.11.36/data/ep_00001.h5",
    #         "UnrollEval.checkpoint_host":"http://escher.csail.mit.edu:4000",
    #         "UnrollEval.load_from_cache":True,
    #         "UnrollEval.action_smoothing": True,
    #         # action_weighting_factor=0,
    # }, strict=False
    # )

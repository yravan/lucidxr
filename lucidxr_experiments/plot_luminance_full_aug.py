import shutil
from pathlib import Path
import imageio
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from concurrent.futures import ProcessPoolExecutor, as_completed

from dotvar import auto_load  # noqa
from ml_logger import ML_Logger
from params_proto import PrefixProto

import torchvision.transforms as T
import torch
import cv2


class Params(PrefixProto, cli_parse=False):
    dataset_host: str = "/home/ravan/datasets/escher_snapshot/"
    cache_root: str = "/scratch/ravan/.cache"
    frame_stride: int = 10
    n_augments: int = 1
    n_workers: int = 16
    datasets: list = [
        # {
        #     "dataset_prefix": "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/pick_place_real/2025/08/25/17.02.44/",
        #     "camera_keys": [
        #         "wrist/rgb",
        #     ],
        #     "env_name": "ball_sorting_toy_real",
        # },
        # {
        #     "dataset_prefix": "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/ball_sorting_toy_new/2025/08/27/20.34.22_1/",
        #     "camera_keys": [
        #         "wrist/lucid",
        #         "wrist/splat_rgb-cic_12th_coffee_table",
        #         "wrist/splat_rgb-cic_11th_kitchen_back",
        #         "wrist/splat_rgb-google_building_table",
        #     ],
        #     "env_name": "ball_sorting_toy_new",
        # },
        # {
        #     "dataset_prefix": "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/24/14.30.11_1/",
        #     "camera_keys": [
        #         "wrist/rgb",
        #     ],
        #     "env_name": "ball_sorting_toy_real",
        # },
        {
            "dataset_prefix": "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/24/14.30.11_1/",
            "camera_keys": [
                "wrist/lucid",
                "wrist/splat_rgb-cic_4th_kitchen_day",
                "wrist/splat_rgb-cic_4th_nook",
                "wrist/splat_rgb-google_building_table",
            ],
            "env_name": "mug_tree",
        },
    ]


torch.set_num_threads(1)  # avoid deadlock in subprocesses


class AugmentWrapper(torch.nn.Module):
    def __init__(
        self,
        use_color_jitter=True,
        use_hue_jitter=True,
        use_gamma=False,
        use_blur=True,
        use_noise=False,
        use_grayscale=False,
        use_channel_dropout=False,
    ):
        super().__init__()
        aug_list = []

        if use_color_jitter:
            aug_list.append(
                T.ColorJitter(
                    brightness=0.5,
                    contrast=1.2,
                    saturation=0.5,
                )
            )
        if use_hue_jitter:
            aug_list.append(T.ColorJitter(hue=0.4))
        if use_gamma:
            aug_list.append(T.Lambda(lambda x: torch.clamp(x ** torch.empty(1).uniform_(0.7, 1.4).item(), 0.0, 1.0)))
        if use_blur:
            aug_list.append(T.GaussianBlur(kernel_size=3, sigma=(0.1, 2.0)))
        if use_noise:
            aug_list.append(T.Lambda(lambda x: torch.clamp(x + torch.randn_like(x) * 0.05, 0.0, 1.0)))
        if use_grayscale:
            aug_list.append(T.RandomGrayscale(p=0.2))
        if use_channel_dropout:
            def drop_channels(x):
                C = x.size(0)
                mask = torch.rand(C) > 0.8
                x = x.clone()
                for c in range(C):
                    if mask[c]:
                        x[c, :, :] = 0
                return x
            aug_list.append(T.Lambda(drop_channels))

        self.pipeline = T.Compose(aug_list) if aug_list else None

    def forward(self, imgs):
        if self.pipeline is None:
            return imgs
        if isinstance(imgs, np.ndarray):
            imgs = torch.from_numpy(imgs.transpose(2, 0, 1)).float()
        if imgs.dim() == 3:  # C,H,W
            imgs = self.pipeline(imgs)
            return imgs.permute(1, 2, 0).numpy()
        elif imgs.dim() == 4:  # B,C,H,W
            imgs = self.pipeline(imgs)
            return imgs.permute(0, 2, 3, 1).numpy()
        else:
            return self.pipeline(imgs)


def describe_augmentations(aug_model: AugmentWrapper) -> str:
    desc = []
    for t in aug_model.pipeline.transforms if aug_model.pipeline else []:
        if isinstance(t, T.ColorJitter):
            args = []
            if t.brightness: args.append(f"brightness={t.brightness}")
            if t.contrast: args.append(f"contrast={t.contrast}")
            if t.saturation: args.append(f"saturation={t.saturation}")
            if t.hue: args.append(f"hue={t.hue}")
            desc.append("ColorJitter(" + ", ".join(args) + ")")
        elif isinstance(t, T.GaussianBlur):
            desc.append(f"GaussianBlur(ksize={t.kernel_size}, sigma={t.sigma})")
        elif isinstance(t, T.RandomGrayscale):
            desc.append(f"RandomGrayscale(p={t.p})")
        elif isinstance(t, T.Lambda):
            desc.append("Lambda(...)")
        else:
            desc.append(t.__class__.__name__)
    return "; ".join(desc) if desc else "No augmentations"


def compute_luminance(img: np.ndarray) -> np.ndarray:
    img = img.astype(np.float32) / 255.0 if img.dtype == np.uint8 else img
    return 0.299 * img[..., 0] + 0.587 * img[..., 1] + 0.114 * img[..., 2]


def compute_saturation(img: np.ndarray) -> float:
    hsv = mcolors.rgb_to_hsv(img.astype(np.float32) / 255.0)
    return hsv[..., 1].mean()


def compute_sharpness(img: np.ndarray) -> float:
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()


def compute_clipping(img: np.ndarray) -> float:
    img_f = img.astype(np.float32) / 255.0
    return np.mean((img_f <= 0.0) | (img_f >= 1.0))


def compute_hue(img: np.ndarray) -> float:
    hsv = mcolors.rgb_to_hsv(img.astype(np.float32) / 255.0)
    return hsv[..., 0].mean()


def compute_colorfulness(img: np.ndarray) -> float:
    (R, G, B) = [img[..., i].astype(np.float32) for i in range(3)]
    rg = np.abs(R - G)
    yb = np.abs(0.5 * (R + G) - B)
    std_rg, mean_rg = np.std(rg), np.mean(rg)
    std_yb, mean_yb = np.std(yb), np.mean(yb)
    return np.sqrt(std_rg**2 + std_yb**2) + 0.3 * np.sqrt(mean_rg**2 + mean_yb**2)


AUG_MODEL = AugmentWrapper()


def process_video(cam_key, cam_subpath, dataset_host, frame_stride, n_augments):
    print(f"[WORKER] Starting {cam_subpath} → {cam_key}")
    results = {cam_subpath: {m: [] for m in ["luminance","means","stds","saturation","sharpness","clipping","hue","colorfulness"]}}
    if "lucid" in cam_subpath:
        results[cam_subpath + "_aug"] = {m: [] for m in results[cam_subpath]}

    loader = ML_Logger(root=dataset_host, prefix=Params.dataset_prefix)
    try:
        video_memory = loader.load_file(cam_key)
    except Exception as e:
        print(f"[WARN] Failed to load {cam_key}: {e}")
        return results

    frame_count = 0
    for i, frame in enumerate(imageio.v3.imiter(video_memory, plugin="pyav")):
        if i % frame_stride != 0: continue
        Y = compute_luminance(frame)
        results[cam_subpath]["luminance"].append(Y.ravel())
        results[cam_subpath]["means"].append(Y.mean())
        results[cam_subpath]["stds"].append(Y.std())
        results[cam_subpath]["saturation"].append(compute_saturation(frame))
        results[cam_subpath]["sharpness"].append(compute_sharpness(frame))
        results[cam_subpath]["clipping"].append(compute_clipping(frame))
        results[cam_subpath]["hue"].append(compute_hue(frame))
        results[cam_subpath]["colorfulness"].append(compute_colorfulness(frame))

        if "lucid" in cam_subpath:
            for _ in range(n_augments):
                img = frame.astype(np.float32) / 255.0
                img_aug = AUG_MODEL(img)
                img_aug_uint8 = (img_aug * 255).astype(np.uint8)
                Y_aug = compute_luminance(img_aug_uint8)
                results[cam_subpath + "_aug"]["luminance"].append(Y_aug.ravel())
                results[cam_subpath + "_aug"]["means"].append(Y_aug.mean())
                results[cam_subpath + "_aug"]["stds"].append(Y_aug.std())
                results[cam_subpath + "_aug"]["saturation"].append(compute_saturation(img_aug_uint8))
                results[cam_subpath + "_aug"]["sharpness"].append(compute_sharpness(img_aug_uint8))
                results[cam_subpath + "_aug"]["clipping"].append(compute_clipping(img_aug_uint8))
                results[cam_subpath + "_aug"]["hue"].append(compute_hue(img_aug_uint8))
                results[cam_subpath + "_aug"]["colorfulness"].append(compute_colorfulness(img_aug_uint8))

        frame_count += 1
    print(f"[WORKER] Finished {cam_subpath}, processed {frame_count} frames (stride={frame_stride})")
    return results

def build_plots(all_cam_stats):
    print("[INFO] Building combined plots across datasets")
    fig, axes = plt.subplots(2, 3, figsize=(20, 10))

    con_bins = np.linspace(0, 0.5, 101)

    cam_con_hist = {}
    for cam_subpath, stats in all_cam_stats.items():
        if len(stats["stds"]) == 0:
            continue
        cam_con_hist[cam_subpath], _ = np.histogram(stats["stds"], bins=con_bins)
        print(f"[INFO] {cam_subpath}: {len(stats['means'])} frames, mean brightness {np.mean(stats['means']):.3f}, mean contrast {np.mean(stats['stds']):.3f}")

    # --- Contrast Histogram (counts) ---
    for cam_subpath, stats in all_cam_stats.items():
        if len(stats["stds"]) == 0: continue
        axes[0, 0].hist(stats["stds"], bins=50, alpha=0.5, label=cam_subpath)  # removed density=True
    axes[0, 0].set_title("Contrast Histogram"); axes[0, 0].legend()

    # --- Brightness vs Contrast (scatter, unchanged) ---
    for cam_subpath, stats in all_cam_stats.items():
        if len(stats["means"]) == 0: continue
        axes[0, 1].scatter(stats["means"], stats["stds"], alpha=0.3, s=5, label=cam_subpath)
    axes[0, 1].set_title("Brightness vs Contrast"); axes[0, 1].legend()

    # --- Frame Mean Luminance (counts) ---
    for cam_subpath, stats in all_cam_stats.items():
        axes[0, 2].hist(stats["means"], bins=50, alpha=0.5, label=cam_subpath)  # removed density=True
    axes[0, 2].set_title("Frame Mean Luminance"); axes[0, 2].legend()

    # --- Saturation (counts) ---
    for cam_subpath, stats in all_cam_stats.items():
        axes[1, 0].hist(stats["saturation"], bins=50, alpha=0.5, label=cam_subpath)
    axes[1, 0].set_title("Saturation"); axes[1, 0].legend()

    # --- Hue (counts) ---
    for cam_subpath, stats in all_cam_stats.items():
        axes[1, 1].hist(stats["hue"], bins=50, alpha=0.5, label=cam_subpath)
    axes[1, 1].set_title("Hue"); axes[1, 1].legend()

    # --- Colorfulness (counts) ---
    for cam_subpath, stats in all_cam_stats.items():
        axes[1, 2].hist(stats["colorfulness"], bins=50, alpha=0.5, label=cam_subpath)
    axes[1, 2].set_title("Colorfulness"); axes[1, 2].legend()

    fig.suptitle(f"Combined datasets with Augmentations: {describe_augmentations(AUG_MODEL)}", fontsize=12)
    plt.tight_layout(rect=[0, 0, 1, 0.92])
    plt.savefig(f"luminance_full_aug_{Params.datasets[0]['env_name']}.png")
    plt.show()

def main(**deps):
    print("[INFO] Updating configs...")
    Params._update(**deps)
    print("[INFO] Configs:", deps)

    all_cam_stats = {}
    for ds in Params.datasets:
        ds_prefix = ds["dataset_prefix"].lstrip("/") if ds["dataset_prefix"].startswith("/") else ds["dataset_prefix"]
        Params.dataset_prefix = ds_prefix
        loader = ML_Logger(root=Params.dataset_host, prefix=ds_prefix)

        all_entries = loader.glob("**/*.h5")
        print(f"[INFO] Found {len(all_entries)} episodes in {ds['env_name']} ({ds_prefix})")

        video_jobs = []
        for episode_key in all_entries:
            stem = Path(episode_key).stem
            cam_keys = loader.glob(f"videos/{stem}/*/*.mp4")
            for cam_key in cam_keys:
                cam_subpath = str(Path(cam_key).relative_to(f"videos/{stem}")).replace(".mp4", "")
                if cam_subpath in ds["camera_keys"]:
                    video_jobs.append((cam_key, cam_subpath))

        print(f"[INFO] {ds['env_name']}: {len(video_jobs)} videos selected")

        with ProcessPoolExecutor(max_workers=Params.n_workers) as executor:
            futures = {
                executor.submit(process_video, cam_key, cam_subpath, Params.dataset_host, Params.frame_stride, Params.n_augments): (
                    cam_key, cam_subpath
                )
                for cam_key, cam_subpath in video_jobs
            }
            for future in as_completed(futures):
                _, cam_subpath = futures[future]
                result = future.result()
                for k, v in result.items():
                    prefixed_key = f"{ds['env_name']}:{k}"
                    if prefixed_key not in all_cam_stats:
                        all_cam_stats[prefixed_key] = {metric: [] for metric in v}
                    for metric in v:
                        all_cam_stats[prefixed_key][metric].extend(v[metric])

    print("[INFO] All datasets processed, building plots...")
    build_plots(all_cam_stats)


if __name__ == "__main__":
    main()
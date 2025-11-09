import imageio
import torchvision
from dotvar import auto_load
import os
import pickle
import numpy as np
import torch
from PIL import Image
from matplotlib import pyplot as plt
from ml_logger import logger
from params_proto import Proto, ParamsProto
from torchvision import transforms
from torchvision.transforms import InterpolationMode
from tqdm import tqdm
from sklearn.decomposition import PCA  # using sklearn PCA
import pandas as pd
import random
import torchvision.transforms.functional as TF
from clip import clip

from lucidxr.learning.unroll_eval import load_policy, UnrollEval


class Args(ParamsProto):
    datasets = [
        # {   "prefix": "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/pick_place_robot_room/2025/08/07/15.58.28/",
        #     "image_keys": ["wrist/lucid"],
        #     "name": "pick place lucid"
        # },
        # {   "prefix": "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/pick_place_robot_room/2025/08/07/15.58.28/",
        #     "image_keys": ["wrist/splat_rgb", ],
        #     "name": "pick place splat"
        # },
        # {   "prefix": "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/pick_place_robot_room/2025/08/07/15.58.28/",
        #     "image_keys": ["wrist/domain_rand/0", ],
        #     "name": "pick place domain_rand"
        # },
        {   "prefix": "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/pick_place_robot_room/2025/08/07/15.58.28/",
            "image_keys": ["wrist/rgb",],
            "name": "pick place sim"
        },
        {   "prefix": "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/pick_place_real/2025/08/07/16.43.17/",
            "image_keys": ["wrist/rgb", ],
            "name": "pick place real"
        },
        # {   "prefix": "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/28/11.50.11/",
        #     "image_keys": ["wrist/rgb",],
        #     "name": "mug tree sim"
        # },
        # {   "prefix": "/lucidxr/lucidxr/datasets/lucidxr/corl-2025/mug_tree/2025/07/28/11.50.11/",
        #     "image_keys": ["wrist/lucid", ],
        #     "name": "mug_tree lucid"
        # },
    ]
    load_checkpoint = "/lucidxr/lucidxr/post_corl_2025/yajvan/8-19-25/../8-19-25/pick_place_heaviest_dr/learn/2025/08/19/12-17-12/base-frame/chunk-size-25/dec_layers-1/nheads-8/lr_backbone-1e-05/checkpoints/policy_last.pt"
    device = "cuda"
    dinov2_model = "dinov2_vitb14"   # choices: dinov2_vits14, dinov2_vitb14, dinov2_vitl14, dinov2_vitg14
    clip_model = "ViT-B/32"
    batch_size = 256
    max_images_per_dataset = None
    seed = 0
    out_prefix = "dinov2_pca"
    n_components = 2  # for plotting
    input_size = 224  # use 224 for speed; you can try 518 for ViT-14 models if desired
    embedding = "policy"  # choices: dinov2, clip, policy
    color_scheme = "frame_index"  # choices: dataset, frame_index

def set_seed(seed: int):
    np.random.seed(seed)
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def build_preprocess(jitter=True, size=224):
    # DINOv2 uses ImageNet normalization
    imagenet_mean = (0.485, 0.456, 0.406)
    imagenet_std  = (0.229, 0.224, 0.225)

    if jitter:
        return transforms.Compose(
            [
                transforms.Resize(size if isinstance(size, int) else size[0],
                                  interpolation=InterpolationMode.BICUBIC, antialias=True),
                transforms.CenterCrop(size if isinstance(size, int) else size[-1]),
                transforms.ColorJitter(brightness=0.2, contrast=0.3, saturation=0.3, hue=0.1),
                transforms.GaussianBlur(kernel_size=(13, 13), sigma=(2.0, 2.0)),
                transforms.ToTensor(),
                transforms.Normalize(mean=imagenet_mean, std=imagenet_std),
            ]
        )

    return transforms.Compose([
        transforms.Resize(size if isinstance(size, int) else size[0],
                          interpolation=InterpolationMode.BICUBIC, antialias=True),
        transforms.CenterCrop(size if isinstance(size, int) else size[-1]),
        transforms.ToTensor(),
        transforms.Normalize(mean=imagenet_mean, std=imagenet_std),
    ])

def load_images(log, dataset_prefix: str, image_keys: list, max_images=None, seed=0):
    paths = []
    with log.Prefix(dataset_prefix):
        for key in image_keys:
            found = log.glob(f"videos/*/{key}.mp4")
            paths.extend(found)
    if not paths:
        return []

    rng = np.random.default_rng(seed)
    idx = np.arange(len(paths))
    rng.shuffle(idx)
    if max_images is not None:
        idx = idx[:max_images]
    paths = [paths[i] for i in idx]

    imgs = []
    with log.Prefix(dataset_prefix):
        for p in tqdm(paths, desc=f"[load] {os.path.basename(dataset_prefix)} ({len(paths)} vids)"):
            buff = log.load_file(p)
            img = list(imageio.v3.imiter(buff, plugin="pyav"))
            imgs.append(img)
    print(len(paths))
    print(len(imgs))
    return imgs

def _ensure_pil_rgb(x):
    """Coerce x -> PIL.Image in RGB."""
    if isinstance(x, Image.Image):
        return x.convert("RGB")
    if torch.is_tensor(x):
        x = x.detach().cpu()
        # TF.to_pil_image expects CHW (float in [0,1]) or HWC uint8
        if x.ndim == 3 and x.shape[0] in (1, 3, 4):  # CHW
            pil = TF.to_pil_image(x)
        else:  # assume HWC
            pil = Image.fromarray(np.asarray(x))
        return pil.convert("RGB")
    if isinstance(x, np.ndarray):
        # handle grayscale/HWC/RGBA
        if x.ndim == 2:  # H,W
            x = np.stack([x, x, x], axis=-1)
        if x.shape[-1] == 4:  # RGBA -> RGB
            x = x[..., :3]
        if x.dtype != np.uint8:
            # scale to 0-255 if float
            x_min, x_max = float(x.min()), float(x.max())
            denom = (x_max - x_min) if x_max != x_min else 1.0
            x = ((x - x_min) / denom * 255.0).clip(0, 255).astype(np.uint8)
        return Image.fromarray(x).convert("RGB")
    raise TypeError(f"Unsupported image type: {type(x)}")

@torch.no_grad()
def encode_dinov2(model, preprocess, pil_images, device, batch_size=256):
    """
    Returns L2-normalized global embeddings.
    Works with torch.hub 'facebookresearch/dinov2' models which typically return (N, D).
    """
    feats = []
    for i in tqdm(range(0, len(pil_images), batch_size), desc="[DINOv2] encoding"):
        batch_imgs = pil_images[i:i + batch_size]
        batch_t = torch.stack([preprocess(_ensure_pil_rgb(im)) for im in batch_imgs], dim=0).to(device)
        out = model(batch_t)  # most hub variants return (N, D) features
        # if the hub returns a dict (older/newer variants), try common keys:
        if isinstance(out, dict):
            # try class token normalized feature if present
            for k in ("x_norm_clstoken", "x_norm_patchtokens", "feats", "feat", "embeddings"):
                if k in out:
                    out = out[k]
                    break
            if isinstance(out, dict):  # fallback to first tensor value
                out = next(v for v in out.values() if torch.is_tensor(v))
        emb = out.float()
        emb = emb / (emb.norm(dim=-1, keepdim=True) + 1e-9)
        feats.append(emb.detach().cpu())
    if not feats:
        return torch.empty(0, 768)  # default dim for vitb14; harmless fallback
    return torch.cat(feats, dim=0)


@torch.no_grad()
def encode_clip(model, preprocess, pil_or_arrays, device, batch_size=256):
    feats = []
    for i in tqdm(range(0, len(pil_or_arrays), batch_size), desc="[CLIP] encoding"):
        batch_items = pil_or_arrays[i:i + batch_size]
        batch_pils = [_ensure_pil_rgb(im) for im in batch_items]
        batch_t = torch.stack([preprocess(im) for im in batch_pils], dim=0).to(device)
        emb = model.encode_image(batch_t)
        emb = emb / emb.norm(dim=-1, keepdim=True)
        feats.append(emb.detach().cpu())
    return torch.cat(feats, dim=0) if feats else torch.empty(0, model.visual.output_dim)

@torch.no_grad()
def encode_resnet(model, preprocess, pil_or_arrays, device, batch_size=256):
    feats = []
    for i in tqdm(range(0, len(pil_or_arrays), batch_size), desc="[Resnet] encoding"):
        batch_items = pil_or_arrays[i:i + batch_size]
        batch_pils = [_ensure_pil_rgb(im) for im in batch_items]
        batch_t = torch.stack([preprocess(im) for im in batch_pils], dim=0).to(device)
        batch_t = torchvision.transforms.functional.resize(batch_t, 180)
        emb = model[0][1](batch_t)["0"]
        emb = emb.mean(dim=[-2, -1])  # -> shape (B, 512)
        emb = emb / emb.norm(dim=-1, keepdim=True)
        feats.append(emb.detach().cpu())
    return torch.cat(feats, dim=0) if feats else torch.empty(0, model.visual.output_dim)

def fit_gamma_wb_sets(sim_imgs, real_imgs,  # lists/arrays of uint8 or float [H,W,3]
                      direction="sim_to_real",  # or "real_to_sim"
                      n_quant=1024, lo=0.05, hi=0.95, eps=1e-6,
                      robust=True):
    """
    Fit global gamma (shared across channels) + per-channel white-balance gains
    between two domains with unequal, unpaired samples using quantile matching.

    direction:
      "sim_to_real": model real ≈ α_c * sim^γ  (maps SIM --> REAL)
      "real_to_sim": model sim  ≈ α_c * real^γ (maps REAL --> SIM)
    Returns: gamma (float), alphas (np.array shape [3])
    """
    def to_float_stack(imgs):
        if isinstance(imgs, np.ndarray) and imgs.ndim == 4:
            X = imgs
        else:
            X = np.stack(imgs, 0)
        X = X.astype(np.float32)
        if X.max() > 1.0: X /= 255.0
        return X

    S = to_float_stack(sim_imgs).reshape(-1, 3)  # [Ns*H*W, 3]
    R = to_float_stack(real_imgs).reshape(-1, 3) # [Nr*H*W, 3]

    # midtone mask (avoid saturations); apply per-domain to be safe
    maskS = (S > lo) & (S < hi)
    maskR = (R > lo) & (R < hi)
    S = S[maskS.all(axis=1)]
    R = R[maskR.all(axis=1)]

    # Build per-channel quantile samples
    qs = np.linspace(lo, hi, n_quant)
    # Values at these quantiles for each domain/channel
    S_q = np.quantile(S, qs, axis=0)  # [n_quant, 3]
    R_q = np.quantile(R, qs, axis=0)  # [n_quant, 3]

    # Choose source (x) and target (y) per direction
    if direction == "sim_to_real":
        X_q = S_q.clip(eps, 1-eps)   # source domain (sim)
        Y_q = R_q.clip(eps, 1-eps)   # target domain (real)
    elif direction == "real_to_sim":
        X_q = R_q.clip(eps, 1-eps)   # source domain (real)
        Y_q = S_q.clip(eps, 1-eps)   # target domain (sim)
    else:
        raise ValueError("direction must be 'sim_to_real' or 'real_to_sim'")

    # Fit ln(Y_c) = gamma * ln(X) + ln(alpha_c)
    x = np.log(X_q)                         # [n_quant, 3]
    y = np.log(Y_q)                         # [n_quant, 3]

    # Estimate gamma per channel, then take robust central tendency
    gammas = []
    alphas = []
    A = np.vstack([x.mean(axis=1), np.ones_like(qs)]).T  # use channel-mean x for stability
    # Option 1 (robust): fit per channel then median gamma
    for c in range(3):
        y_c = y[:, c]
        if robust:
            # Huber-like weights: downweight tails
            w = 1.0 / (1.0 + ((y_c - y_c.mean()) / (3*y_c.std()+1e-6))**2)
            Aw = A * w[:, None]
            yw = y_c * w
            g_c, b_c = np.linalg.lstsq(Aw, yw, rcond=None)[0]
        else:
            g_c, b_c = np.linalg.lstsq(A, y_c, rcond=None)[0]
        gammas.append(g_c)
        alphas.append(np.exp(b_c))
    gamma = float(np.median(gammas))

    # Refit alphas per channel with fixed gamma
    alphas2 = []
    xg = gamma * x.mean(axis=1)  # [n_quant]
    A0 = np.ones_like(xg)[:, None]
    for c in range(3):
        y_c = y[:, c]
        b = np.linalg.lstsq(A0, (y_c - xg), rcond=None)[0][0]
        alphas2.append(np.exp(b))

    print("gamma =", gamma)
    print("alphas =", alphas2)

    return gamma, np.array(alphas2, dtype=np.float32)

def apply_gamma_wb(imgs, gamma, alphas):
    out = (imgs/255) ** gamma
    out = out * alphas[None, None, :]
    return np.clip(out, 0, 1) * 255  # scale back to [0, 255] range

def main():
    UnrollEval.load_checkpoint = Args.load_checkpoint
    set_seed(Args.seed)

    device = torch.device(Args.device if torch.cuda.is_available() else "cpu")

    if Args.embedding == "clip":
        print(f"[INFO] loading CLIP: {Args.clip_model} on {Args.device}")
        model, _ = clip.load(Args.clip_model, device=device, jit=False)
        model.eval()
    elif Args.embedding == "dinov2":
        # Requires: pip install git+https://github.com/facebookresearch/dinov2 or rely on torch.hub
        print(f"[INFO] loading DINOv2: {Args.dinov2_model} on {device}")
        model = torch.hub.load('facebookresearch/dinov2', Args.dinov2_model)
        model = model.to(device).eval()
    else:
        policy = load_policy()
        model = policy.backbones["wrist/rgb"]

    preprocess = build_preprocess(jitter=True, size=Args.input_size)


    sim_images = load_images(
        logger, Args.datasets[0]["prefix"], Args.datasets[0]["image_keys"],
        max_images=Args.max_images_per_dataset, seed=Args.seed
    )
    sim_images = np.concatenate(sim_images[:15], axis=0)

    real_images = load_images(
        logger, Args.datasets[1]["prefix"], Args.datasets[1]["image_keys"],
        max_images=Args.max_images_per_dataset, seed=Args.seed
    )
    real_images = np.concatenate(real_images[:15], axis=0)

    gamma, alphas = fit_gamma_wb_sets(
        sim_images.astype(np.float32), real_images.astype(np.float32),direction="real_to_sim"
    )

    all_feats = []
    all_labels = []
    per_ds_counts = []

    for meta in Args.datasets:
        ds_prefix = meta["prefix"]
        print(ds_prefix)
        pil_images = load_images(
            logger, ds_prefix, meta["image_keys"],
            max_images=Args.max_images_per_dataset, seed=Args.seed
        )
        if len(pil_images) == 0:
            print(f"[WARN] no images found in {ds_prefix}")
            continue

        if "real" in meta["name"].lower():
            print(f"[INFO] applying gamma correction and white balance for {meta['name']} …")
            pil_images = [apply_gamma_wb(np.array(img).astype(np.float32), gamma, alphas) for img in pil_images[:10]]

        for imgs in pil_images[:10]:
            if Args.embedding == "clip":
                print(f"[INFO] encoding {len(imgs)} images with CLIP …")
                feats = encode_clip(model, preprocess, imgs, device, batch_size=Args.batch_size).to(torch.float32)
            elif Args.embedding == "dinov2":
                print(f"[INFO] encoding {len(imgs)} images with DINOv2 …")
                feats = encode_dinov2(model, preprocess, imgs, device, batch_size=Args.batch_size).to(torch.float32)
            else:
                print(f"[INFO] encoding {len(imgs)} images with policy backbone …")
                feats = encode_resnet(model, preprocess, imgs, device, batch_size=Args.batch_size).to(torch.float32)
            all_feats.append(feats)
            if Args.color_scheme == "dataset":
                all_labels += [meta["name"]] * feats.shape[0]
            else:
                all_labels += (np.arange(feats.shape[0])/feats.shape[0]).tolist()
        print(f"[INFO] {meta['name']}: {feats.shape[0]} embeddings")
        count = len(all_labels) if len(per_ds_counts) == 0 else len(all_labels) - sum(per_ds_counts)
        per_ds_counts.append(count)
        if not all_feats:
            print("[ERROR] No features collected.")
            return

    feats_cat = torch.cat(all_feats, dim=0).numpy()
    labels = np.array(all_labels)

    print(f"[INFO] PCA to {Args.n_components}D …")
    pca = PCA(n_components=Args.n_components, random_state=Args.seed)
    xy = pca.fit_transform(feats_cat)

    # Compute 95% bounds per axis
    x_lo, x_hi = np.quantile(xy[:, 0], [0.025, 0.975])
    y_lo, y_hi = np.quantile(xy[:, 1], [0.025, 0.975])

    # Optional padding so points don't sit exactly on border
    pad_x = 0.02 * (x_hi - x_lo + 1e-12)
    pad_y = 0.02 * (y_hi - y_lo + 1e-12)

    x_min_lim, x_max_lim = x_lo - pad_x, x_hi + pad_x
    y_min_lim, y_max_lim = y_lo - pad_y, y_hi + pad_y

    for i in range(len(per_ds_counts)):
        print("[INFO] plotting …")
        plt.figure(figsize=(7, 6))
        if Args.color_scheme == "dataset":
            uniq = list(dict.fromkeys(labels))
            for u in uniq:
                m = labels == u
                plt.scatter(xy[m, 0], xy[m, 1], s=12, alpha=0.2, label=u)
        else:
            sc = plt.scatter(xy[sum(per_ds_counts[:i]):sum(per_ds_counts[:i + 1]), 0], xy[sum(per_ds_counts[:i]):sum(per_ds_counts[:i + 1]), 1], c=labels[sum(per_ds_counts[:i]):sum(per_ds_counts[:i + 1])], cmap="viridis", s=12, alpha=0.2)
            plt.colorbar(sc, label="Normalized Frame Index")
        plt.xlabel("PC 1")
        plt.ylabel("PC 2")
        plt.title(f"{Args.datasets[i]['name']} Embeddings → PCA (2D)")
        plt.legend(markerscale=1.5, frameon=True)
        plt.xlim(x_min_lim, x_max_lim)
        plt.ylim(y_min_lim, y_max_lim)
        plt.tight_layout()
        plt.show()

    print("[INFO] plotting …")
    plt.figure(figsize=(7, 6))
    if Args.color_scheme == "dataset":
        uniq = list(dict.fromkeys(labels))
        for u in uniq:
            m = labels == u
            plt.scatter(xy[m, 0], xy[m, 1], s=12, alpha=0.2, label=u)
    else:
        sc = plt.scatter(
            xy[:, 0],
            xy[:, 1],
            c=labels,
            cmap="viridis",
            s=12,
            alpha=0.2,
        )
        plt.colorbar(sc, label="Normalized Frame Index")
    plt.xlabel("PC 1")
    plt.ylabel("PC 2")
    plt.title(f"Embeddings → PCA (2D)")
    plt.legend(markerscale=1.5, frameon=True)
    plt.xlim(x_min_lim, x_max_lim)
    plt.ylim(y_min_lim, y_max_lim)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()

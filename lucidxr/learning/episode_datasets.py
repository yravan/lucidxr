from time import sleep

import tempfile

import h5py
import random
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor

from dotvar import auto_load  # noqa
from filelock import FileLock
from pathlib import Path

import imageio
import numpy as np
import torch
from termcolor import cprint
from torch.utils.data import DataLoader
import os

import zarr

from torchvision.io import read_image
import torchvision.transforms.v2 as T
from torchvision.transforms import InterpolationMode
from zarr.errors import GroupNotFoundError

from vuer_mujoco.schemas.se3.rot_gs6 import gs62quat, quat2gs6
from vuer_mujoco.tasks.base.real_robot_env import RealRobotEnv

def validate_all_cache(cache_root, max_keys=5):
    """
    Recursively search for every 'episode_data.zarr' in cache_root,
    and validate arrays inside.
    """
    cache_root = Path(cache_root)
    zarr_dirs = list(cache_root.rglob("episode_data.zarr"))
    print(f"[validate_all_cache] Found {len(zarr_dirs)} episode_data.zarr groups under {cache_root}")

    for ep_dir in zarr_dirs:
        print("=" * 80)
        print(f"[validate_all_cache] Checking episode: {ep_dir}")

        try:
            root = zarr.open_group(str(ep_dir), mode="r")
        except Exception as e:
            print(f"  ❌ Failed to open zarr group: {e}")
            continue

        print("  Contents:")
        try:
            print(root.tree())
        except Exception as e:
            print(f"  ❌ Failed to print tree: {e}")

        for k in list(root.keys())[:max_keys]:  # only first few keys for brevity
            obj = root[k]
            if isinstance(obj, zarr.Array):
                print(f"   - {k}: shape={obj.shape}, dtype={obj.dtype}")

                if obj.shape[0] == 0:
                    print(f"     ⚠️ EMPTY array (shape[0]==0)")
                    continue

                try:
                    _first = obj[0]
                    _last = obj[-1]
                    print(f"     first frame ok (type={type(_first)}), last frame ok (type={type(_last)})")
                except Exception as e:
                    print(f"     ❌ Error accessing array {k}: {e}")

            elif isinstance(obj, zarr.Group):
                print(f"   - {k}: subgroup (contains {len(list(obj.keys()))} keys)")
            else:
                print(f"   - {k}: unknown type {type(obj)}")

    print()

def safe_load_h5(loader, episode_key):
    """
    Copy the .h5 from NFS to local scratch, load it, then delete the scratch copy.
    """
    remote_path = episode_key
    local_tmp = Path(tempfile.gettempdir()) / Path(episode_key).name

    try:
        # Copy to scratch
        h5_stream = loader.load_file(remote_path)
        with open(local_tmp, "wb") as f:
            if isinstance(h5_stream, (bytes, bytearray)):
                f.write(h5_stream)
            else:
                shutil.copyfileobj(h5_stream, f)
        print(f"[safe_load_h5] staged {remote_path} -> {local_tmp}")

        # Load arrays
        with h5py.File(local_tmp, "r") as f:
            obs = f["state"][:]
            actions = f["action"][:]

    finally:
        # Always clean up local copy
        if local_tmp.exists():
            try:
                local_tmp.unlink()
                print(f"[safe_load_h5] deleted scratch copy {local_tmp}")
            except Exception as e:
                print(f"[safe_load_h5] warning: failed to delete {local_tmp}: {e}")

    return obs, actions

def prune_safe(prune_dir: Path):
    if not prune_dir.exists():
        return

    # Move to a temporary name first (atomic rename)
    tmp_dir = prune_dir.with_suffix(".prune_tmp")
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)   # clear any leftover from previous run
    os.replace(prune_dir, tmp_dir)
    # Now readers will see "cache_dir" as gone instantly.
    # The slow delete happens in the background.
    shutil.rmtree(tmp_dir)


def load_png_as_tensor(filepath: str) -> torch.Tensor:
    """
    Returns a CxHxW uint8 tensor (3 channels). Handles RGBA/gray.
    """
    # DEBUG:
    print(f"[load_png_as_tensor] (T:{threading.current_thread().name}) filepath={filepath}", flush=True)
    img = read_image(str(filepath))  # CxHxW, dtype=uint8
    print(f"[load_png_as_tensor] read_image -> shape={tuple(img.shape)}, dtype={img.dtype}", flush=True)
    # Drop alpha if present
    if img.shape[0] == 4:
        print(f"[load_png_as_tensor] dropping alpha channel (shape before={tuple(img.shape)})", flush=True)
        img = img[:3]
        print(f"[load_png_as_tensor] shape after drop={tuple(img.shape)}", flush=True)
    # Expand gray to 3ch
    if img.shape[0] == 1:
        print(f"[load_png_as_tensor] expanding gray to 3ch (shape before={tuple(img.shape)})", flush=True)
        img = img.expand(3, *img.shape[1:])
        print(f"[load_png_as_tensor] shape after expand={tuple(img.shape)}", flush=True)
    out = img.contiguous()
    print(f"[load_png_as_tensor] returning contiguous tensor shape={tuple(out.shape)}, dtype={out.dtype}", flush=True)
    return out


class CombinedDataset(torch.utils.data.Dataset):
    def __init__(self, *datasets):
        super(CombinedDataset).__init__()

        # DEBUG:
        cprint(f"[CombinedDataset.__init__] (T:{threading.current_thread().name}) num_datasets={len(datasets)}", "cyan")
        self.dataset_collection = datasets
        self.dataset_lens = [len(d) for d in self.dataset_collection]
        print(f"[CombinedDataset.__init__] dataset_lens={self.dataset_lens}, total_len={sum(self.dataset_lens)}", flush=True)

        # map from global index to dataset index and local index
        arr = []

        for i, dataset_size in enumerate(self.dataset_lens):
            # Iterate through each dataset in the collection and map global indices
            # to corresponding dataset index and item index within each dataset.
            for j in range(dataset_size):
                arr.append((i, j))

        self.dataset_indices = np.array(arr, dtype=np.int64)
        print(f"[CombinedDataset.__init__] built index map of length={len(self.dataset_indices)}", flush=True)

    def __len__(self):
        return sum(self.dataset_lens)

    def __getitem__(self, index):
        dataset_idx, local_idx = self.dataset_indices[index]
        # DEBUG:
        # cprint(f"[CombinedDataset.__getitem__] (T:{threading.current_thread().name}) index={index} -> (dataset_idx={dataset_idx}, local_idx={local_idx})", "yellow")
        return self.dataset_collection[dataset_idx][local_idx]


class EpisodeDataset(torch.utils.data.Dataset):
    max_action_size = 2000

    def __init__(
        self,
        *,
        data_prefix,
        cache_root,
        dataset_host=None,
        episode_paths,
        chunk_size=100,
        train_image_keys,
        act_image_keys,
        prune_cache=False,
        lucid_mode=False,
        aug_camera_randomization=False,
        use_quat=False,
        transforms=None,
        downsample_images=1,
        blur_images=False,
        real_robot=False,
        delta_space=False,
        frame_skip = 10,
        history_length = 1,
    ):
        """
        A dataset class for managing episodic data used in machine learning tasks. This dataset handles
        loading, caching, and processing of various types of data such as observations, actions,
        and optionally, image data. The data can either be loaded locally from a cache or pulled remotely.
        """
        super(EpisodeDataset).__init__()
        from ml_logger import ML_Logger

        # DEBUG:
        cprint(f"[EpisodeDataset.__init__] (T:{threading.current_thread().name}) init with {len(episode_paths)} episodes", "cyan")
        print(f"[EpisodeDataset.__init__] data_prefix={data_prefix}, cache_root={cache_root}, chunk_size={chunk_size}, frame_skip={frame_skip}, history_length={history_length}", flush=True)
        print(f"[EpisodeDataset.__init__] use_quat={use_quat}, lucid_mode={lucid_mode}, aug_camera_randomization={aug_camera_randomization}, downsample_images={downsample_images}, blur_images={blur_images}, real_robot={real_robot}, delta_space={delta_space}", flush=True)

        self.device = None
        self.use_quat = use_quat
        self.cache_root = cache_root
        self.lucid_mode = lucid_mode
        self.prune_cache = prune_cache
        self.frame_skip = frame_skip
        self.history_length = history_length
        self.aug_camera_randomization = aug_camera_randomization

        self.chunk_size = chunk_size

        self.cache_prefix = Path(cache_root) / data_prefix.lstrip("/")
        print(f"[EpisodeDataset.__init__] cache_prefix={self.cache_prefix}", flush=True)


        self.train_image_keys = train_image_keys
        self.act_image_keys = act_image_keys
        self.image_keys = self.train_image_keys if train_image_keys else self.act_image_keys
        self.camera_keys = set([x.split("/")[0] for x in self.image_keys])
        print(f"[EpisodeDataset.__init__] image_keys={self.image_keys}", flush=True)
        print(f"[EpisodeDataset.__init__] camera_keys={self.camera_keys}", flush=True)

        self.is_sim = None

        if dataset_host is None:
            dataset_host = os.getenv("ML_LOGGER_HOST")
            print(f"[EpisodeDataset.__init__] dataset_host from env ML_LOGGER_HOST -> {dataset_host}", flush=True)
        if dataset_host.startswith("/"):
            data_prefix = data_prefix.lstrip("/")
            print(f"[EpisodeDataset.__init__] dataset_host is local path, updated data_prefix={data_prefix}", flush=True)
        self.loader = ML_Logger(prefix=data_prefix, root=dataset_host)
        self.dataset_host = dataset_host
        self.root_prefix = data_prefix
        print(f"[EpisodeDataset.__init__] ML_Logger configured: root={self.dataset_host}, prefix={self.root_prefix}", flush=True)

        episodes = episode_paths

        self.multiplicity = np.inf
        for key in self.image_keys:
            prefix = f"videos/{episodes[0].replace('data/','').split('.')[0]}"
            image_keys = self.loader.glob(f"{prefix}/{key}/*.mp4")
            print(f"[EpisodeDataset.__init__] multiplicity probe key={key} -> found {len(image_keys)} files under {prefix}/{key}", flush=True)
            self.multiplicity = min(self.multiplicity, len(image_keys))
        if self.multiplicity == 0 or self.multiplicity == np.inf:
            self.multiplicity = 1
        cprint(f"[EpisodeDataset.__init__] multiplicity={self.multiplicity}", "blue")

        # ge: because we pad, fixed episode order is no problem.
        self.episode_paths = sorted(episode_paths)
        print(f"[EpisodeDataset.__init__] sorted episode_paths (n={len(self.episode_paths)}) sample={self.episode_paths[:3]}", flush=True)

        self.real_robot = real_robot
        self.episode_sizes = self.pre_load_episodes()
        cprint(f"[EpisodeDataset.__init__] episode_sizes={self.episode_sizes} (total={sum(self.episode_sizes)})", "blue")
        validate_all_cache(cache_root)
        self.transforms = transforms
        self.downsample_images = downsample_images
        interp_mode = InterpolationMode.BILINEAR if downsample_images > 1 else InterpolationMode.NEAREST
        resize_tf = T.Resize(360 // downsample_images, interpolation=interp_mode)
        self.transforms = T.Compose([self.transforms, resize_tf]) if self.transforms else resize_tf
        print(f"[EpisodeDataset.__init__] transforms set: downsample_images={downsample_images}, interp_mode={interp_mode}", flush=True)

        if blur_images:
            self.transforms = T.Compose((
                self.transforms,
                T.GaussianBlur(kernel_size=(5,5))
            ))
            print(f"[EpisodeDataset.__init__] blur_images=True -> appended GaussianBlur(5x5)", flush=True)
        self.delta_space = delta_space
        print(f"[EpisodeDataset.__init__] delta_space={self.delta_space}", flush=True)

    def pre_load_episodes(self):
        data_sizes = []
        cprint(f"[EpisodeDataset.pre_load_episodes] (T:{threading.current_thread().name}) start preloading {len(self.episode_paths)} episodes with ThreadPoolExecutor(max_workers=32)", "cyan")
        with ThreadPoolExecutor(max_workers=32) as executor:
            data_sizes = list(executor.map(self.download_episode, self.episode_paths))
        print(f"[EpisodeDataset.pre_load_episodes] data_sizes={data_sizes} (sum={sum(data_sizes) if data_sizes else 0})", flush=True)
        return data_sizes


    def load_cam_video(self, episode_key, stem, cam_key, obs):
        session_prefix = Path(episode_key).parent.parent
        cprint(f"[EpisodeDataset.load_cam_video] (T:{threading.current_thread().name}) ep={episode_key}, stem={stem}, cam_key={cam_key}, session_prefix={session_prefix}", "magenta")
        with self.loader.Prefix(session_prefix):
            video_path = f"videos/{stem}/{cam_key}.mp4"
            # print(video_path)
            try:
                video_memory = self.loader.load_file(video_path)
                print(f"[EpisodeDataset.load_cam_video] loaded video file {video_path} (bytes={len(video_memory) if hasattr(video_memory,'__len__') else 'unknown'})", flush=True)
                frames = list(imageio.v3.imiter(video_memory, plugin="pyav"))  # PyAV backend
                print(f"[EpisodeDataset.load_cam_video] decoded frames={len(frames)}", flush=True)
            except Exception as e:
                print(f"\33[31m[EpisodeDataset.load_cam_video] Error loading video {video_path}: {e}\033[0m", flush=True)
                raise e
            if len(frames) != len(obs):
                print("[EpisodeDataset.load_cam_video] WARNING: video length does not match observation length!"
                      f" {len(frames)} != {len(obs)}", flush=True)

        stacked = np.stack(frames, axis=0)
        if len(stacked.shape) == 3:
            print(f"[EpisodeDataset.load_cam_video] frame stack had no channel dim, expanding (before shape={stacked.shape})", flush=True)
            stacked = stacked[..., None]
        # tensor = torch.from_numpy(stacked)
        print(f"[EpisodeDataset.load_cam_video] returning stacked shape={stacked.shape}, dtype={stacked.dtype}", flush=True)
        return stacked, len(frames)

    def download_episode(self, episode_key):
        """
        Downloads an episode from the remote server and saves it to the local cache.
        This is useful for ensuring that the dataset is available locally for faster access.
        """
        prefix = self.cache_prefix / episode_key
        # if self.prune_cache:
        #     try:
        #         print(f"[download_episode] prune_cache: rmtree {prefix}", flush=True)
        #         shutil.rmtree(prefix)
        #     except Exception as _e:
        #         print(f"[download_episode] prune_cache: rmtree ignored error: {_e}", flush=True)
        print(f"[download_episode] (T:{threading.current_thread().name}) loading episode {episode_key}, prefix={prefix}", flush=True)
        try:
            root = zarr.open_group(str(prefix / "episode_data.zarr"), mode="a")
            print(f"[download_episode] opened zarr group at {prefix / 'episode_data.zarr'} (mode='a')", flush=True)
            obs_np = root["obs"][:]  # materialize to NumPy (one read)
            act_np = root["actions"][:]
            print(f"[download_episode] local cache obs shape={obs_np.shape}, actions shape={act_np.shape}", flush=True)

            if self.aug_camera_randomization:
                for k in self.camera_keys:
                    _ = root[f"{k}_K"]
                    _ = root[f"{k}_C2W"]
                    print(f"[download_episode] verified camera randomization arrays for {k}: {k}_K, {k}_C2W exist", flush=True)

            for cam_key in self.image_keys:
                if self.multiplicity == 1:
                    key = (prefix / "render" / cam_key).with_suffix(".data")
                    if not isinstance(root[cam_key], zarr.Array):
                        raise FileNotFoundError(f"Camera key {cam_key} not found in local cache for episode {episode_key}.")
                    print(f"[download_episode] verified cam_key={cam_key} present (multiplicity=1), example data path={key}", flush=True)
                else:
                    for i in range(self.multiplicity):
                        key = (prefix / "render" / f"{cam_key}/{i}").with_suffix(".data")
                        _ = root[f"{cam_key}/{i}"]
                        print(f"[download_episode] verified cam_key={cam_key}/{i} present (multiplicity={self.multiplicity}), example data path={key}", flush=True)

            if self.aug_camera_randomization:
                for k in self.camera_keys:
                    cam_key = f"{k}/midas_depth_full"
                    print(f"[download_episode] (aug) checked depth key placeholder for {cam_key}", flush=True)
            ret = obs_np.shape[0] - 1 - self.frame_skip
            print(f"[download_episode] returning length={ret} (obs_len-1-frame_skip)", flush=True)
            return ret
        except (FileNotFoundError, KeyError, GroupNotFoundError) as e:
            print("[download_episode] local cache not found, loading from remote", e, flush=True)
            print("cache:", self.cache_prefix, flush=True)

            # now load from the remote server.
            stem = Path(episode_key).stem

            try:
                obs, actions = self.loader.load_h5(episode_key + ":state,action")
                print(f"[download_episode] remote load h5 ok: obs shape={obs.shape}, actions shape={actions.shape}", flush=True)
            except Exception as e2:
                print(f"\33[31m[download_episode] Error loading episode {self.loader.root}/{self.root_prefix}/{episode_key}: {e2}\033[0m", flush=True)
                raise e2

            print("[download_episode] now saving local cache.", flush=True)
            # save as both memmaps and zarr files

            zarr.group(str(prefix / "episode_data.zarr"))
            print(f"[download_episode] ensured group exists at {prefix / 'episode_data.zarr'}", flush=True)

            lock_path = prefix / "episode_data.zarr.lock"
            root = zarr.open_group(str(prefix / "episode_data.zarr"), mode="a")
            print(f"[download_episode] zarr group opened (mode='a') with lock", flush=True)

            with FileLock(str(lock_path)):
                # set obs and action as zarr chunks
                if "obs" not in root:
                    print(f"[download_episode] creating obs array: shape={obs.shape}, chunks={(1, obs.shape[1])}, dtype='f4'", flush=True)
                    obs_arr = root.create_array("obs", shape=obs.shape, chunks=(1, obs.shape[1]), dtype="f4")
                    obs_arr[:] = obs
                else:
                    print("[download_episode] obs array already exists", flush=True)
                if 'actions' not in root:
                    print(f"[download_episode] creating actions array: shape={actions.shape}, chunks={(self.chunk_size, actions.shape[1])}, dtype='f4'", flush=True)
                    action_arr = root.create_array("actions", shape=actions.shape, chunks=(self.chunk_size, actions.shape[1]), dtype='f4')
                    action_arr[:] = actions
                else:
                    print("[download_episode] actions array already exists", flush=True)

            if self.aug_camera_randomization:
                # load the cameras and depth renders
                for k in self.camera_keys:
                    Ks, c2ws = self.loader.load_h5(episode_key + f":{k}/K,{k}/C2W")
                    print(f"[download_episode] loaded {k}/K shape={Ks.shape}, {k}/C2W shape={c2ws.shape}", flush=True)

                    with FileLock(str(lock_path)):
                        if f"{k}_K" not in root:
                            print(f"[download_episode] creating {k}_K zarr array: shape={Ks.shape}, chunks={(self.chunk_size, *Ks.shape[1:])}", flush=True)
                            k_arr = root.create_array(f"{k}_K", shape=Ks.shape, chunks=(self.chunk_size, *Ks.shape[1:]), dtype='f4')
                            k_arr[:] = Ks
                        else:
                            print(f"[download_episode] {k}_K already exists", flush=True)
                        if f"{k}_C2W" not in root:
                            print(f"[download_episode] creating {k}_C2W zarr array: shape={c2ws.shape}, chunks={(self.chunk_size, *c2ws.shape[1:])}", flush=True)
                            c2w_arr = root.create_array(f"{k}_C2W", shape=c2ws.shape, chunks=(self.chunk_size, *c2ws.shape[1:]), dtype='f4')
                            c2w_arr[:] = c2ws
                        else:
                            print(f"[download_episode] {k}_C2W already exists", flush=True)

                for k in self.camera_keys:
                    load_key = f"{k}/lucid/midas_depth_full"
                    cam_key = f"{k}/midas_depth_full"
                    single_view, num_frames = self.load_cam_video(episode_key, stem, load_key, obs)
                    print(f"[download_episode] saving depth camera {cam_key} shape={single_view.shape} episode={episode_key}", flush=True)
                    try:
                        with FileLock(str(lock_path)):
                            if cam_key not in root:
                                print(f"[download_episode] creating zarr array for {cam_key} with chunks=(1, *shape[1:]) dtype=float32", flush=True)
                                cam_arr = root.create_array(f"{cam_key}", shape=single_view.shape, chunks=(1, *single_view.shape[1:]), dtype='float32')
                                cam_arr[:] = single_view
                            else:
                                print(f"[download_episode] {cam_key} already exists", flush=True)
                    except Exception as e3:
                        print(f"[download_episode] Another thread is creating the array for {cam_key}, ignoring this error. {e3}", flush=True)

            for cam_key in self.image_keys:
                if self.multiplicity == 1:
                    single_view, num_frames = self.load_cam_video(episode_key, stem, cam_key, obs)
                    print(f"[download_episode] saving camera {cam_key} shape={single_view.shape} episode={episode_key}", flush=True)
                    try:
                        with FileLock(str(lock_path)):
                            if cam_key not in root:
                                print(f"[download_episode] creating zarr array for {cam_key} with chunks=(1, *shape[1:]) dtype=uint8", flush=True)
                                cam_arr = root.create_array(cam_key, shape=single_view.shape, chunks=(1, *single_view.shape[1:]), dtype='uint8') # TODO: hardcoded shape
                                cam_arr[:] = single_view
                            else:
                                print(f"[download_episode] cam {cam_key} already exists", flush=True)
                    except Exception as e4:
                        print(f"[download_episode] Another thread is creating the array, ignoring this error. {e4}", flush=True)
                else:
                    for i in range(self.multiplicity):
                        cam_key, tmp = f"{cam_key}/{i}", cam_key
                        single_view, num_frames = self.load_cam_video(episode_key, stem, cam_key, obs)
                        print(f"[download_episode] saving camera {cam_key} shape={single_view.shape} episode={episode_key}", flush=True)
                        try:
                            with FileLock(str(lock_path)):
                                if cam_key not in root:
                                    print(f"[download_episode] creating zarr array for {cam_key} with chunks=(1, *shape[1:]) dtype=uint8", flush=True)
                                    cam_arr = root.create_array(
                                        cam_key, shape=single_view.shape, chunks=(1, *single_view.shape[1:]), dtype="uint8"
                                    )  # TODO: hardcoded shape
                                    cam_arr[:] = single_view
                                else:
                                    print(f"[download_episode] cam {cam_key} already exists", flush=True)
                        except Exception as e5:
                            print(f"[download_episode] Another thread is creating the array, ignoring this error. {e5}", flush=True)
                        cam_key = tmp
            root = zarr.open_group(str(prefix / "episode_data.zarr"), mode="r")
            required = ["obs", "actions", *self.image_keys]
            for k in required:
                if k not in root:
                    raise RuntimeError(f"Episode {episode_key} missing {k} after caching!")

            ret2 = len(obs) - 1 - self.frame_skip
            print(f"[download_episode] finished remote save, returning length={ret2}", flush=True)
            return ret2

    def load_chunk(self, episode_id, relative_idx):
        """
        Load a chunk of data from the dataset.
        Args:
            episode_id: the id of the episode to load
            relative_idx: the index within the episode to load
            H: the number of actions in the future to load (chunk size)
        Returns:
            a dictionary of the observation, action, episode ids, and images
        """
        ep_path = self.episode_paths[episode_id]
        prefix = self.cache_prefix / ep_path
        multiview = {}

        # print(f"[load_chunk] (T:{threading.current_thread().name}) ep_id={episode_id}, rel_idx={relative_idx}, ep_path={ep_path}", flush=True)

        relative_idx = relative_idx + self.frame_skip
        # print(f"[load_chunk] relative_idx advanced by frame_skip={self.frame_skip} -> {relative_idx}", flush=True)

        # load state and action from the memmap files
        try:
            root = zarr.open_group(str(prefix / "episode_data.zarr"), mode="r")
            # print(f"[load_chunk] opened zarr group for read: {prefix / 'episode_data.zarr'}", flush=True)
        except Exception as e:
            # print(f"[load_chunk] open zarr failed, downloading episode. error={e}", flush=True)
            self.download_episode(ep_path)
            root = zarr.open_group(str(prefix / "episode_data.zarr"), mode="r")
            # print(f"[load_chunk] re-opened zarr group after download", flush=True)
        pad_length = self.frame_skip - (relative_idx - self.history_length + 1)
        start_ind = max(self.frame_skip, relative_idx - self.history_length + 1)
        # print(f"[load_chunk] pad_length(hist)={pad_length}, start_ind={start_ind}", flush=True)
        obs = root["obs"][start_ind:relative_idx + 1]
        # print(f"[load_chunk] loaded obs slice [{start_ind}:{relative_idx+1}] -> shape={obs.shape}", flush=True)
        if pad_length > 0:
            # print(f"[load_chunk] padding obs at front with {pad_length} frames (tile first row)", flush=True)
            obs = np.concatenate((np.tile(obs[0],(pad_length,1)), obs), axis=0)
            # print(f"[load_chunk] obs shape after pad={obs.shape}", flush=True)
        actions = root["actions"][1 + relative_idx : min(root["actions"].shape[0], 1 + relative_idx + self.chunk_size)]
        # print(f"[load_chunk] actions slice [{1+relative_idx}:{min(root['actions'].shape[0], 1+relative_idx+self.chunk_size)}] -> shape={actions.shape}", flush=True)
        if self.delta_space:
            # print("[load_chunk] delta_space=True -> actions := actions - actions[t0]", flush=True)
            actions = actions - root["actions"][relative_idx : relative_idx + actions.shape[0]]

        if self.real_robot:
            # print("[load_chunk] real_robot=True -> converting obs/actions frames", flush=True)
            o = obs
            o = np.concatenate([o[:3], gs62quat(o[3:9])])
            o = RealRobotEnv.robot_to_mujoco_pose(o)
            obs = np.concatenate([o[:3], quat2gs6(o[3:7]), [obs[9]]])

            for i in range(actions.shape[0]):
                a = actions[i]
                a = np.concatenate([a[:3], gs62quat(a[3:9])])
                a = RealRobotEnv.robot_to_mujoco_pose(a)
                actions[i] = np.concatenate([a[:3], quat2gs6(a[3:7]), [actions[i][9]]])

        actions = torch.from_numpy(np.array(actions, copy=True))
        # print(f"[load_chunk] actions torch tensor shape={tuple(actions.shape)}, dtype={actions.dtype}", flush=True)
        is_pad = torch.zeros(len(actions), dtype=torch.uint8)

        pad_length = 1 + relative_idx + self.chunk_size - root["actions"].shape[0]
        if  pad_length > 0:
            # print(f"[load_chunk] tail pad_length={pad_length} -> padding actions and is_pad", flush=True)
            actions = torch.cat((actions, torch.zeros((pad_length, actions.shape[1]))), dim=0)
            is_pad = torch.cat((is_pad, torch.ones(pad_length, dtype=torch.uint8)), dim=0)
        # print(f"[load_chunk] final actions shape={tuple(actions.shape)}, is_pad sum={int(is_pad.sum())}", flush=True)

        idx = random.randint(0, self.multiplicity - 1)
        # print(f"[load_chunk] selected view idx={idx} (multiplicity={self.multiplicity})", flush=True)
        for cam_key in self.image_keys:
            tmp = cam_key
            if self.multiplicity > 1:
                cam_key = f"{cam_key}/{idx}"
            try:
                single_view = root[cam_key][int(relative_idx)]
                # print(f"[load_chunk] loaded cam_key={cam_key} frame={int(relative_idx)} -> shape={single_view.shape}, dtype={single_view.dtype}", flush=True)

            except Exception as e:
                # print(f"\33[31m[load_chunk] Error loading {cam_key} from zarr: {e}, episode_index: {episode_id:05d}\033[0m", flush=True)
                self.download_episode(ep_path)
                single_view = root[cam_key][int(relative_idx)]
                # print(f"[load_chunk] reloaded cam_key={cam_key} frame={int(relative_idx)} after download", flush=True)
                # raise e

            _image_tensor = self.preprocess(single_view)
            # print(f"[load_chunk] preprocessed image for cam={cam_key} -> tensor shape={tuple(_image_tensor.shape)}, dtype={_image_tensor.dtype}", flush=True)
            for key in self.act_image_keys:
                if key.split("/")[0] == tmp.split("/")[0]:
                    multiview[key] = _image_tensor
                    # print(f"[load_chunk] assigned multiview[{key}] from cam group {tmp}", flush=True)

        if self.aug_camera_randomization:
            for k in self.camera_keys:
                cam_key = f"{k}/midas_depth_full"
                single_view = root[cam_key][relative_idx]
                # print(f"[load_chunk] (aug) loaded depth {cam_key} -> shape={single_view.shape}, dtype={single_view.dtype}", flush=True)
                multiview[cam_key] = self.preprocess(single_view, normalize=False)
            for k in self.camera_keys:
                Ks = root[f"{k}_K"][relative_idx]
                c2ws = root[f"{k}_C2W"][relative_idx]
                # print(f"[load_chunk] (aug) loaded {k}_K shape={Ks.shape}, {k}_C2W shape={c2ws.shape}", flush=True)
                multiview[f"{k}_K"] = torch.from_numpy(Ks.copy())
                multiview[f"{k}_C2W"] = torch.from_numpy(c2ws.copy())

        ret = dict(
            is_pad = is_pad != 0,
            observation=torch.from_numpy(np.array(obs.flatten(), copy=True)),
            actions=actions,
            **multiview,
        )
        # DEBUG: summary of return
        keys_summary = {k: (tuple(v.shape), str(v.dtype)) if isinstance(v, torch.Tensor) else "non-tensor" for k, v in ret.items()}
        # print(f"[load_chunk] return keys={list(ret.keys())}, shapes/dtypes={keys_summary}", flush=True)
        return ret

    def __getitem__(self, index):
        sample_idx, relative_idx = find_ep_id(index, self.episode_sizes)
        # cprint(f"[EpisodeDataset.__getitem__] (T:{threading.current_thread().name}) index={index} -> (ep={sample_idx}, rel={relative_idx})", "yellow")
        data = self.load_chunk(sample_idx, relative_idx)
        batch = data
        for k, v in batch.items():
            if isinstance(v, torch.Tensor) and v.dtype != torch.bool:
                # print(f"[EpisodeDataset.__getitem__] casting {k} to float (was {v.dtype})", flush=True)
                batch[k] = v.float()

        # DEBUG: final batch summary
        keys_summary = {k: (tuple(v.shape), str(v.dtype)) if isinstance(v, torch.Tensor) else type(v).__name__ for k, v in batch.items()}
        # print(f"[EpisodeDataset.__getitem__] final batch keys={list(batch.keys())}, shapes/dtypes={keys_summary}", flush=True)
        return batch


    def to(self, device):
        self.device = device
        # print(f"[EpisodeDataset.to] moved dataset device pointer to {self.device}", flush=True)
        return self

    def __len__(self):
        return sum(self.episode_sizes)

    def preprocess(self, image, normalize=True):
        # print(f"[preprocess] input np array shape={getattr(image,'shape',None)}, dtype={getattr(image,'dtype',None)}, normalize={normalize}", flush=True)
        image = torch.tensor(image, dtype=torch.float32).permute(2, 0, 1)
        # print(f"[preprocess] after tensor+permute -> shape={tuple(image.shape)}, dtype={image.dtype}", flush=True)
        image = image[:, :360, :640]  # TODO: hardcoded
        # print(f"[preprocess] after crop [:, :360, :640] -> shape={tuple(image.shape)}", flush=True)
        if normalize:
            image = image / 255.0
            # print(f"[preprocess] normalized to [0,1], dtype={image.dtype}", flush=True)
        if self.transforms is not None:
            image = self.transforms(image)
            # print(f"[preprocess] after transforms -> shape={tuple(image.shape)}, dtype={image.dtype}", flush=True)
        image = image.contiguous()
        # print(f"[preprocess] returning contiguous image shape={tuple(image.shape)}, dtype={image.dtype}", flush=True)
        return image

def load_data_combined(
        dataset_dirs,
        data_fractions,
        real_robot,
        cache_root,
        train_image_keys,
        act_image_keys,
        batch_size_train,
        batch_size_val,
        train_ratio=0.8,
        debug=False,
        lucid_mode=False,
        aug_camera_randomization=False,
        **kwargs,
):
    from ml_logger import ML_Logger

    if kwargs.get("prune_cache", False):
        cprint(f"[load_data_combined] pruning cache", "cyan")
        if Path(cache_root).exists():
            try:
                # remove everything inside cache_root, but keep the directory itself
                for child in Path(cache_root).iterdir():
                    if child.is_file() or child.is_symlink():
                        child.unlink()
                    elif child.is_dir():
                        prune_safe(child)
            except Exception as e:
                raise e

    # DEBUG:
    cprint(f"[load_data_combined] (T:{threading.current_thread().name}) start with dataset_dirs={dataset_dirs}", "cyan")
    print(f"[load_data_combined] data_fractions={data_fractions}, train_ratio={train_ratio}, debug={debug}", flush=True)

    trainsets = []
    valsets = []

    loader = ML_Logger()

    for i, data_path in enumerate(dataset_dirs[: 1 if debug else None]):
        print(f"[load_data_combined] [dir {i}] data_path={data_path}", flush=True)
        loader.configure(prefix=data_path)

        episodes = loader.glob("**/*.h5")
        print(f"[load_data_combined] [dir {i}] found {len(episodes)} .h5 episode files", flush=True)
        video_entries = loader.glob(f"videos/**/{train_image_keys[0]}.mp4")
        print(f"[load_data_combined] [dir {i}] found {len(video_entries)} matching video entries for key={train_image_keys[0]}", flush=True)
        all_entries = []
        for v in video_entries:
            ep = Path(v).parent.parent.name
            data_string = "data/" + ep + ".h5"
            if data_string in episodes:
                all_entries.append(data_string)
        fraction = data_fractions[i] if data_fractions and i < len(data_fractions) else 1.0
        print(f"[load_data_combined] [dir {i}] initial matched entries={len(all_entries)}, applying fraction={fraction}", flush=True)
        all_entries = random.sample(all_entries, int(len(all_entries) * fraction))
        all_entries = [e for e in all_entries if "ep_00084.h5" not in e]  # HACK: bad episode
        print(f"[load_data_combined] [dir {i}] entries after fraction+filter={len(all_entries)}", flush=True)
        entries_shuffled = np.random.permutation([*all_entries])
        entries_train = entries_shuffled[: int(train_ratio * len(entries_shuffled))]
        entries_eval = entries_shuffled[int(train_ratio * len(entries_shuffled)):]

        cprint(f"[load_data_combined] [dir {i}] train: {len(entries_train)}, val: {len(entries_eval)}", color="green")

        # construct dataset and dataloader
        train_dataset = EpisodeDataset(
            data_prefix=data_path,
            cache_root=cache_root,
            episode_paths=entries_train[: 1 if debug else None],
            train_image_keys = train_image_keys[i] if train_image_keys and isinstance(train_image_keys[0], list) else train_image_keys,
            real_robot=real_robot[i] if real_robot and isinstance(real_robot, list) else real_robot,
            act_image_keys=act_image_keys,
            lucid_mode=lucid_mode,
            aug_camera_randomization=aug_camera_randomization,
            **kwargs,
        )
        print(f"[load_data_combined] [dir {i}] built train_dataset len={len(train_dataset)}", flush=True)
        val_dataset = EpisodeDataset(
            data_prefix=data_path,
            cache_root=cache_root,
            episode_paths=entries_eval[: 1 if debug else None],
            train_image_keys = train_image_keys[i] if train_image_keys and isinstance(train_image_keys[0], list) else train_image_keys,
            real_robot=real_robot[i] if real_robot and isinstance(real_robot, list) else real_robot,
            act_image_keys=act_image_keys,
            lucid_mode=lucid_mode,
            aug_camera_randomization=aug_camera_randomization,
            **kwargs,
        )
        print(f"[load_data_combined] [dir {i}] built val_dataset len={len(val_dataset)}", flush=True)

        trainsets.append(train_dataset)
        valsets.append(val_dataset)

    combined_train_dataset = CombinedDataset(*trainsets)
    combined_val_dataset = CombinedDataset(*valsets)
    print(f"[load_data_combined] combined_train_dataset len={len(combined_train_dataset)}, combined_val_dataset len={len(combined_val_dataset)}", flush=True)

    train_dataloader = DataLoader(
        combined_train_dataset,
        batch_size=batch_size_train,
        shuffle=True,
        pin_memory=False,
        num_workers=0 if debug else 8,
        prefetch_factor=None if debug else 2,
        persistent_workers=not debug,
    )
    print(f"[load_data_combined] train_dataloader: batch_size={batch_size_train}, workers={0 if debug else 8}, persistent_workers={not debug}", flush=True)
    val_dataloader = DataLoader(
        combined_val_dataset,
        batch_size=batch_size_val,
        shuffle=True,
        pin_memory=False,
        num_workers=0 if debug else 8,
        prefetch_factor=None if debug else 2,
        persistent_workers=not debug,
    )
    print(f"[load_data_combined] val_dataloader: batch_size={batch_size_val}, workers={0 if debug else 8}, persistent_workers={not debug}", flush=True)

    return train_dataloader, val_dataloader

def find_ep_id(index, data_sizes):
    original_index = index
    ep_id = -1
    rel_idx = 0
    for i, length in enumerate(data_sizes):
        index -= length
        if index < 0:
            ep_id = i
            rel_idx = index + length
            break

    assert ep_id >= 0, "Index too large."

    # DEBUG:
    # cprint(f"[find_ep_id] (T:{threading.current_thread().name}) global_index={original_index} -> ep_id={ep_id}, rel_idx={rel_idx}", "cyan")
    return ep_id, rel_idx
"""One single-device training loop for all policies; paths and tensors only."""

import fcntl
import json
import logging
import math
import platform
import random
import signal
import time
from dataclasses import asdict
from pathlib import Path
from uuid import uuid4

import numpy as np
import torch
from torch.optim.swa_utils import AveragedModel, get_ema_multi_avg_fn
from torch.utils.data import DataLoader

from training.checkpoint import atomic_save, implementation, load_checkpoint, restore_rng, rng_state
from training.data.dataset import Batches, Windows
from training.data.manifest import load_manifest
from training.logging import Metrics
from training.policy import ChunkPolicy

logger = logging.getLogger(__name__)


def to_device(batch, device):
    if isinstance(batch, dict):
        return {key: to_device(value, device) for key, value in batch.items()}
    return batch.to(device, non_blocking=True)


def learning_rate(config, step):
    if step < config.warmup_steps:
        return config.learning_rate * (step + 1) / config.warmup_steps
    progress = (step - config.warmup_steps) / max(1, config.steps - config.warmup_steps - 1)
    return config.learning_rate * (1 + math.cos(math.pi * progress)) / 2


def loader(data, config, *, steps, workers, start=0, seed=None):
    return DataLoader(
        data,
        batch_sampler=Batches(
            data, config.batch_size, steps, start=start, seed=config.seed if seed is None else seed
        ),
        num_workers=workers,
        pin_memory=config.device == "cuda",
        persistent_workers=workers > 0,
        generator=torch.Generator().manual_seed(config.seed),
    )


@torch.inference_mode()
def validate(policy, batches, device, precision, seed):
    policy.eval()
    generator = torch.Generator(device=device).manual_seed(seed)
    losses = []
    for batch in batches:
        with torch.autocast(device.type, dtype=precision, enabled=precision == torch.bfloat16):
            losses.append(policy.loss(to_device(batch, device), generator)["loss"])
    return torch.stack(losses).mean().item()


def train(cache, output, config, *, resume=False, wandb_mode="disabled", project="lucidxr", stop_after=None):
    """stop_after cooperatively checkpoints at a batch boundary for recovery rehearsals."""
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    with (output / ".writer.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError(f"Another trainer owns {output}") from exc
        return _train(cache, output, config, resume, wandb_mode, project, stop_after)


def _train(cache, output, config, resume, wandb_mode, project, stop_after):
    if stop_after is not None and (type(stop_after) is not int or not 1 <= stop_after <= config.steps):
        raise ValueError("stop_after must be a positive step within the configured run")
    torch.set_num_threads(config.cpu_threads)
    random.seed(config.seed)
    np.random.seed(config.seed % (2**32))
    torch.manual_seed(config.seed)
    device = torch.device(config.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable; use device='cpu' for a local smoke run")
    # BF16 needs no loss scaler; devices without support use FP32.
    precision = torch.bfloat16 if device.type == "cuda" and torch.cuda.is_bf16_supported() else torch.float32
    manifest = load_manifest(cache, verify=True)
    spec = config.policy_spec(manifest)
    identity = {
        "config": asdict(config),
        "policy_spec": spec.to_dict(),
        "dataset": manifest["fingerprint"],
        "implementation": implementation(),
        "precision": str(precision),
    }
    # Canonical JSON makes tuple/list representations equivalent across reloads.
    identity = json.loads(json.dumps(identity))
    record_path, last = output / "run.json", output / "last.pt"
    if record_path.exists():
        record = json.loads(record_path.read_text())
        if not resume:
            raise FileExistsError("Run already exists; resume explicitly or choose a new output")
        if record["identity"] != identity:
            raise ValueError("Resume requires the same config, dataset, implementation and precision")
    else:
        if any(path.name != ".writer.lock" for path in output.iterdir()):
            raise FileExistsError("Output contains files but no recognized training run")
        record = {
            "version": 1,
            "run_id": uuid4().hex,
            "identity": identity,
            "created_at": time.time(),
            "hardware": {
                "platform": platform.platform(),
                "python": platform.python_version(),
                "device": torch.cuda.get_device_name() if device.type == "cuda" else platform.machine(),
            },
        }
        atomic_save(record_path, record)
    policy = ChunkPolicy(spec).to(device)
    stats = manifest["statistics"]
    policy.normalizer.fit(**stats, rotation_indices=manifest["contract"]["rotation_indices"])
    optimizer = torch.optim.AdamW(
        policy.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay,
        fused=device.type == "cuda",
    )

    def average(averaged, current, updates):
        # Let early EMA checkpoints learn, then approach the configured long-run decay.
        decay = min(config.ema_decay, 1 - (1 + int(updates)) ** (-2 / 3))
        get_ema_multi_avg_fn(decay)(averaged, current, updates)

    ema = AveragedModel(policy, multi_avg_fn=average, use_buffers=True)
    ema.requires_grad_(False)
    generator = torch.Generator(device=device).manual_seed(config.seed)
    step = 0
    if resume and last.exists():
        saved = load_checkpoint(last)
        if saved["identity"] != identity or saved["run_id"] != record["run_id"]:
            raise ValueError("Checkpoint does not belong to this run")
        policy.load_state_dict(saved["policy"])
        optimizer.load_state_dict(saved["optimizer"])
        ema.module.load_state_dict(saved["ema"])
        ema.n_averaged.fill_(saved["ema_updates"])
        generator.set_state(saved["noise_rng"])
        restore_rng(saved["rng"])
        step = saved["step"]
        if type(step) is not int or not 0 <= step <= config.steps:
            raise ValueError("Checkpoint has an invalid consumed-step count")
        logger.info("Resumed consumed_steps=%d checkpoint=%s", step, last)
    if step == config.steps:
        logger.info("Run already complete: %s", last)
        return last
    train_data = Windows(cache, "train", observation_steps=config.observation_steps, horizon=config.horizon)
    batches = loader(train_data, config, steps=config.steps, start=step, workers=config.workers)
    validation = None
    if any(e["split"] == "validation" for e in manifest["episodes"]):
        validation_data = Windows(
            cache, "validation", observation_steps=config.observation_steps, horizon=config.horizon
        )
        # Short periodic validation does not need a second persistent worker pool.
        validation = loader(validation_data, config, steps=config.validation_batches, seed=config.seed + 1, workers=0)
    else:
        logger.info("No held-out episodes supplied; validation metrics will be absent")
    metrics = Metrics(output, record["run_id"], identity, wandb_mode=wandb_mode, project=project)
    interrupted = False

    def request_stop(signum, frame):
        nonlocal interrupted
        interrupted = True
        logger.info("Signal %s: checkpointing after the current batch", signum)

    signals = (signal.SIGINT, signal.SIGTERM, signal.SIGUSR1)
    previous = {sig: signal.signal(sig, request_stop) for sig in signals}

    def save():
        atomic_save(
            last,
            {
                "version": 1,
                "run_id": record["run_id"],
                "identity": identity,
                "step": step,
                "policy_spec": spec.to_dict(),
                "data": manifest["data"],
                "contract": manifest["contract"],
                "policy": policy.state_dict(),
                "ema": ema.module.state_dict(),
                "ema_updates": int(ema.n_averaged),
                "optimizer": optimizer.state_dict(),
                "noise_rng": generator.get_state(),
                "rng": rng_state(),
            },
            tensor=True,
        )
        atomic_save(
            output / "status.json",
            {
                "step": step,
                "steps": config.steps,
                "state": "complete" if step == config.steps else "interrupted" if interrupted else "running",
            },
        )
        logger.info("Checkpoint saved step=%d path=%s", step, last)

    failed = True
    interval_start = time.perf_counter()
    losses, waits, iteration_count = [], 0.0, 0
    try:
        policy.train()
        iterator = iter(batches)
        while step < config.steps:
            start = time.perf_counter()
            batch = to_device(next(iterator), device)
            waits += time.perf_counter() - start
            lr = learning_rate(config, step)
            for group in optimizer.param_groups:
                group["lr"] = lr
            optimizer.zero_grad(set_to_none=True)
            with torch.autocast(device.type, dtype=precision, enabled=precision == torch.bfloat16):
                loss = policy.loss(batch, generator)["loss"]
            if not torch.isfinite(loss):
                raise FloatingPointError(f"Nonfinite loss at step {step}; last checkpoint retained")
            loss.backward()
            grad_norm = torch.nn.utils.clip_grad_norm_(
                policy.parameters(), config.gradient_clip, error_if_nonfinite=True
            )
            optimizer.step()
            ema.update_parameters(policy)
            step += 1
            iteration_count += 1
            losses.append(loss.detach())
            interrupted = interrupted or (stop_after is not None and step >= stop_after)
            boundary = step == config.steps or interrupted
            validate_now = (
                validation is not None
                and not interrupted
                and (step % config.validation_every == 0 or boundary)
            )
            checkpoint_now = step % config.checkpoint_every == 0 or boundary
            if step % config.log_every == 0 or checkpoint_now or validate_now:
                # One reporting synchronization per interval; uint8 images stay uint8 on transfer.
                mean_loss = torch.stack(losses).mean().item()
                elapsed = time.perf_counter() - interval_start
                values = {
                    "train/loss": mean_loss,
                    "train/lr": lr,
                    "train/grad_norm": grad_norm.item(),
                    "perf/samples_per_second": iteration_count * config.batch_size / elapsed,
                    "perf/batch_wait_ms": 1000 * waits / iteration_count,
                    "perf/step_ms": 1000 * elapsed / iteration_count,
                }
                if device.type == "cuda":
                    values["perf/gpu_peak_bytes"] = torch.cuda.max_memory_allocated()
                metrics.write(step, **values)
                logger.info(
                    "step=%d/%d loss=%.5f samples/s=%.1f wait_ms=%.2f",
                    step,
                    config.steps,
                    mean_loss,
                    values["perf/samples_per_second"],
                    values["perf/batch_wait_ms"],
                )
                losses, waits, iteration_count = [], 0.0, 0
                interval_start = time.perf_counter()
            if validate_now:
                value = validate(ema.module, validation, device, precision, config.seed + 2)
                metrics.write(step, **{"validation/loss": value})
                logger.info("step=%d validation_loss=%.5f", step, value)
                interval_start = time.perf_counter()
            if checkpoint_now:
                save()
                interval_start = time.perf_counter()
            if interrupted:
                break
        failed = False
        return last
    except BaseException:
        logger.exception("Training failed; resume from the last completed checkpoint: %s", last)
        raise
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)
        metrics.close(failed)

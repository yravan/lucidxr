"""Measure actual window loading, including collation and interprocess transfer."""

import argparse
import json
import time

import numpy as np
import torch
from torch.utils.data import DataLoader

from training.data.dataset import Batches, Windows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cache")
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--batches", type=int, default=100)
    parser.add_argument("--history", type=int, default=2)
    parser.add_argument("--horizon", type=int, default=16)
    args = parser.parse_args(argv)
    if args.batches < 1:
        parser.error("batches must be positive")
    torch.set_num_threads(2)
    data = Windows(args.cache, "train", observation_steps=args.history, horizon=args.horizon)
    loader = DataLoader(
        data,
        batch_sampler=Batches(data, args.batch_size, args.batches + 5),
        num_workers=args.workers,
        persistent_workers=args.workers > 0,
        pin_memory=torch.cuda.is_available(),
    )
    waits = []
    start = time.perf_counter()
    iterator = iter(loader)
    for _ in range(5):
        next(iterator)
    startup = time.perf_counter() - start
    for _ in range(args.batches):
        start = time.perf_counter()
        next(iterator)
        waits.append(time.perf_counter() - start)
    print(
        json.dumps(
            {
                "workers": args.workers,
                "batch_size": args.batch_size,
                "batches": args.batches,
                "warmup_seconds": startup,
                "samples_per_second": args.batch_size / np.mean(waits),
                "batch_wait_ms_p50": np.percentile(waits, 50) * 1000,
                "batch_wait_ms_p95": np.percentile(waits, 95) * 1000,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

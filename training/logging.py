"""JSONL is always durable local evidence; W&B receives scalar metrics only."""

import json
import logging
import time
from uuid import uuid4

logger = logging.getLogger(__name__)


class Metrics:
    def __init__(self, directory, run_id, config, *, wandb_mode="disabled", project="lucidxr"):
        self.stream = (directory / "metrics.jsonl").open("a", buffering=1)
        self.run_id, self.attempt = run_id, uuid4().hex
        self.remote = None
        self.remote_failed = False
        if wandb_mode != "disabled":
            try:
                import wandb

                # Each process attempt has its own metrics stream. Checkpoints own resume.
                self.remote = wandb.init(
                    project=project,
                    id=self.attempt,
                    group=run_id,
                    name=f"{run_id[:8]}-{self.attempt[:8]}",
                    mode=wandb_mode,
                    dir=str(directory),
                    config=config,
                    save_code=False,
                    settings=wandb.Settings(disable_git=True, init_timeout=15),
                )
                self.remote.define_metric("train/step")
                self.remote.define_metric("*", step_metric="train/step")
            except Exception:
                self.remote_failed = True
                logger.exception("W&B unavailable; continuing with local JSONL metrics")

    def write(self, step, **values):
        row = {
            "run_id": self.run_id,
            "attempt": self.attempt,
            "time": time.time(),
            "train/step": step,
            **values,
        }
        self.stream.write(json.dumps(row, allow_nan=False) + "\n")
        if self.remote is not None and not self.remote_failed:
            try:
                self.remote.log({"train/step": step, **values})
            except Exception:
                logger.exception("W&B logging failed; local metrics remain available")
                self.remote_failed = True

    def close(self, failed=False):
        self.stream.close()
        if self.remote is not None:
            try:
                self.remote.finish(exit_code=int(failed))
            except Exception:
                logger.exception("W&B close failed; local metrics remain available")

"""Decode an EMA chunk policy into native commands with correctly spaced history."""

import time
from collections import deque

import numpy as np
import torch

from training.checkpoint import load_checkpoint
from training.data.images import resize_rgb
from training.policy import ChunkPolicy, PolicySpec
from training.simulation import SimulationAdapter


class Controller:
    def __init__(self, checkpoint, env, *, execute_steps=4, device="cpu", seed=0):
        saved = load_checkpoint(checkpoint)
        self.spec = PolicySpec(**saved["policy_spec"])
        self.data, self.contract = saved["data"], saved["contract"]
        if not 1 <= execute_steps <= self.spec.model.horizon:
            raise ValueError("Execution length must fit the predicted chunk")
        if not np.isclose(env.dt, self.data["control_period"], rtol=0, atol=1e-9):
            raise ValueError("Environment control period differs from the training data")
        self.env, self.device = env, torch.device(device)
        self.policy = ChunkPolicy(self.spec).to(self.device).eval()
        self.policy.load_state_dict(saved["ema"])
        self.adapter = SimulationAdapter(
            env.model,
            self.data["joints"],
            controls=self.contract["controls"],
            state_schema=self.contract["state_schema"],
        )
        for name in self.data["cameras"]:
            env.model.camera(name)  # Resolve missing cameras before the first control step.
        self.execute_steps, self.seed = execute_steps, seed
        self.reset()

    def reset(self):
        self.history = deque(maxlen=self.spec.model.observation_steps)
        self.pending = deque()
        self.generator = torch.Generator(device=self.device).manual_seed(self.seed)
        self.last_time = None
        self.inference_seconds = []

    def action(self):
        now = self.env.data.time
        if self.last_time is not None and not np.isclose(
            now - self.last_time, self.env.dt, rtol=0, atol=1e-8
        ):
            raise ValueError(
                "Observe once per control step; reset controller history after an environment reset"
            )
        self.last_time = now
        images = np.stack(
            [
                resize_rgb(
                    self.env.rendering.image(camera, self.contract["width"], self.contract["height"]),
                    self.data["image_size"],
                )
                for camera in self.data["cameras"]
            ]
        )
        self.history.append((images, self.adapter.state(self.env.frame())))
        if not self.pending:
            missing = self.spec.model.observation_steps - len(self.history)
            history = [self.history[0]] * missing + list(self.history)
            observation = {
                "images": torch.from_numpy(np.stack([item[0] for item in history])[None]).to(self.device),
                "state": torch.from_numpy(np.stack([item[1] for item in history])[None]).to(self.device),
                "valid": torch.tensor([[False] * missing + [True] * len(self.history)], device=self.device),
            }
            start = time.perf_counter()
            chunk = self.policy.sample(observation, self.generator)[0].cpu().numpy()
            self.inference_seconds.append(time.perf_counter() - start)
            self.pending.extend(chunk[: self.execute_steps])
        return self.adapter.commands(self.pending.popleft())

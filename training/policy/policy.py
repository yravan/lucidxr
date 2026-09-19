"""One loss/sampling contract, three explicit architecture/objective combinations."""

from dataclasses import asdict, dataclass

import torch
from torch import nn

from training.models import ModelSpec, MoT, UNet

from .normalization import Normalizer
from .objectives import Diffusion, FlowMatching


@dataclass(frozen=True)
class PolicySpec:
    kind: str
    model: ModelSpec
    inference_steps: int = 16
    diffusion_steps: int = 100

    def __post_init__(self):
        if isinstance(self.model, dict):
            object.__setattr__(self, "model", ModelSpec(**self.model))
        if self.kind not in ("diffusion", "flow", "mot"):
            raise ValueError("Policy must be diffusion, flow or mot")
        if type(self.inference_steps) is not int or self.inference_steps < 1:
            raise ValueError("Inference steps must be positive")
        if type(self.diffusion_steps) is not int or self.diffusion_steps < 2:
            raise ValueError("Diffusion schedule needs at least two steps")
        if self.kind == "diffusion" and self.inference_steps > self.diffusion_steps:
            raise ValueError("Inference steps exceed the diffusion schedule")

    def to_dict(self):
        return asdict(self)


class ChunkPolicy(nn.Module):
    def __init__(self, spec: PolicySpec):
        super().__init__()
        self.spec = spec
        self.network = MoT(spec.model) if spec.kind == "mot" else UNet(spec.model)
        self.objective = Diffusion(spec.diffusion_steps) if spec.kind == "diffusion" else FlowMatching()
        self.normalizer = Normalizer(spec.model.state_dim, spec.model.action_dim)

    def condition(self, observation):
        model = self.spec.model
        images, state, valid = observation["images"], observation["state"], observation["valid"]
        if images.shape[1:] != (
            model.observation_steps,
            len(model.cameras),
            3,
            model.image_size,
            model.image_size,
        ):
            raise ValueError("Images disagree with the checkpoint's ordered camera/history specification")
        if (
            state.shape != (images.shape[0], model.observation_steps, model.state_dim)
            or valid.shape != state.shape[:2]
        ):
            raise ValueError("Observation state or mask shape mismatch")
        if valid.dtype != torch.bool:
            raise ValueError("Observation validity must be boolean")
        return self.network.condition(images, self.normalizer.normalize("state", state), valid)

    def loss(self, batch, generator=None):
        clean = self.normalizer.normalize("action", batch["actions"])
        valid = batch["action_valid"]
        if (
            clean.shape[1:] != (self.spec.model.horizon, self.spec.model.action_dim)
            or valid.shape != clean.shape[:2]
        ):
            raise ValueError("Action chunk shape mismatch")
        if valid.dtype != torch.bool or not valid.any():
            raise ValueError("Loss requires at least one valid action target")
        noisy, time, target = self.objective.corrupt(clean, generator)
        condition = self.condition(batch["obs"])
        prediction = self.network.predict(noisy, time, condition, valid)
        loss = ((prediction.float() - target).square() * valid[..., None]).sum() / (
            valid.sum() * clean.shape[-1]
        )
        return {"loss": loss}

    def forward(self, batch, generator=None):
        return self.loss(batch, generator)["loss"]

    @torch.inference_mode()
    def sample(self, observation, generator=None, *, steps=None, noise=None):
        condition = self.condition(observation)
        if noise is None:
            noise = torch.randn(
                (observation["state"].shape[0], self.spec.model.horizon, self.spec.model.action_dim),
                device=observation["state"].device,
                generator=generator,
            )
        elif noise.shape != (
            observation["state"].shape[0],
            self.spec.model.horizon,
            self.spec.model.action_dim,
        ):
            raise ValueError("Initial noise shape mismatch")

        def predict(x, t):
            return self.network.predict(x, t, condition)

        normalized = self.objective.sample(
            predict, noise, self.spec.inference_steps if steps is None else steps, generator
        )
        return self.normalizer.denormalize_actions(normalized)

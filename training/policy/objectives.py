"""Two objectives; samplers share the policy's already computed observation condition."""

import torch
from diffusers import DDIMScheduler, DDPMScheduler
from torch import nn


class Diffusion(nn.Module):
    """Epsilon DDPM loss, cosine schedule, DDIM inference with explicit step count."""

    def __init__(self, steps=100):
        super().__init__()
        self.steps = steps
        self.scheduler_config = dict(
            num_train_timesteps=steps,
            beta_schedule="squaredcos_cap_v2",
            prediction_type="epsilon",
            clip_sample=False,
        )
        self.register_buffer("alpha", DDPMScheduler(**self.scheduler_config).alphas_cumprod)

    def corrupt(self, clean, generator=None):
        noise = torch.randn(clean.shape, device=clean.device, generator=generator)
        index = torch.randint(self.steps, (clean.shape[0],), device=clean.device, generator=generator)
        alpha = self.alpha[index, None, None]
        return alpha.sqrt() * clean + (1 - alpha).sqrt() * noise, index.float() / (self.steps - 1), noise

    def sample(self, predict, noise, steps, generator=None):
        if not 1 <= steps <= self.steps:
            raise ValueError("Diffusion inference steps must be within the trained schedule")
        scheduler = DDIMScheduler(**self.scheduler_config)
        scheduler.set_timesteps(steps, device=noise.device)
        x = noise
        for index in scheduler.timesteps:
            time = (index.float() / (self.steps - 1)).expand(x.shape[0])
            x = scheduler.step(predict(x, time).float(), index, x, eta=0, generator=generator).prev_sample
        return x


class FlowMatching(nn.Module):
    """t=0 data, t=1 noise; regress noise-data and integrate backward with Euler."""

    def corrupt(self, clean, generator=None):
        noise = torch.randn(clean.shape, device=clean.device, generator=generator)
        time = torch.rand((clean.shape[0],), device=clean.device, generator=generator)
        return (1 - time[:, None, None]) * clean + time[:, None, None] * noise, time, noise - clean

    def sample(self, predict, noise, steps, generator=None):
        if type(steps) is not int or steps < 1:
            raise ValueError("Flow steps must be a positive integer")
        x = noise
        for index in range(steps):
            time = torch.full((x.shape[0],), 1 - index / steps, device=x.device)
            x = x - predict(x, time).float() / steps
        return x

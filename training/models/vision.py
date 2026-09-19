"""One randomly initialized visual trunk; no downloads or language dependencies."""

import torch
from torch import nn
from torchvision.models import resnet18


class VisionEncoder(nn.Module):
    """Encode [B,O,V,3,H,W] RGB in one trunk call, preserving time/camera axes."""

    output_dim = 512

    def __init__(self):
        super().__init__()
        backbone = resnet18(weights=None, norm_layer=lambda channels: nn.GroupNorm(32, channels))
        self.trunk = nn.Sequential(*list(backbone.children())[:-2])
        self.register_buffer("mean", torch.tensor([0.485, 0.456, 0.406])[None, :, None, None])
        self.register_buffer("std", torch.tensor([0.229, 0.224, 0.225])[None, :, None, None])

    def forward(self, images):
        if images.ndim != 6 or images.shape[3] != 3 or images.dtype != torch.uint8:
            raise ValueError("Images must be uint8 [batch,history,camera,3,height,width]")
        shape = images.shape
        pixels = images.flatten(0, 2).float().mul_(1 / 255)
        features = self.trunk((pixels - self.mean) / self.std)
        return features.reshape(*shape[:3], *features.shape[1:])

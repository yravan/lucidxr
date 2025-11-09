# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
"""
Backbone modules.
"""

import torch
import torchvision
from torch import nn
from torchvision.models._utils import IntermediateLayerGetter
from typing import List

from lucidxr.learning.act_config import ACT_Config
from lucidxr.learning.models.torch_misc import NestedTensor
from torchvision.models import ResNet18_Weights


class FrozenBatchNorm2d(torch.nn.Module):
    """
    BatchNorm2d where the batch statistics and the affine parameters are fixed.

    Copy-paste from torchvision.misc.ops with added eps before rqsrt,
    without which any other policy_models than torchvision.policy_models.resnet[18,34,50,101]
    produce nans.
    """

    def __init__(self, n):
        super(FrozenBatchNorm2d, self).__init__()
        self.register_buffer("weight", torch.ones(n))
        self.register_buffer("bias", torch.zeros(n))
        self.register_buffer("running_mean", torch.zeros(n))
        self.register_buffer("running_var", torch.ones(n))

    def _load_from_state_dict(self, state_dict, prefix, local_metadata, strict, missing_keys, unexpected_keys, error_msgs):
        num_batches_tracked_key = prefix + "num_batches_tracked"
        if num_batches_tracked_key in state_dict:
            del state_dict[num_batches_tracked_key]

        super(FrozenBatchNorm2d, self)._load_from_state_dict(
            state_dict, prefix, local_metadata, strict, missing_keys, unexpected_keys, error_msgs
        )

    def forward(self, x):
        # move reshapes to the beginning
        # to make it fuser-friendly
        w = self.weight.reshape(1, -1, 1, 1)
        b = self.bias.reshape(1, -1, 1, 1)
        rv = self.running_var.reshape(1, -1, 1, 1)
        rm = self.running_mean.reshape(1, -1, 1, 1)
        eps = 1e-5
        scale = w * (rv + eps).rsqrt()
        bias = b - rm * scale
        return x * scale + bias

# Channel-wise LayerNorm for NCHW
class LayerNorm2d(nn.Module):
    """Channel-wise LayerNorm for NCHW, with top-level weight/bias."""
    def __init__(self, C: int, eps: float = 1e-6, affine: bool = True):
        super().__init__()
        self.C = C
        self.eps = eps
        if affine:
            self.weight = nn.Parameter(torch.ones(C))
            self.bias  = nn.Parameter(torch.zeros(C))
        else:
            self.register_parameter('weight', None)
            self.register_parameter('bias', None)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Normalize over channels only, per spatial location
        # Convert to NHWC, apply layer_norm over C, convert back.
        x_perm = x.permute(0, 2, 3, 1)                      # N H W C
        x_norm = F.layer_norm(x_perm, (self.C,), self.weight, self.bias, self.eps)
        return x_norm.permute(0, 3, 1, 2)                    # N C H W

def make_norm_factory(kind: str, target_group_size: int = 16, max_groups: int = 32):
    if kind == "FrozenBatchNorm2d":
        return FrozenBatchNorm2d
    if kind == "BatchNorm2d":
        return nn.BatchNorm2d
    if kind == "GroupNorm":
        # return a callable: norm_layer(C) -> GroupNorm(G, C)
        def _gn(C: int):
            # pick groups so channels/group ≈ target_group_size and divides C
            G = min(max_groups, C)
            best = 1; gap = float("inf")
            for g in range(G, 0, -1):
                if C % g == 0:
                    cg = C // g
                    if 8 <= cg <= 32 and abs(cg - target_group_size) < gap:
                        best, gap = g, abs(cg - target_group_size)
            return nn.GroupNorm(best, C)
        return _gn
    if kind == "LayerNorm":
        # return a callable: norm_layer(C) -> LayerNorm2d(C)
        def _ln(C: int):
            return LayerNorm2d(C)
        return _ln
    raise ValueError(f"Unknown norm_layer: {kind}")

class BackboneBase(nn.Module):
    def __init__(self, input_channels:int, backbone: nn.Module, train_backbone: bool, num_channels: int, return_interm_layers: bool):
        super().__init__()
        # for name, parameter in backbone.named_parameters(): # only train later layers # TODO do we want this?
        #     if not train_backbone or 'layer2' not in name and 'layer3' not in name and 'layer4' not in name:
        #         parameter.requires_grad_(False)
        if return_interm_layers:
            return_layers = {"layer1": "0", "layer2": "1", "layer3": "2", "layer4": "3"}
        else:
            return_layers = {"layer4": "0"}
        self.input_channels = input_channels
        if input_channels != 3:
            self.preprocess = nn.Conv2d(input_channels, 3, kernel_size=1, stride=1, bias=False)
        else:
            self.preprocess = None
        self.body = IntermediateLayerGetter(backbone, return_layers=return_layers)
        self.num_channels = num_channels

    def forward(self, tensor):
        # if self.preprocess is not None:
        #     tensor = self.preprocess(tensor)
        if tensor.shape[1] == 1:
            tensor = tensor.repeat(1, 3, 1, 1)
        xs = self.body(tensor)
        return xs
        # out: Dict[str, NestedTensor] = {}
        # for name, x in xs.items():
        #     m = tensor_list.mask
        #     assert m is not None
        #     mask = F.interpolate(m[None].float(), size=x.shape[-2:]).to(torch.bool)[0]
        #     out[name] = NestedTensor(x, mask)
        # return out


class Backbone(BackboneBase):
    """ResNet backbone with frozen BatchNorm."""

    def __init__(self, input_channels: int, name: str, train_backbone: bool, pretrained:bool, return_interm_layers: bool, dilation: list):
        norm_layer = make_norm_factory(ACT_Config.norm_layer)
        if pretrained:
            w = ResNet18_Weights.IMAGENET1K_V1.get_state_dict()
            if ACT_Config.norm_layer == "FrozenBatchNorm2d" or ACT_Config.norm_layer == "BatchNorm2d":
                backbone = getattr(torchvision.models, name)(
                    replace_stride_with_dilation=dilation, weights=w, norm_layer=norm_layer
                )  # pretrained # TODO do we want frozen batch_norm??

            else:
                backbone = getattr(torchvision.models, name)(
                    replace_stride_with_dilation=dilation, weights=None, norm_layer=norm_layer
                )
                filtered = {
                    k: v
                    for k, v in w.items()
                    if not (k.endswith(".running_mean") or k.endswith(".running_var") or k.endswith(".num_batches_tracked"))
                }
                missing, unexpected = backbone.load_state_dict(filtered, strict=False)
                print("missing:", missing)  # usually empty or GN affine params if shapes differ
                print("unexpected:", unexpected)  # should be empty

        num_channels = 512 if name in ("resnet18", "resnet34") else 2048
        super().__init__(input_channels, backbone, train_backbone, num_channels, return_interm_layers)


class Joiner(nn.Sequential):
    def __init__(self, backbone, position_embedding):
        super().__init__(backbone, position_embedding)

    def forward(self, tensor_list: NestedTensor):
        xs = self[0](tensor_list)
        out: List[NestedTensor] = []
        pos = []
        for name, x in xs.items():
            out.append(x)
            # position encoding
            pos.append(self[1](x).to(x.dtype))

        return out, pos


import torch
import torch.nn as nn
import torch.nn.functional as F


class ConvGNBlock(nn.Module):
    """Conv → GroupNorm → SiLU helper."""
    def __init__(self, c_in, c_out, k=3, s=1, p=1, groups=32):
        super().__init__()
        self.conv = nn.Conv2d(c_in, c_out, k, stride=s, padding=p, bias=False)
        self.gn   = nn.GroupNorm(min(groups, c_out // 2), c_out)
        self.act  = nn.SiLU(inplace=True)

    def forward(self, x):
        return self.act(self.gn(self.conv(x)))

class SpatialSoftmax(nn.Module):
    """
    (B, C, H, W) → (B, 2 × C) expected (x,y) coordinates per channel.
    """
    def forward(self, feat):
        b, c, h, w = feat.shape

        # normalised mesh‑grid in [‑1, 1]
        xs = torch.linspace(-1.0, 1.0, w, device=feat.device)
        ys = torch.linspace(-1.0, 1.0, h, device=feat.device)
        yv, xv = torch.meshgrid(ys, xs, indexing="ij")
        grid   = torch.stack([xv, yv], dim=0)      # (2, H, W)
        grid   = grid.view(1, 2, 1, h * w)         # *** keep a dummy channel axis ***

        feat    = feat.view(b, c, h * w)           # (B, C, H*W)
        softmax = F.softmax(feat, dim=-1)

        coords = torch.sum(softmax.unsqueeze(1) * grid, dim=-1)  # (B, 2, C)
        return coords.reshape(b, 2 * c)             # (B, 2C)


class VisionEncoder(nn.Module):
    """
    360×640 RGB → latent vector for FiLM.

    Args
    ----
    embed_dim : size of output vector fed to FiLM heads
    channels  : tuple with feature sizes for each down‑sampling stage
    """
    def __init__(self, embed_dim: int = 256,
                 channels: tuple = (32, 64, 128, 256, 512)):
        super().__init__()

        c0, c1, c2, c3, c4 = channels

        self.stem = nn.Sequential(
            ConvGNBlock(3,  c0, k=5, s=2, p=2),   # 360×640 → 180×320
            ConvGNBlock(c0, c0),
        )
        self.stage1 = nn.Sequential(
            ConvGNBlock(c0, c1, s=2),             # 180×320 →  90×160
            ConvGNBlock(c1, c1),
        )
        self.stage2 = nn.Sequential(
            ConvGNBlock(c1, c2, s=2),             #  90×160 →  45×80
            ConvGNBlock(c2, c2),
        )
        self.stage3 = nn.Sequential(
            ConvGNBlock(c2, c3, s=2),             #  45×80  → ~23×40
            ConvGNBlock(c3, c3),
        )
        self.stage4 = nn.Sequential(
            ConvGNBlock(c3, c4, s=2),             # ~
            ConvGNBlock(c4, c4),
        )

        self.spatial_softmax = SpatialSoftmax()
        self.proj = nn.Linear(2 * c3, embed_dim)

    def forward(self, x):
        """
        x : (B, 3, 360, 640) uint8 or float in [0, 1]
        returns (B, embed_dim)
        """
        if x.dtype == torch.uint8:
            x = x.float() / 255.0

        x = self.stem(x)
        x = self.stage1(x)
        x = self.stage2(x)
        x = self.stage3(x)            # shape ≈ (B, C=256, 23, 40)
        x = self.stage4(x)            # shape ≈ (B, C=512, 12, 20)
        return {"0": x}

        coords = self.spatial_softmax(x)  # (B, 512)
        return {"0": self.proj(coords)}        # (B, embed_dim)

def build_vision_backbone(embed_dim):
    """
    Build a vision encoder backbone for FiLM conditioning.

    Returns
    -------
    nn.Module
        VisionEncoder instance.
    """
    return VisionEncoder(embed_dim=embed_dim, channels=(32, 64, 128, 256, 512))

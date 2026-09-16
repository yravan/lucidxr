"""Optional Gaussian-splat rendering; importing this package does not import torch."""

from .alignment import SplatAlignment
from .renderer import GsplatRenderer, SplatRenderParams

__all__ = ["SplatAlignment", "GsplatRenderer", "SplatRenderParams"]

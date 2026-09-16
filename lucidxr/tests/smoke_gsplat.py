"""Manual optional CUDA smoke: uv run --extra splat python lucidxr/tests/smoke_gsplat.py."""

from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

from lucidxr.sim.mujoco_env.splat import GsplatRenderer


def main():
    import torch

    with TemporaryDirectory() as directory:
        path = Path(directory) / "synthetic.pt"
        torch.save(
            {
                "splats": {
                    "means": torch.tensor([[0.0, 0.0, 2.0]]),
                    "quats": torch.tensor([[1.0, 0.0, 0.0, 0.0]]),
                    "scales": torch.full((1, 3), -2.0),
                    "opacities": torch.tensor([4.0]),
                    "sh0": torch.zeros((1, 1, 3)),
                    "shN": torch.zeros((1, 0, 3)),
                }
            },
            path,
        )
        renderer = GsplatRenderer(path)
        try:
            K = np.array([[50.0, 0.0, 32.0], [0.0, 50.0, 24.0], [0.0, 0.0, 1.0]])
            result = renderer.render(K, np.eye(4), 64, 48)
            assert result["rgb"].shape == (48, 64, 3)
            assert result["rgb"].dtype == np.uint8
            assert result["alpha"][24, 32] > 0.5
            assert abs(result["depth"][24, 32] - 2) < 0.1
            assert all(np.isfinite(value).all() for value in result.values())
            print("CUDA splat RGB/depth/alpha smoke passed")
        finally:
            renderer.close()


if __name__ == "__main__":
    main()

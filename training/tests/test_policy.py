"""Representation, objective direction, learnability and sampling contracts."""

import numpy as np
import pytest
from scipy.spatial.transform import Rotation

torch = pytest.importorskip("torch")
pytest.importorskip("diffusers")

from training.models import ModelSpec  # noqa: E402
from training.policy import ActionCodec, ChunkPolicy, PolicySpec  # noqa: E402
from training.policy.actions import rotation_6d_to_quaternion  # noqa: E402
from training.policy.objectives import FlowMatching  # noqa: E402


def test_command_roundtrip_and_degenerate_rotations():
    codec = ActionCodec({"actuators": [{"name": "grip", "range": [0, 1]}], "mocap_bodies": ["hand"]})
    rng = np.random.default_rng(4)
    quat = Rotation.random(8, rng=rng).as_quat()[:, [3, 0, 1, 2]].reshape(8, 1, 4)
    frame = {"ctrl": rng.uniform(0, 1, (8, 1)), "mocap_pos": rng.normal(size=(8, 1, 3)), "mocap_quat": quat}
    decoded = codec.decode(codec.encode(frame))
    np.testing.assert_allclose(decoded["ctrl"], frame["ctrl"], atol=1e-7)
    np.testing.assert_allclose(decoded["mocap_pos"], frame["mocap_pos"], atol=1e-7)
    np.testing.assert_allclose(np.abs(np.sum(decoded["mocap_quat"] * quat, axis=-1)), 1, atol=1e-7)
    degenerate = rotation_6d_to_quaternion(np.array([[0] * 6, [1, 0, 0, 3, 0, 0]], dtype=float))
    np.testing.assert_allclose(np.linalg.norm(degenerate, axis=-1), 1)
    np.testing.assert_allclose(degenerate, [[1, 0, 0, 0], [1, 0, 0, 0]])
    assert codec.decode(np.full((1, 10), 4.0))["ctrl"].item() == 1


def test_flow_integrates_noise_to_data_not_away_from_it():
    clean, noise = torch.randn(2, 4, 3), torch.randn(2, 4, 3)
    prediction = FlowMatching().sample(lambda x, t: noise - clean, noise, 8)
    torch.testing.assert_close(prediction, clean)


@pytest.mark.parametrize("kind", ["diffusion", "flow", "mot"])
def test_policy_can_learn_and_encodes_images_once_per_decision(kind):
    torch.set_num_threads(2)
    torch.manual_seed(9)
    spec = ModelSpec(5, 10, image_size=32, width=32, depth=2, horizon=4)
    policy = ChunkPolicy(PolicySpec(kind, spec, inference_steps=3))
    batch = {
        "obs": {
            "images": torch.randint(256, (2, 2, 1, 3, 32, 32), dtype=torch.uint8),
            "state": torch.randn(2, 2, 5),
            "valid": torch.ones(2, 2, dtype=torch.bool),
        },
        "actions": torch.randn(2, 4, 10),
        "action_valid": torch.tensor([[True] * 4, [True, True, False, False]]),
    }
    optimizer = torch.optim.AdamW(policy.parameters(), lr=1e-3)
    losses = []
    for _ in range(20):
        optimizer.zero_grad(set_to_none=True)
        loss = policy.loss(batch, torch.Generator().manual_seed(11))["loss"]
        assert torch.isfinite(loss)
        loss.backward()
        optimizer.step()
        losses.append(loss.detach().item())
    assert np.mean(losses[-3:]) < losses[0] * 0.6, losses
    policy.eval()
    calls = []
    hook = policy.network.vision.register_forward_hook(lambda *args: calls.append(1))
    a = policy.sample(batch["obs"], torch.Generator().manual_seed(3))
    assert len(calls) == 1
    b = policy.sample(batch["obs"], torch.Generator().manual_seed(3))
    hook.remove()
    torch.testing.assert_close(a, b)
    assert a.shape == batch["actions"].shape and torch.isfinite(a).all()
    batch["action_valid"][:] = False
    with pytest.raises(ValueError, match="valid action"):
        policy.loss(batch)

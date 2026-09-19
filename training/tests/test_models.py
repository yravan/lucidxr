"""Check the generative network boundary, MoT isolation and real cache gradients."""

import pytest

torch = pytest.importorskip("torch")

from training.models import ModelSpec, MoT, UNet  # noqa: E402


def inputs():
    spec = ModelSpec(7, 10, cameras=("left", "right"), image_size=32, width=32, depth=2, horizon=5)
    return spec, (
        torch.randn(2, 5, 10),
        torch.rand(2),
        torch.randint(256, (2, 2, 2, 3, 32, 32), dtype=torch.uint8),
        torch.randn(2, 2, 7),
        torch.tensor([[False, True], [True, True]]),
        torch.tensor([[True] * 3 + [False] * 2, [True] * 5]),
    )


def test_unet_backward_and_observation_encoding_once():
    torch.set_num_threads(2)
    spec, args = inputs()
    model = UNet(spec)
    condition = model.condition(*args[2:5])
    prediction = model.predict(args[0], args[1], condition)
    assert prediction.shape == args[0].shape
    prediction.square().mean().backward()
    assert torch.isfinite(model.vision.trunk[0].weight.grad).all()
    assert model.vision.trunk[0].weight.grad.abs().sum() > 0


def test_mot_cache_matches_joint_and_observation_parameters_receive_gradients():
    torch.set_num_threads(2)
    spec, args = inputs()
    model = MoT(spec)
    cached = model.predict(args[0], args[1], model.condition(*args[2:5]), args[5])
    joint = model(*args)
    torch.testing.assert_close(cached, joint, atol=2e-6, rtol=2e-5)
    cached.square().mean().backward()
    for name, parameter in model.named_parameters():
        if name.startswith(("vision.", "prefix_layers.")):
            assert parameter.grad is not None, name
            assert torch.isfinite(parameter.grad).all(), name
    assert model.vision.trunk[0].weight.grad.abs().sum() > 0
    # Invalid history and future action slots may not influence valid action outputs.
    changed = [x.clone() for x in args]
    changed[2][0, 0] = 255 - changed[2][0, 0]
    changed[3][0, 0] += 100
    changed[0][0, 3:] += 100
    torch.testing.assert_close(model(*changed)[0, :3], joint[0, :3], atol=2e-6, rtol=2e-5)

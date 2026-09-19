"""Atomic local checkpoints and reproducible process state, without infra imports."""

import json
import os
import random
import tempfile
from importlib.metadata import version
from pathlib import Path

import numpy as np
import torch

from training.data.manifest import file_hash, fingerprint


def implementation():
    root = Path(__file__).parent
    code = {
        p.relative_to(root).as_posix(): file_hash(p)
        for p in sorted(root.rglob("*.py"))
        if "tests" not in p.relative_to(root).parts
    }
    return {
        "code": fingerprint(code),
        "packages": {name: version(name) for name in ("torch", "torchvision", "diffusers", "numpy")},
    }


def rng_state():
    numpy_state = np.random.get_state()
    return {
        "torch": torch.get_rng_state(),
        "cuda": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else [],
        "python": random.getstate(),
        "numpy": (numpy_state[0], torch.from_numpy(numpy_state[1].copy()), *numpy_state[2:]),
    }


def restore_rng(state):
    torch.set_rng_state(state["torch"].cpu())
    if state["cuda"]:
        torch.cuda.set_rng_state_all([value.cpu() for value in state["cuda"]])
    random.setstate(state["python"])
    numpy_state = state["numpy"]
    np.random.set_state((numpy_state[0], numpy_state[1].cpu().numpy(), *numpy_state[2:]))


def atomic_save(path, value, *, tensor=False):
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            if tensor:
                torch.save(value, stream)
            else:
                stream.write(json.dumps(value, indent=2, allow_nan=False).encode())
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def load_checkpoint(path):
    # State dicts, tensors and primitive metadata only; no pickled policy objects.
    result = torch.load(path, map_location="cpu", weights_only=True)
    if result["version"] != 1:
        raise ValueError("Unsupported checkpoint format")
    return result

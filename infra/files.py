"""Small filesystem operations used by launch receipts and input staging."""

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path


def atomic_json(path, value):
    """Replace mutable local metadata only after its full contents have been flushed."""
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(json.dumps(value, indent=2, allow_nan=False).encode())
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def stage_input(source, destination, checksum):
    """Copy into an owned workspace and reject changed or truncated source bytes."""
    destination = Path(destination)
    shutil.copyfile(source, destination)
    with destination.open("rb") as stream:
        actual = hashlib.file_digest(stream, "sha256").hexdigest()
    if actual != checksum:
        raise ValueError(f"Staged input checksum mismatch: {destination}")
    return destination

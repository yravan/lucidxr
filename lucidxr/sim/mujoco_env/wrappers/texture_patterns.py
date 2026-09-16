"""Seeded color patterns on compiled textures; preserve non-color channels."""

import numpy as np

MODES = frozenset({"tint", "flat", "checker", "gradient", "noise"})


def paint(
    pixels,
    rng,
    *,
    mode,
    strength,
    face_height,
    baseline=None,
    blend=1.0,
    checker_tiles=2,
    gradient_axis="random",
    noise_probability=0.9,
):
    """Modify RGB only, in bounded row chunks. Cube patterns repeat per face.

    pixels is the compiled H x W x C view (C is 3 or 4). MuJoCo packs cube/skybox
    faces vertically, so face_height is width for those types and height for 2D.
    Patterns replace RGB; tint adds a bounded offset to the restored baseline.
    """
    height, width, channels = pixels.shape
    if channels not in (3, 4) or mode not in MODES:
        raise ValueError("Color patterns require RGB/RGBA and a supported mode")
    if mode == "tint":
        shift = np.rint(rng.uniform(-strength, strength, 3) * 255).astype(np.int16)
    else:
        colors = rng.integers(0, 256, (2, 3), dtype=np.uint8)
    if gradient_axis == "random":
        gradient_axis = rng.choice(("x", "y"))
    rows_per_chunk = max(1, 65536 // width)
    columns = np.arange(width)
    for start in range(0, height, rows_per_chunk):
        stop = min(start + rows_per_chunk, height)
        target = pixels[start:stop, :, :3]
        rows = np.arange(start, stop) % face_height
        if mode == "tint":
            # int16 is enough for [-255,510]; avoid float64-sized texture copies.
            values = target.astype(np.int16) + shift
            np.clip(values, 0, 255, out=values)
            target[:] = values
        elif mode == "flat":
            target[:] = colors[0]
        elif mode == "checker":
            parity = (
                (rows[:, None] * checker_tiles // face_height) + (columns[None, :] * checker_tiles // width)
            ) % 2
            target[:] = colors[parity.astype(np.intp)]
        elif mode == "gradient":
            weight = (
                (rows / max(face_height - 1, 1))[:, None, None]
                if gradient_axis == "y"
                else (columns / max(width - 1, 1))[None, :, None]
            ).astype(np.float32)
            target[:] = colors[0] * (1 - weight) + colors[1] * weight
        else:
            target[:] = colors[(rng.random(target.shape[:2]) < noise_probability).astype(np.intp)]

        if baseline is not None and blend < 1:
            target[:] = np.rint(target.astype(np.float32) * blend + baseline[start:stop] * (1 - blend))

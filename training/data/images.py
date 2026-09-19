"""Exactly the same RGB resizing for prepared recordings and online observations."""

import av
import numpy as np


def resize_rgb(frame, size):
    if isinstance(frame, np.ndarray):
        frame = av.VideoFrame.from_ndarray(frame, format="rgb24")
    return (
        frame.reformat(width=size, height=size, format="rgb24", interpolation="BILINEAR")
        .to_ndarray()
        .transpose(2, 0, 1)
    )

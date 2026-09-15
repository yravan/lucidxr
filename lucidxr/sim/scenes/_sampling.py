import numpy as np


def random_quat(rng):
    theta = rng.uniform(0, 2 * np.pi)
    w = np.cos(theta / 2)
    z = np.sin(theta / 2)
    return (w, 0, 0, z)

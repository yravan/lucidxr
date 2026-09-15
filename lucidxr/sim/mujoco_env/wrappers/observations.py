"""One observation path for both rollouts and restored recordings."""

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from ..control import site_poses


class ObservationWrapper(gym.ObservationWrapper):
    """Extend Gym's wrapper with a read-only observe() for offline playback."""

    def observe(self):
        return self.observation(self.env.get_wrapper_attr("observe")())


class Proprioception(ObservationWrapper):
    """Replace raw physics observations with named measured site poses and ctrl.

    Output is a flat vector under 'state', ready to combine with CameraWrapper.
    Sites are explicit and ordered; target actions remain a separate quantity.
    """

    def __init__(self, env, *, sites, relative_to=None):
        super().__init__(env)
        self.sites = tuple(sites)
        self.relative_to = dict(relative_to or {})
        site_poses(self.unwrapped.model, self.unwrapped.data, self.sites, relative_to=self.relative_to)
        for name in self.sites:
            self.unwrapped.model.site(name)
        self.observation_space = spaces.Dict(
            {
                "state": spaces.Box(
                    -np.inf, np.inf, (9 * len(self.sites) + self.unwrapped.model.nu,), dtype=np.float64
                )
            }
        )

    def observation(self, observation):
        base = self.unwrapped
        return {
            "state": np.r_[
                site_poses(base.model, base.data, self.sites, relative_to=self.relative_to), base.data.ctrl
            ]
        }

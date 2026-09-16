"""A single observation pass for rollouts and restored recordings."""

from contextlib import nullcontext

import gymnasium as gym


class ObservationWrapper(gym.ObservationWrapper):
    """Fuse adjacent compatible observation wrappers without bypassing other wrappers.

    Implement observation() normally. Built-in additive wrappers may implement
    _apply_observation() to update the pass's owned dictionary without copying it.
    """

    def __init__(self, env):
        super().__init__(env)
        self.base = env.unwrapped
        if (
            isinstance(env, ObservationWrapper)
            and getattr(env.reset, "__func__", None) is ObservationWrapper.reset
            and getattr(env.step, "__func__", None) is ObservationWrapper.step
            and getattr(env.observe, "__func__", None) is ObservationWrapper.observe
        ):
            self._source = env._source
            self._transforms = (*env._transforms, self._apply_observation)
        else:
            self._source = env
            self._transforms = (self._apply_observation,)
        self._read = self._source.get_wrapper_attr("observe")
        self._uses_rendering = any(getattr(t.__self__, "uses_rendering", False) for t in self._transforms)

    def _apply_observation(self, observation):
        return self.observation(observation)

    def _transform(self, observation):
        result = dict(observation) if isinstance(observation, dict) else observation
        # Only image wrappers create a renderer. The batch never survives a read.
        batch = self.base.rendering.batch() if self._uses_rendering else nullcontext()
        with batch:
            for transform in self._transforms:
                result = transform(result)
        return result

    def observe(self):
        return self._transform(self._read())

    def reset(self, *, seed=None, options=None):
        observation, info = self._source.reset(seed=seed, options=options)
        return self._transform(observation), info

    def step(self, action):
        observation, reward, terminated, truncated, info = self._source.step(action)
        return self._transform(observation), reward, terminated, truncated, info

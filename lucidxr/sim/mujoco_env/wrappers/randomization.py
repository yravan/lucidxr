"""Shared lifecycle for independently composable model randomizers."""

from abc import ABC, abstractmethod

import gymnasium as gym
import numpy as np


class RandomizationWrapper(gym.Wrapper, ABC):
    """Sample on reset or explicit randomize(); observation reads never resample.

    Subclasses declare model fields and implement sample(). Each sample starts
    from the captured baseline. Stack these inside image observation wrappers.
    The environment RNG seeds the entire stack, in inner-to-outer reset order.
    """

    def __init__(self, env, *, fields, textures_changed=False):
        super().__init__(env)
        self.base = env.unwrapped
        self._indices = dict(fields) if isinstance(fields, dict) else {name: slice(None) for name in fields}
        self._defaults = {
            name: getattr(self.base.model, name)[index].copy() for name, index in self._indices.items()
        }
        self._textures_changed = textures_changed
        if (
            isinstance(env, RandomizationWrapper)
            and getattr(env.reset, "__func__", None) is RandomizationWrapper.reset
            and getattr(env.step, "__func__", None) is RandomizationWrapper.step
            and getattr(env.observe, "__func__", None) is RandomizationWrapper.observe
            and getattr(env.close, "__func__", None) is RandomizationWrapper.close
        ):
            self._source = env._source
            self._randomizers = (*env._randomizers, self)
        else:
            self._source = env
            self._randomizers = (self,)
        self._read = self._source.get_wrapper_attr("observe")

    @staticmethod
    def validate_scales(**scales):
        for name, value in scales.items():
            if not np.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and nonnegative")

    def _restore_model(self):
        for name, value in self._defaults.items():
            getattr(self.base.model, name)[self._indices[name]] = value

    def _refresh(self):
        self.base.refresh_model(textures_changed=self._textures_changed)

    def restore(self):
        self._restore_model()
        self._refresh()

    def randomize(self):
        self._restore_model()
        try:
            self.sample(self.base.np_random)
        except Exception:
            self.restore()
            raise
        self._refresh()

    @abstractmethod
    def sample(self, rng):
        """Modify owned model fields using rng; called after restoring defaults."""

    def perturb(self, rng, field, scale, *, bounds=None):
        target = getattr(self.base.model, field)
        baseline = self._defaults[field]
        value = baseline + rng.uniform(-scale, scale, baseline.shape)
        target[self._indices[field]] = np.clip(value, *bounds) if bounds is not None else value

    def reset(self, *, seed=None, options=None):
        for wrapper in self._randomizers:
            wrapper._restore_model()
        _, info = self._source.reset(seed=seed, options=options)
        try:
            for wrapper in self._randomizers:
                wrapper.sample(self.base.np_random)
        except Exception:
            for wrapper in self._randomizers:
                wrapper._restore_model()
            raise
        finally:
            self.base.refresh_model(textures_changed=any(w._textures_changed for w in self._randomizers))
        return self.observe(), info

    def step(self, action):
        return self._source.step(action)

    def observe(self):
        return self._read()

    def close(self):
        try:
            for wrapper in self._randomizers:
                wrapper._restore_model()
            self.base.refresh_model(textures_changed=any(w._textures_changed for w in self._randomizers))
        finally:
            self._source.close()

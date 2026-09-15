"""Shared lifecycle for independently composable model randomizers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

import gymnasium as gym
import numpy as np


@dataclass(frozen=True, kw_only=True)
class RandomizationParams:
    """Shared sampling schedule; None disables periodic sampling."""

    on_reset: bool = True
    every_n_steps: int | None = None

    def __post_init__(self):
        if type(self.on_reset) is not bool:
            raise TypeError("on_reset must be bool")
        if self.every_n_steps is not None and (type(self.every_n_steps) is not int or self.every_n_steps < 1):
            raise ValueError("every_n_steps must be a positive integer or None")


class RandomizationWrapper(gym.Wrapper, ABC):
    """Sample on reset, configured steps, or explicit randomize(); reads never resample.

    Subclasses declare model fields and implement sample(). Each sample starts
    from the captured baseline. Stack these inside image observation wrappers.
    The environment RNG seeds the entire stack, in inner-to-outer reset order.
    """

    def __init__(self, env, *, fields, texture_ids=(), params=None):
        super().__init__(env)
        self.params = params or RandomizationParams()
        self._step_count = 0
        self.base = env.unwrapped
        self._indices = dict(fields) if isinstance(fields, dict) else {name: slice(None) for name in fields}
        self._defaults = {
            name: getattr(self.base.model, name)[index].copy() for name, index in self._indices.items()
        }
        self._texture_ids = tuple(texture_ids)
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
        self._scheduled = tuple(w for w in self._randomizers if w.params.every_n_steps is not None)

    @staticmethod
    def parameters(value, expected):
        if value is None:
            return expected()
        if not isinstance(value, expected):
            raise TypeError(f"params must be {expected.__name__}")
        return value

    @staticmethod
    def validate_scales(**scales):
        for name, value in scales.items():
            if not np.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and nonnegative")

    def _restore_model(self):
        for name, value in self._defaults.items():
            getattr(self.base.model, name)[self._indices[name]] = value

    def _refresh(self):
        self.base.refresh_model(texture_ids=self._texture_ids)

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

    @staticmethod
    def _texture_union(wrappers):
        return tuple(sorted({index for wrapper in wrappers for index in wrapper._texture_ids}))

    def _sample_batch(self, wrappers):
        for wrapper in wrappers:
            wrapper._restore_model()
        try:
            for wrapper in wrappers:
                wrapper.sample(self.base.np_random)
        except Exception:
            for wrapper in wrappers:
                wrapper._restore_model()
            raise
        finally:
            if wrappers:
                self.base.refresh_model(texture_ids=self._texture_union(wrappers))

    def reset(self, *, seed=None, options=None):
        self._step_count = 0
        for wrapper in self._randomizers:
            wrapper._restore_model()
        _, info = self._source.reset(seed=seed, options=options)
        enabled = tuple(w for w in self._randomizers if w.params.on_reset)
        # Refresh also covers restored textures on wrappers with sampling disabled.
        try:
            for wrapper in enabled:
                wrapper.sample(self.base.np_random)
        except Exception:
            for wrapper in self._randomizers:
                wrapper._restore_model()
            raise
        finally:
            self.base.refresh_model(texture_ids=self._texture_union(self._randomizers))
        return self.observe(), info

    def step(self, action):
        if self._scheduled:
            self._sample_batch(
                tuple(w for w in self._scheduled if self._step_count % w.params.every_n_steps == 0)
            )
        result = self._source.step(action)
        self._step_count += 1
        return result

    def observe(self):
        return self._read()

    def close(self):
        try:
            for wrapper in self._randomizers:
                wrapper._restore_model()
            self.base.refresh_model(texture_ids=self._texture_union(self._randomizers))
        finally:
            self._source.close()

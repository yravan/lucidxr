"""Add named camera observations to native physics observations."""

from gymnasium import spaces

from .camera_view import Camera, CameraView, body_geoms, depth_image
from .observations import ObservationWrapper

__all__ = ["Camera", "CameraWrapper", "body_geoms", "depth_image"]


class CameraWrapper(ObservationWrapper):
    """One view per configuration; capture identically during rollouts and replay."""

    uses_rendering = True

    def __init__(self, env, cameras):
        super().__init__(env)
        if not isinstance(env.observation_space, spaces.Dict):
            raise TypeError("CameraWrapper requires a Dict observation space")
        self.views = tuple(CameraView(self.base.model, camera) for camera in cameras)
        entries = dict(env.observation_space.spaces)
        keys = set()
        for view in self.views:
            if view.key in keys:
                raise ValueError(f"Duplicate camera output key {view.key}")
            keys.add(view.key)
            overlap = entries.keys() & view.spaces.keys()
            if overlap:
                raise ValueError(f"Duplicate observation keys: {sorted(overlap)}")
            entries.update(view.spaces)
        self.observation_space = spaces.Dict(entries)

    def observation(self, observation):
        return self._apply_observation(dict(observation))

    def _apply_observation(self, observation):
        for view in self.views:
            observation.update(view.capture(self.base.rendering))
        return observation

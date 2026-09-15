"""Native MuJoCo environments built from LucidXR Scenes."""

from .env import Episode, MujocoEnv

__all__ = ["Episode", "MujocoEnv", "make_env"]


def make_env(scene, *, scene_options=None, max_episode_steps=None, **kwargs):
    """Accept a Scene or catalogue name; optionally apply Gymnasium TimeLimit."""
    from lucidxr.sim.scenes import make_scene

    if isinstance(scene, str):
        scene = make_scene(scene, **(scene_options or {}))
    elif scene_options:
        raise ValueError("Pass scene_options only with a catalogue name")
    env = MujocoEnv(scene, **kwargs)
    if max_episode_steps is not None:
        from gymnasium.wrappers import TimeLimit

        env = TimeLimit(env, max_episode_steps=max_episode_steps)
    return env

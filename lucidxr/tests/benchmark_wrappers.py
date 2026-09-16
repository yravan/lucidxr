"""Manual wrapper overhead benchmark; run with uv run python lucidxr/tests/benchmark_wrappers.py."""

import runpy
from pathlib import Path
from statistics import median
from time import perf_counter

from lucidxr.sim.mujoco_env import MujocoEnv
from lucidxr.sim.mujoco_env.wrappers import Camera, CameraWrapper, LightingRandomization, ObservationWrapper

MiniScene = runpy.run_path(str(Path(__file__).with_name("test_mujoco_env.py")))["MiniScene"]


class Identity(ObservationWrapper):
    def observation(self, obs):
        return obs


def benchmark(kind, count, steps):
    base = MujocoEnv(MiniScene(), frame_skip=1)
    env = base
    for i in range(count):
        if kind == "identity":
            env = Identity(env)
        elif kind == "randomization":
            env = LightingRandomization(env)
        else:
            env = CameraWrapper(
                env, [Camera("view", key=f"view_{i}", width=64, height=48, calibration=False)]
            )
    try:
        env.reset(seed=4)
        action = base.current_action()
        for _ in range(5):
            env.step(action)
        samples = []
        for _ in range(5):
            t = perf_counter()
            for _ in range(steps):
                env.step(action)
            samples.append((perf_counter() - t) / steps * 1e6)
        print(kind, count, f"{median(samples):.1f} us/step", flush=True)
    finally:
        env.close()


if __name__ == "__main__":
    benchmark("identity", 0, 500)
    benchmark("identity", 100, 500)
    benchmark("randomization", 100, 500)
    benchmark("camera", 1, 50)
    benchmark("camera", 100, 50)

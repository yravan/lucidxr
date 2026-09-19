"""Named policy state/commands survive different scene layouts and native stepping."""

import numpy as np
import pytest

pytest.importorskip("torch")
pytest.importorskip("diffusers")

from lucidxr.sim.mujoco_env import MujocoEnv  # noqa: E402
from lucidxr.sim.scenes import make_scene  # noqa: E402
from training.simulation import SimulationAdapter  # noqa: E402


def test_named_robot_state_and_native_command_roundtrip_across_scenes():
    joints = ["gripper-float-floating-base", "gripper-right_driver_joint", "gripper-left_driver_joint"]
    controls = schema = None
    for name in ("pick_block", "pick_sphere"):
        env = MujocoEnv(make_scene(name, seed=9))
        try:
            env.reset()
            adapter = SimulationAdapter(env.model, joints, controls=controls, state_schema=schema)
            controls, schema = adapter.codec.controls, adapter.state_schema
            frame = env.frame()
            expected = adapter.state(frame)
            # These models place an object joint before the selected robot joints.
            frame["qpos"][:3] += 3
            frame["qvel"][:3] += 4
            np.testing.assert_array_equal(adapter.state(frame), expected)
            native = env.current_action()
            for index in range(25):
                command = {key: value.copy() for key, value in native.items()}
                command["mocap_pos"][0, 0] += 0.01 * np.sin(index / 10)
                encoded = adapter.action(command)
                decoded = adapter.commands(encoded)
                for key in command:
                    np.testing.assert_allclose(decoded[key], command[key], atol=1e-7)
                env.step(decoded)
            assert np.isfinite(adapter.state(env.frame())).all()
        finally:
            env.close()

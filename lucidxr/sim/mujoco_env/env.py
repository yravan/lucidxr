"""A Scene-backed Gymnasium environment using native MuJoCo."""

import gymnasium as gym
import mujoco
import numpy as np
from gymnasium import spaces

from lucidxr.sim.scenes.base import Scene

from .control import ActuatorControl, actuator_space

FRAME_FIELDS = ("qpos", "qvel", "act", "ctrl", "mocap_pos", "mocap_quat")


class Episode:
    """Override initialization/evaluation for an objective; defaults to free rollout.

    evaluate returns (reward, terminated, info) and must be read-only. Stateful
    success tracking belongs in after_step, which playback never calls.
    """

    def reset(self, env):
        pass

    def after_step(self, env):
        pass

    def evaluate(self, env):
        return 0.0, False, {}


class MujocoEnv(gym.Env):
    """Compile a Scene once. Own simulation state, control timing and rendering.

    Use MocapControl for floating rigs, otherwise actions directly set actuators.
    Scene.seed controls construction; reset(seed=...) seeds episode sampling.
    Wrap with Gymnasium TimeLimit to impose a maximum number of control steps.
    """

    metadata = {"render_modes": ["human", "rgb_array", "depth_array"]}

    def __init__(
        self,
        scene: Scene,
        *,
        control=None,
        episode=None,
        frame_skip=10,
        settle_steps=0,
        render_mode=None,
        camera=-1,
        width=640,
        height=360,
    ):
        if not isinstance(scene, Scene):
            raise TypeError("scene must be a Scene instance")
        if not isinstance(frame_skip, int) or frame_skip < 1:
            raise ValueError("frame_skip must be a positive integer")
        if not isinstance(settle_steps, int) or settle_steps < 0:
            raise ValueError("settle_steps must be a nonnegative integer")
        if render_mode is not None and render_mode not in self.metadata["render_modes"]:
            raise ValueError(f"Unsupported render_mode: {render_mode}")
        self.scene = scene
        self.model = scene.compile()
        self.data = mujoco.MjData(self.model)
        self.control = control if control is not None else ActuatorControl()
        self.episode = episode if episode is not None else Episode()
        self.frame_skip, self.settle_steps = frame_skip, settle_steps
        self.render_mode = render_mode
        self.camera, self.width, self.height = camera, width, height
        self.metadata = {**self.metadata, "render_fps": max(1, round(1 / self.dt))}
        self.action_space = self.control.bind(self.model)
        self.observation_space = spaces.Dict(
            {
                name: spaces.Box(-np.inf, np.inf, getattr(self.data, name).shape, dtype=np.float64)
                for name in (*FRAME_FIELDS, "sensordata")
            }
        )
        self._rendering = None
        self._ready = False

    @property
    def dt(self):
        return self.model.opt.timestep * self.frame_skip

    def observe(self):
        """Read current state without advancing physics or episode bookkeeping."""
        return {name: getattr(self.data, name).copy() for name in self.observation_space.spaces}

    def current_action(self):
        """Encode current commanded targets/ctrl, not measured end-effector poses."""
        return self.control.encode(self.model, self.data)

    def frame(self):
        """Portable recording fields; derived quantities are recomputed on restore."""
        return {name: getattr(self.data, name).copy() for name in FRAME_FIELDS}

    def restore_frame(self, frame):
        """Apply a partial recorded frame atomically, with exact shapes and no step."""
        unknown = set(frame) - set(FRAME_FIELDS)
        if unknown:
            raise ValueError(f"Unsupported frame fields: {sorted(unknown)}")
        values = {}
        for name, value in frame.items():
            value = np.asarray(value, dtype=np.float64)
            if value.shape != getattr(self.data, name).shape or not np.isfinite(value).all():
                raise ValueError(f"Invalid {name}: expected finite shape {getattr(self.data, name).shape}")
            if name == "mocap_quat" and np.any(np.linalg.norm(value, axis=-1) < 1e-8):
                raise ValueError("mocap quaternions must be nonzero")
            values[name] = value.copy()
        for name, value in values.items():
            getattr(self.data, name)[:] = value
        mujoco.mj_normalizeQuat(self.model, self.data.qpos)
        if "mocap_quat" in values:
            self.data.mocap_quat[:] /= np.linalg.norm(self.data.mocap_quat, axis=-1, keepdims=True)
        mujoco.mj_forward(self.model, self.data)

    def snapshot(self):
        """MuJoCo integration state for this model (not wrapper/RNG/episode state)."""
        spec = mujoco.mjtState.mjSTATE_INTEGRATION
        state = np.empty(mujoco.mj_stateSize(self.model, spec))
        mujoco.mj_getState(self.model, self.data, state, spec)
        return state

    def restore_snapshot(self, state):
        spec = mujoco.mjtState.mjSTATE_INTEGRATION
        state = np.asarray(state, dtype=np.float64)
        if state.shape != (mujoco.mj_stateSize(self.model, spec),) or not np.isfinite(state).all():
            raise ValueError("Invalid integration state for this model")
        mujoco.mj_setState(self.model, self.data, state, spec)
        mujoco.mj_forward(self.model, self.data)
        # Forward updates warmstart; preserve the snapshot's integration inputs.
        mujoco.mj_setState(self.model, self.data, state, spec)

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        options = dict(options or {})
        unknown = set(options) - {"keyframe", "frame"}
        if unknown:
            raise ValueError(f"Unknown reset options: {sorted(unknown)}")
        if "keyframe" in options:
            key = options["keyframe"]
            key = self.model.key(key).id if isinstance(key, str) else key
            if not isinstance(key, (int, np.integer)) or not 0 <= key < self.model.nkey:
                raise ValueError("Invalid keyframe")
            mujoco.mj_resetDataKeyframe(self.model, self.data, key)
        else:
            mujoco.mj_resetData(self.model, self.data)
            limits = actuator_space(self.model)
            self.data.ctrl[:] = np.clip(self.data.ctrl, limits.low, limits.high)
        self.episode.reset(self)
        if "frame" in options:
            self.restore_frame(options["frame"])
        mujoco.mj_forward(self.model, self.data)
        if self.settle_steps:
            self._advance(self.settle_steps)
            self.data.time = 0
            mujoco.mj_forward(self.model, self.data)
        self._ready = True
        if self.render_mode == "human":
            self.render()
        return self.observe(), {}

    def step(self, action):
        if not self._ready:
            raise gym.error.ResetNeeded("Call reset() before step()")
        action = np.asarray(action, dtype=np.float64)
        if not self.action_space.contains(action) or not np.isfinite(action).all():
            raise ValueError("Action must be finite and inside action_space")
        self.control.apply(self.model, self.data, action)
        self._advance(self.frame_skip)
        mujoco.mj_forward(self.model, self.data)
        if not np.isfinite(self.data.qpos).all() or not np.isfinite(self.data.qvel).all():
            raise FloatingPointError("MuJoCo produced nonfinite state")
        self.episode.after_step(self)
        reward, terminated, info = self.episode.evaluate(self)
        if self.render_mode == "human":
            self.render()
        return self.observe(), float(reward), bool(terminated), False, dict(info)

    def _advance(self, count):
        expected_time = self.data.time + count * self.model.opt.timestep
        indices = [
            int(mujoco.mjtWarning.mjWARN_BADQPOS),
            int(mujoco.mjtWarning.mjWARN_BADQVEL),
            int(mujoco.mjtWarning.mjWARN_BADQACC),
        ]
        before = self.data.warning.number[indices].copy()
        mujoco.mj_step(self.model, self.data, nstep=count)
        if np.any(self.data.warning.number[indices] > before) or not np.isclose(
            self.data.time, expected_time, rtol=1e-8, atol=1e-10
        ):
            self._ready = False
            raise FloatingPointError("MuJoCo detected unstable physics; reset before continuing")

    @property
    def rendering(self):
        if self._rendering is None:
            from .rendering import Rendering

            self._rendering = Rendering(self.model, self.data)
        return self._rendering

    def render(self):
        if self.render_mode is None:
            return None
        if self.render_mode == "human":
            return self.rendering.show()
        mode = "rgb" if self.render_mode == "rgb_array" else "depth"
        return self.rendering.image(self.camera, self.width, self.height, mode=mode)

    def close(self):
        if self._rendering is not None:
            self._rendering.close()
            self._rendering = None

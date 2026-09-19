"""Shared state restoration and command replay for viewers and offline rendering."""

from dataclasses import asdict, dataclass, field

import mujoco
import numpy as np

from .scenes import make_scene


def control_layout(model):
    """Names identify controls across models; ranges/gear preserve their interpretation."""
    mocaps = [None] * model.nmocap
    for body in range(model.nbody):
        index = model.body_mocapid[body]
        if index >= 0:
            mocaps[index] = model.body(body).name
    objects = {
        mujoco.mjtTrn.mjTRN_JOINT: mujoco.mjtObj.mjOBJ_JOINT,
        mujoco.mjtTrn.mjTRN_JOINTINPARENT: mujoco.mjtObj.mjOBJ_JOINT,
        mujoco.mjtTrn.mjTRN_TENDON: mujoco.mjtObj.mjOBJ_TENDON,
        mujoco.mjtTrn.mjTRN_SITE: mujoco.mjtObj.mjOBJ_SITE,
        mujoco.mjtTrn.mjTRN_SLIDERCRANK: mujoco.mjtObj.mjOBJ_SITE,
        mujoco.mjtTrn.mjTRN_BODY: mujoco.mjtObj.mjOBJ_BODY,
    }
    objects = {int(kind): value for kind, value in objects.items()}
    return {
        "mocap_bodies": mocaps,
        "actuators": [
            {
                "name": model.actuator(i).name,
                "transmission": int(model.actuator_trntype[i]),
                "targets": [
                    mujoco.mj_id2name(model, objects[model.actuator_trntype[i]], int(target))
                    if target >= 0
                    else None
                    for target in model.actuator_trnid[i]
                ],
                "gear": model.actuator_gear[i].tolist(),
                "range": model.actuator_ctrlrange[i].tolist() if model.actuator_ctrllimited[i] else None,
            }
            for i in range(model.nu)
        ],
    }


@dataclass(frozen=True)
class ReplaySpec:
    mode: str = "state"
    scene: str | None = None
    seed: int = 0
    options: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.mode not in ("state", "commands"):
            raise ValueError("Replay mode must be state or commands")
        if self.mode == "state" and self.scene is not None:
            raise ValueError("A different scene requires command replay")
        if self.scene is None and (self.seed != 0 or self.options):
            raise ValueError("Target seed/options require an explicit target scene")
        if not isinstance(self.options, dict) or {"assets", "seed"} & self.options.keys():
            raise ValueError("Scene options must be an object without assets/seed")

    def to_dict(self):
        return asdict(self)

    def make_scene(self, demo, *, assets=None):
        if self.scene is None:
            return demo.scene(assets=assets)
        return make_scene(self.scene, assets=assets, seed=self.seed, **self.options)


def _mapping(source, target, label):
    if any(not name for name in (*source, *target)):
        raise ValueError(f"Command replay requires named {label}")
    if len(set(source)) != len(source) or set(source) != set(target):
        raise ValueError(f"Incompatible {label}: source={source}, target={target}")
    return np.asarray([source.index(name) for name in target], dtype=int)


def command_mapping(demo, model):
    recorded = demo.metadata.get("controls")
    if not recorded:
        raise ValueError("Recording has no named control layout; collect a version-2 demo")
    return control_mapping(recorded, model)


def control_mapping(recorded, model):
    """Map a named command layout to a compiled model, preserving actuator meaning."""
    target = control_layout(model)
    actuators = _mapping(
        [a["name"] for a in recorded["actuators"]], [a["name"] for a in target["actuators"]], "actuators"
    )
    mocaps = _mapping(recorded["mocap_bodies"], target["mocap_bodies"], "mocap bodies")
    for i, source in enumerate(actuators):
        if recorded["actuators"][source] != target["actuators"][i]:
            raise ValueError(f"Actuator interpretation differs: {target['actuators'][i]['name']}")
    return actuators, mocaps


def replay_frames(env, demo, spec=ReplaySpec()):
    """Yield indices with env ready to observe; display speed never changes physics.

    Commands at frame i drive the interval ending at i. State 0 is the initial
    condition for same-scene replay; explicit target scenes keep their own reset.
    """
    if spec.scene is None:
        from .demos import scene_fingerprint

        if scene_fingerprint(env.scene) != demo.metadata["scene_fingerprint"]:
            raise ValueError("Playback model differs from the recorded scene")
    if spec.mode == "state":
        for name, frames in demo.frames.items():
            if frames.shape[1:] != getattr(env.data, name).shape:
                raise ValueError(f"Recording {name} does not match the model")
        for index in range(len(demo.elapsed)):
            env.data.time = float(demo.times[index])
            env.restore_frame(demo.frame(index))
            yield index
        return
    if demo.metadata.get("timing") != "simulation-seconds":
        raise ValueError("Command replay requires simulation timestamps")
    if demo.metadata.get("command_alignment") != "interval-ending-at-frame":
        raise ValueError("Recording does not specify command application timing")
    actuators, mocaps = command_mapping(demo, env.model)
    intervals = np.diff(demo.elapsed) / env.model.opt.timestep
    steps = np.rint(intervals).astype(np.int64)
    if np.any(steps < 1) or not np.allclose(intervals, steps, rtol=0, atol=1e-6):
        raise ValueError("Recorded intervals must be integer multiples of the target physics timestep")
    if spec.scene is None:
        env.data.time = float(demo.times[0])
        env.restore_frame(demo.frame(0))
    else:
        for name in env.action_space.spaces:
            order = actuators if name == "ctrl" else mocaps
            getattr(env.data, name)[:] = demo.frames[name][0][order]
        mujoco.mj_forward(env.model, env.data)
    yield 0
    for index, count in enumerate(steps, 1):
        action = {
            name: demo.frames[name][index][actuators if name == "ctrl" else mocaps]
            for name in env.action_space.spaces
        }
        env.advance(action, steps=int(count))
        yield index

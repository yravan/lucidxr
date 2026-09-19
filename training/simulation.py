"""The optional simulation boundary shared by data preparation and policy rollout."""

import mujoco
import numpy as np

from lucidxr.sim.playback import control_layout, control_mapping
from training.policy.actions import ActionCodec, quaternion_to_6d


class SimulationAdapter:
    """Resolve explicit robot joint/control names once, never flatten object state."""

    def __init__(self, model, joints, *, controls=None, state_schema=None):
        if not joints or len(set(joints)) != len(joints):
            raise ValueError("Select unique measured robot joints explicitly")
        self.codec = ActionCodec(control_layout(model) if controls is None else controls)
        self.actuators, self.mocaps = control_mapping(self.codec.controls, model)
        self.inverse_actuators, self.inverse_mocaps = np.argsort(self.actuators), np.argsort(self.mocaps)
        self.joints, self.state_schema = [], []
        dimension = 0
        for name in joints:
            joint = model.joint(name)
            kind = int(model.jnt_type[joint.id])
            # MuJoCo joint types: free, ball, slide, hinge.
            nq, nv, encoded = {0: (7, 6, 9), 1: (4, 3, 6), 2: (1, 1, 1), 3: (1, 1, 1)}[kind]
            q, v = int(model.jnt_qposadr[joint.id]), int(model.jnt_dofadr[joint.id])
            self.joints.append((kind, slice(q, q + nq), slice(v, v + nv)))
            self.state_schema.append({"name": name, "type": kind})
            dimension += encoded + nv
        if state_schema is not None and self.state_schema != state_schema:
            raise ValueError("Robot joint types differ from the training state schema")
        self.state_dim = dimension

    def state(self, frame):
        values = []
        for kind, q, v in self.joints:
            position = np.asarray(frame["qpos"])[..., q]
            if kind == int(mujoco.mjtJoint.mjJNT_FREE):
                position = np.concatenate((position[..., :3], quaternion_to_6d(position[..., 3:])), axis=-1)
            elif kind == int(mujoco.mjtJoint.mjJNT_BALL):
                position = quaternion_to_6d(position)
            values.extend((position, np.asarray(frame["qvel"])[..., v]))
        state = np.concatenate(values, axis=-1).astype(np.float32)
        if not np.isfinite(state).all():
            raise ValueError("Measured robot state must be finite")
        return state

    def action(self, frame):
        return self.codec.encode(
            {
                "ctrl": np.asarray(frame["ctrl"])[..., self.inverse_actuators],
                "mocap_pos": np.asarray(frame["mocap_pos"])[..., self.inverse_mocaps, :],
                "mocap_quat": np.asarray(frame["mocap_quat"])[..., self.inverse_mocaps, :],
            }
        )

    def commands(self, action):
        decoded = self.codec.decode(action)
        # The environment includes ctrl even for models with zero actuators.
        decoded.setdefault("ctrl", np.empty((*np.asarray(action).shape[:-1], 0)))
        return {
            key: value[..., self.actuators] if key == "ctrl" else value[..., self.mocaps, :]
            for key, value in decoded.items()
        }

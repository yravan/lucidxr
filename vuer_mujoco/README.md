# vuer MuJoCo Environments for Lucid-XR

State observation contains the `[position, gram-schmidt 6D pose]` of the gripper pose.
Action space is the same `3 + 6` vector, corresponding to the mocap pose.

| **Name**     | **Description**                                    | **Observation Space** | **Action Space** | **Success** |
|--------------|----------------------------------------------------|-----------------------|------------------|-------------|
| `pick_block` | Pick up a block .                                  | 3D image of the scene | 3D action vector | 0.5         |
| `pick_place` | Pick up a block and place it in a target location. | 3D image of the scene | 3D action vector | 0.5         |
| `flip_mug`   | Flip a mug over.                                   | 3D image of the scene | 3D action vector | 0.5         |

This codebase comes with two sets of helper functions:

```python
import vuer_mujoco as vm

env = vm.make("Pick_place-v1")

print(env)
```
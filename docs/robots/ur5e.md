
# Xarm7 and Ufactory Gripper

Here is a simple scene with the xarm7 and the ufactory gripper.

```python
from vuer_envs import UR5e, DefaultStage, Robotiq2F85
from vuer_envs.schemas.utils import Save, Prettify
```
```python
def build_ur5e():
    """here we create a scene with a single uR5e arm (no gripper)."""

    ur5e = UR5e(name="ur5e", assets="ur5e")
    # ur5e._xml | Prettify() | Save("ur5e.mjcf.xml")

    scene = DefaultStage(model="ur5e", children=ur5e)
    scene._xml | Prettify() | Save("ur5e.mjcf.xml")
```
```python
def build_ur5e_robotiq():
    """here we create a scene with a single uR5e arm and a gripper."""

    gripper = Robotiq2F85(
        assets="robotiq_2f85",
        mocap_pos="0.4 0 0.3",
    )
    ur5e = UR5e(name="ur5e", assets="ur5e", end_effector=gripper)
    # ur5e._xml | Prettify() | Save("ur5e.mjcf.xml")

    scene = DefaultStage(model="ur5e", children=(ur5e, gripper._mocaps))
    scene._xml | Prettify() | Save("ur5e_robotiq_2f85.mjcf.xml")
```

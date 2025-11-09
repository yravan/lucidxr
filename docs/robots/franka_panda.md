
# Panda Arm (with Tomika Gripper)

Here is a simple scene with a panda arm and a tomika gripper.

```python
from vuer_envs.schemas.robots.default_scene import DefaultStage
from vuer_envs.schemas.robots.franka_panda import Panda
from vuer_envs.schemas.robots.tomika_gripper import TomikaGripper
from vuer_envs.schemas.utils import Save, Prettify
```
```python
def build_panda():
    """here we create a scene with a single panda arm and a tomika gripper"""

    panda = Panda(name="test_panda", pos="0 0 0", quat="0 0 0 1", assets="franka_panda")
    # panda._xml | Save("panda.mjcf.xml")

    scene = DefaultStage(model="franka-panda", children=panda)
    scene._xml | Prettify() | Save("franka_panda.mjcf.xml")
```
```python
def build_panda_tomika():
    """here we create a scene with a single panda arm and a tomika gripper"""

    tomika = TomikaGripper(name="tomika-1")
    # tomika._xml | Save("panda.mjcf.xml")

    panda = Panda(name="test_panda", pos="0 0 0", quat="0 0 0 1", end_effector=tomika)
    # panda._xml | Save("panda.mjcf.xml")

    scene = DefaultStage(model="franka-panda-tomika", children=panda)
    scene._xml | Prettify() | Save("framka_panda_tomika.mjcf.xml")
```

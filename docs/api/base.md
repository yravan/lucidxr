# `vuer-envs.schemas.base`

This module includes the base classes for the xml elements.
You can find the tests in the `specs` folder.

Here is an example

```python
from vuer_mujoco.schemas.base import Xml

config = Xml()

print(config.xml)
```
this should print out.
```xml
<mujoco ></mujoco>
```
You can print minimized xml too

```python 
print(config.minimized)
```
should give you

```xml
<mujoco/>
```

## Detailed API docs

```{eval-rst}
.. automodule:: vuer_envs.schemas.base
   :members: 
   :exclude-members: asset, content
   :show-inheritance: 
   :private-members:
   :no-imported-members:
```
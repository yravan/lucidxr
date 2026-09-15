# Simulation assets

Every catalogued scene resolves mesh and texture files through this directory (or
an explicitly supplied replacement tree). Nothing downloads on import or at runtime.
`manifest.json` records the SHA-256 digest and size of every bundled data file.

- `robots/`: arm, hand, and gripper meshes, including components not selected by
  the default scene catalogue.
- `objects/`: manipulation objects, furniture, and cloth topology.
- `rooms/`: kitchen and room geometry.
- `textures/`: shared textures.
- `adapters/`: assets laid out for the RoboSuite/RoboHive XML adapters.

The bulk of these assets came from the existing local Vuer collections:
`vuer_mjcf/assets` and `vuer-robots/tasks/assets`. These collections supplied files
that were missing from the GitHub checkout. Their exact imported bytes are pinned
by the manifest; their individual upstream revisions were not recorded in those
collections. The repository's MIT license does not replace third-party asset terms.

Two sources have explicit upstream pins:

- Robotiq meshes: [MuJoCo Menagerie](https://github.com/google-deepmind/mujoco_menagerie/tree/8161bba264d7fa7c99ca301e91e7fb44737676ad/robotiq_2f85),
  with its BSD license retained in `robots/robotiq_2f85/LICENSE`.
- MPL collision hulls: [Bullet's MPL model](https://github.com/bulletphysics/bullet3/tree/63c4d67e337017f9d8b298c900e9aabdb69296e7/data/MPL),
  with attribution and licensing in `robots/mpl/LICENSE.txt`. These replace missing
  OBJ conversions with the source STL collision hulls.

Poncho's triangulation was extracted unchanged from the original schema's embedded
coordinates and triangle indices. Generated scene snapshots and executable asset
demos remain in Git history and the ignored local `deprecated/` copy.

To check a complete asset tree:

```python
from lucidxr.sim.assets import verify

verify()  # bundled tree
verify("/data/lucidxr-assets")  # copied tree
```

Keep the directory layout when copying. A future external asset installer can use
this same manifest and root override without changing scene or schema code.

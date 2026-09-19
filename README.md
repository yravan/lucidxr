# LucidXR

MuJoCo scene building and Gymnasium environments for robot manipulation. The active package lives in `lucidxr/`. The old project remains in Git history;
`deprecated/` is an ignored local reference copy and is not included in new clones.

```sh
uv sync --locked
uv run python -m lucidxr.sim.scenes list
uv run python -m lucidxr.sim.scenes build stack_blocks /tmp/stack_blocks.xml --seed 7
uv run python -m lucidxr.sim.scenes check
```

Python 3.14.7 and dependency versions are pinned by `.python-version` and `uv.lock`.
The active package has five direct runtime dependencies: MuJoCo, Gymnasium, NumPy, SciPy, and lxml.
It does not need credentials, a cluster connection, or a logging/launch service.

```python
import mujoco
from lucidxr.sim.scenes import build_xml, compile_model

xml = build_xml("mug_tree")
model = compile_model("stack_blocks", seed=7)
data = mujoco.MjData(model)
mujoco.mj_step(model, data)
```

For rollouts, playback, camera observations and episode rules, see the
[environment guide](lucidxr/sim/mujoco_env/README.md) and
[dependency audit](lucidxr/sim/mujoco_env/DESIGN.md).

## Layout

```text
lucidxr/
  sim/
    xml_schema/
      base.py          # Raw, Xml, XmlTemplate: XML composition
      schema.py        # MjNode, Body, FreeBody, Composite, Replicate, Mjcf
      document.py      # asset resolution for complete MJCF documents
      simple_components/     # cameras, lights, surfaces, particle grids
      robots/         # arms/, grippers/, hands/
      objects/        # reusable rigid and deformable objects
      scene_components/ # reusable rooms, tables, camera/light and robot rigs
      adapters/       # RoboSuite and RoboHive XML conventions
      transforms/     # vectors, quaternions, rotation representations
      utils/          # XML formatting, merging, and file helpers
    assets/           # robots/, objects/, rooms/, textures/, adapters/
    scenes/           # Scene base class, 32 scene definitions, catalogue and CLI
    mujoco_env/       # native Gymnasium environment, controls, playback and wrappers
  rendering/          # offline replay, paired HDF5/video and verified completion
  scripts/            # recording, playback, rendering and remote launch entry points
  tests/              # focused schema and runtime regression checks
infra/                # personal locations, Jaynes/MIT launch, scratch and recovery
training/             # shared models, three policies, data preparation/loaders and trainer
deprecated/          # optional local reference copy, ignored by Git
```

See [the schema design guide](lucidxr/sim/xml_schema/README.md) for extension points
and [asset provenance](lucidxr/sim/assets/README.md) for storage details.
The [cleanup instruction and decision log](lucidxr/REORGANIZATION.md) records the
reorganization method for reuse on other codebases. The [source review record](lucidxr/sim/AUDIT.md)
identifies the reviewed modules and validation boundaries.

## Assets and reproducibility

Assets are bundled for this migration so every retained scene builds offline after
installation. File references use one asset root, independent of source locations
and the current directory. To use a copied asset tree:

```python
xml = build_xml("stack_blocks", assets="/data/lucidxr-assets", seed=7)
```

The CLI accepts the same `--assets` argument. Generated XML records the chosen
absolute root; rebuild with a new root when moving it to another machine.
`lucidxr.sim.assets.verify()` checks the bundled checksum manifest, and accepts an
alternate asset root too. Dataset/checkpoint hosting and Dropbox downloads are
separate follow-up work; they are not required by these scene builders.

The catalogue consolidates demo/export/camera and robot-specific copies into scene
families. Existing configurable builders keep their meaningful options. The original
implementations remain in Git history and the local `deprecated/` copy. Active
runtime entry points and their validation boundaries are documented in the guides
linked here.

For language-free Diffusion Policy, Flow Matching and observation/action MoT,
see [the training guide](training/README.md). Training is an optional install:
`uv sync --extra training`. Its models, policies and loaders are independent of
personal storage and launch configuration; scripts connect them to `infra`.

## Compatibility and validation

All 32 default scenes compile and advance one step on MuJoCo 3.13. The full robot
schema catalogue also compiles, including both hands where supplied upstream.
This is a build/portability smoke check, not a claim of validated policies or
identical trajectories across MuJoCo versions.

Current MuJoCo uses native SDF geometry and native flex elasticity. The port replaces
the removed SdfLib/shell plugins, replaces particle composites with explicit free
bodies, and uses the current orthographic-camera attribute. Poncho uses the discrete
integrator required by native bending elasticity. Push-T's redundant, massless free
joint and several incomplete robot definitions were repaired. The original versions
remain available in Git history and the local `deprecated/` copy.

```sh
uv run pytest -q
uv run ruff check lucidxr
uv build --wheel
```

Generic mesh/evaluation adapters still require the caller to supply their own input
assets. Unused legacy furniture presets may likewise require their original external
asset packs; they are not advertised in the runnable scene catalogue. Tensor-specific
rotation helpers work when PyTorch is installed by a downstream training project;
NumPy versions do not require it.

Demo collection and playback entry points live in [lucidxr/scripts](lucidxr/scripts/README.md).
Offline replay produces paired HDF5/video files; see [rendering](lucidxr/rendering/README.md).
Personal storage configuration and Jaynes/MIT launching, scratch staging and retry
commands live in [infra](infra/README.md). Core simulation and rendering accept
ordinary paths without importing deployment configuration.

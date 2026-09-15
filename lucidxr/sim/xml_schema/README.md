# XML schema design

The schema composes MJCF. Application scene definitions live one level above it in
`lucidxr.sim.scenes`; the schema never imports them.

## Responsibilities

- `base.py`: `Raw`, `Xml`, `XmlTemplate`, attribute serialization, and `chain`.
- `schema.py`: MuJoCo nodes, `Body`, `FreeBody`, `Group`, and the `Mjcf` document.
- `simple_components/`: simple cameras, lights, surfaces, sensors, and mechanics.
- `objects/`: reusable physical objects, including kitchen fixtures.
- `robots/`: arm, gripper, and hand models with their kinematics and controls.
- `scene_components/`: reusable room/table layouts and camera, lighting, robot rigs.
- `adapters/`: external XML conventions; `transforms/`: coordinate operations;
  `utils/`: XML/file operations; `document.py`: complete-document asset resolution.

`Body` introduces a physical frame. `Group` collects components without introducing
a frame or world. Robot rigs contain robots and their control targets. Scenes choose
world settings, lights, layouts, and objects explicitly.

`Raw` is an explicit XML fragment; `Xml` is an element with attributes and children.
`XmlTemplate` adds inherited template parameters. `MjNode` merges document-level
side sections, and `Mjcf` gathers bodies and these sections into one MJCF document.
Instances own their attribute dictionaries and child tuples.

## Define a scene

Every scene subclasses `Scene` and overrides one function: `build() -> Mjcf`.
The base handles seeded construction support, asset resolution, XML export and
compilation. Build a layout from ordinary components or select a reusable preset.

```python
from lucidxr.sim.scenes import Scene
from lucidxr.sim.xml_schema import FreeBody, Mjcf, Xml
from lucidxr.sim.xml_schema.scene_components.tables import Tabletop


class BallOnTable(Scene):
    def build(self) -> Mjcf:
        table = Tabletop()
        ball = FreeBody(
            Xml(tag="geom", type="sphere", size=0.04, mass=0.1),
            name="ball",
            pos=table.surface_origin + (0, 0, 0.1),
        )
        return Mjcf(table, ball)


scene = BallOnTable(seed=7)
model = scene.compile()
scene.save("/tmp/ball.xml")
```

Use `rng = self.rng` once inside `build()` when sampling positions. Each build gets
a fresh generator for the scene's seed. Use `self.options` for scene configuration;
shared lifecycle configuration stays in the base. Register a named scene in the
explicit catalogue to expose it through `python -m lucidxr.sim.scenes`.

## Components and resources

Use `attributes={...}` for MJCF attributes and keyword parameters for template
configuration. `pos=` and `quat=` accept numeric sequences or MJCF strings.
Template fields are inherited through the class hierarchy. Existing `_preamble`,
`_postamble`, `_children_raw`, and `_mocaps` definitions remain supported.

Mesh and texture paths are relative to one asset root, such as
`robots/robotiq_2f85/base.stl`. Never resolve them from a scene file or working
directory. `Scene(assets=...)` selects a relocated root; `prepare_xml` configures
compiler paths and verifies file references. `MjNode.referenced_files()` inspects
component declarations without resolving them.

Preambles merge by MJCF identity (tag plus name/class/reference fields). Parent
settings take precedence for repeated declarations. Give independent resources
unique names. This ordering is part of the existing composition contract.

The original source remains in Git history; `deprecated/` is an ignored local copy. Similar demos share scene families;
meaningful variations should be options or reusable components, rather than copied
modules. Build checks establish loadability, not equivalent policy performance or
identical trajectories across MuJoCo versions.

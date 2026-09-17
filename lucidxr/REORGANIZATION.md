# Instructions for a codebase cleanup

Current storage policy: `deprecated/` is a local, Git-ignored reference copy. The
PR history was rewritten to omit it; original source remains in the base history.
Earlier archive-commit entries below describe the superseded approach.

Current status: the source-review pass and final package/relocation checks are
complete. Delivered in [PR #1](https://github.com/yravan/lucidxr/pull/1), left unmerged
for review. Earlier progress entries below are retained
as a decision history; later entries resolve their open findings.

Use the following instruction in another session. Replace the scope and behavior
examples with those of the target project. This is a working method, not a folder
template: derive the structure from the code's responsibilities.

## Reusable instruction

Audit and reorganize every source file in the agreed scope. Improve the design and
implementation, not just the paths. Preserve supported behavior and required data.
Work through the following steps and record evidence as you go.

1. Establish the boundary. Inspect repository instructions, branches, local changes,
   entry points, dependency metadata, and data sources. Record what must continue to
   work, what may change, and what is deferred. Follow the user's current choices;
   do not silently expand a cleanup into a runtime or storage migration.
2. Inventory every source module. Read runtime logic and inspect large embedded
   templates separately. Track files reviewed, findings, decisions, and unresolved
   issues. A directory listing or automated duplicate scan does not constitute a
   code review. Distinguish executable logic, static model data, generated output,
   examples, and archived code.
3. Capture a practical reference before editing. Exercise representative entry
   points and retain outputs or structural summaries. Include every supported
   configuration when inexpensive. Record existing failures separately from new
   regressions. Keep a recoverable baseline; archive code only when requested.
4. Design around responsibilities and dependency direction. Put primitives below
   reusable components, components below compositions, and application definitions
   above them. Choose names that explain what a module owns. Avoid ambiguous bins
   such as miscellaneous assemblies. A component should not secretly create its
   enclosing application or own unrelated presentation and lifecycle concerns.
5. Review implementations for shared mutable defaults, duplicated constructors,
   stale derived values, ignored arguments, global randomness, inconsistent
   serialization, hardcoded paths, hidden IO, swallowed errors, and unused code.
   Trace callers before changing behavior. Read large templates for naming,
   references, ownership, and physical or domain-specific distinctions.
6. Extract shared behavior only where it is actually shared. Compare variants
   first: similar code can encode different physics, ordering, or conventions.
   Prefer composition and small parameterized helpers. Use inheritance when there
   is a stable contract and a meaningful specialization. Keep model-specific data
   explicit; do not invent a general framework to avoid a few lines of duplication.
7. Make extension points small and obvious. Centralize common lifecycle work in
   one place. If application definitions share a lifecycle, give them one clear
   construction hook, with reusable components that users can compose themselves.
   Avoid forcing custom configurations to subclass a stack of presets.
8. Centralize resource resolution. Resolve paths at an explicit boundary against
   one configurable root, independent of the working directory and source-file
   locations. Inventory required assets, retain provenance, and verify referenced
   files. Do not confuse simulation assets with datasets or model checkpoints.
9. Migrate in coherent batches: core contracts, components, compositions,
   application definitions, then public entry points and documentation. Update
   imports and call sites together. Check results after each meaningful batch so
   failures have a small search space. Avoid permanent compatibility aliases in a
   fresh API unless compatibility is an explicit requirement.
10. Verify outcomes proportionately. Use focused tests for contracts and corrected
    bugs, plus end-to-end smoke checks for supported applications. Compare semantic
    structure where text or ordering legitimately changes. Test from a different
    working directory and, where relevant, an installed package and relocated data
    root. Compilation alone does not prove numerical or behavioral equivalence.
11. Document the final architecture, a minimal extension example, resource setup,
    known limitations, and verification performed. Keep a separate decision log
    explaining significant tradeoffs and outstanding findings. Do not present
    planned checks as completed checks.
12. Deliver a reviewable change. Review the diff for accidental deletions, secrets,
    generated artifacts, stale imports, and unexplained dependencies. Prepare the
    requested PR with concrete resulting behavior and validation. Leave merging
    and other actions outside authorization to the user.

At completion, report which behavior is preserved, which intentional changes were
made, what was actually checked, and any remaining limitations. Never claim to have
reviewed every file until the inventory has been reconciled with the review record.

## LucidXR decisions and working record

- Preserve the original tree under `deprecated/`; build the active package in
  `lucidxr/`. The archive commit preserves all 1,913 original tracked file blobs.
- Keep simulation code together: `lucidxr/sim/xml_schema/`, `assets/`, and `scenes/`.
- Separate XML primitives, atomic components, physical objects, robot models, and
  reusable scene components. Robot rigs compose robots without creating a world or
  adding unrelated lighting and task objects.
- Put room, table, camera, lighting, and robot presets in `scene_components/`.
  Presets are ordinary compositions, so custom layouts can use the same pieces.
- Every scene inherits `Scene` and implements `build() -> Mjcf`. The shared base
  owns seeded construction support, asset resolution, serialization, saving, and
  compilation. Scene-specific objects and choices remain in the scene definition.
- Consolidate near-duplicate demonstrations into 32 named scene families. Preserve
  their required assets and expose one explicit catalogue and CLI.
- Use uv and a locked Python/dependency environment. Keep training services,
  dataset/checkpoint hosting, and Dropbox integration outside this migration.
- MuJoCo compatibility changes are intentional: native SDF and flex elasticity,
  explicit particle bodies, and the current orthographic camera attribute. These
  require build checks and do not establish identical trajectories to old versions.
- The broader implementation audit is ongoing. Findings include repeated mesh
  builders and drawer constructors, inconsistent vector serialization, and derived
  geometry computed before configuration overrides. These are findings to resolve,
  not claims of completed refactoring.
- Moving scenes under `sim` updated the catalogue's dynamic imports and Python
  call sites. The new CLI lists all 32 scenes; the three focused tests pass after
  that move. All 32 scenes subsequently compiled and advanced one simulation step. Packaging
  and relocation checks remain to be repeated after the broader cleanup.

### Example: distinguish shared mechanics from meaningful variants

The two kitchen drawer classes duplicated their constructor, width calculations,
and asset declarations. Their geometry differs: one includes a sliding box, while
the other supplies a fixed face for a layout. The fixed-face class now inherits the
shared setup and retains its own geometry. This removes repeated mechanics without
pretending that the two objects have identical behavior.

### Example: fix inconsistencies at their shared boundary

Camera and light factories formatted attributes independently. Numeric sequences
could become Python list syntax, and camera look-at handling failed for NumPy arrays
or a vertical view direction. Both factories now use the XML attribute serializer;
look-at construction handles vertical views and rejects coincident positions.
The existing scene catalogue still compiles after this change. Focused edge-case
checks should accompany the general smoke check when extending this helper further.

### Example: replace exhaustive declarations only after proving the rule

Each DexHand stored 2,475 explicit body-pair exclusions. Reading the declarations
revealed a common rule: exclude all pairs except pairs of distal finger links.
The replacement enumerates the named links once and generates those pairs. Before
editing, the generated ordered list was compared to every original exclusion for
both hands. The model-specific joint and geometry templates remain explicit.
This removed roughly 4,800 lines without changing the contact-pair policy.

### Implementation audit progress

- Cup and bowl mesh generation now shares `MeshObject`; material, texture, friction,
  geometry naming, and scale remain object-specific. Removed a duplicate bowl base
  constructor and renamed numbered modules to `cup.py` and `bowl.py`.
- Three floating hand rigs now share placement, wrist-camera wiring, and control
  target inclusion in `scene_components/robots/floating_hands.py`.
- Removed redundant Panda link constructors. Shared vector arithmetic and point
  transformation moved into the transforms layer instead of individual robots.
- Corrected WXYZ composition/inversion ordering and half-turn matrix conversion.
  A focused regression test checks identity, inverse, composition against SciPy,
  and a 180-degree matrix round trip. These are intentional correctness changes.
- Bin wall positions now derive from each instance's dimensions. Particle grids
  normalize accepted integer counts and validate the offset dimension.
- Asset inspection propagates malformed XML; path flattening detects collisions
  instead of silently replacing one asset with another.
- Separate robot-rig compilation exposed missing class defaults in dual Panda/UR5
  and an invalid free joint in a mounted ShadowHand. All three corrected rigs load.
- Scene checks and robot model checks continue after each shared-layer change.
  The source review and final package/relocation verification remain open; this
  log does not claim the complete audit or PR has been delivered.

### Package verification progress

The archive's Git tree hash matches the original commit exactly. All asset hashes
pass after updating the asset README's stale entry; no mesh, texture, or cloth data
needed a checksum change. A relocated asset-root check loads ball sorting, particle
pouring, and poncho scenes. The rebuilt wheel contains `sim/scenes` and excludes
archived code, obsolete tasks/assemblies paths, and Python caches. The complete
installed-wheel scene check is running separately from the checkout.

Lighting and calibrated/stereo cameras now use ordinary instance-based groups.
Direct composition verifies that calibrated and stereo rigs emit two and four
cameras respectively. ForcePlate uses shared Body/Xml construction; the marked slab
inherits common slab setup while retaining its different geometry and friction.

The installed wheel subsequently passed all 32 default scene build-and-step checks
from `/tmp`, outside the checkout. The active package and original archive are now
separate commits. Follow-up scene review corrected the `pick_block` asset-root
forwarding and preserved `remove_joints=True` in the new mesh builder; the affected
scenes were rechecked. These follow-up edits require the final wheel to be rebuilt.

Remaining reconciliation items include repeated optional Panda setup in scene
builders, camera customization through raw string replacement in `tie_knot`, and
removing obsolete scene options that are popped but never used. These are concrete
source findings, not reasons to expand the migration into environment runtimes.

### Closing the recorded scene findings

Optional Panda/Tomika setup is now one reusable `PandaTomika` component used by four
scenes. All four `show_robot=True` variants compile. `tie_knot` uses explicit camera
position and wrist-pose overrides, and its additional Panda camera has a distinct
name. Removed the unused option-pop block from the kitchen scene. All 32 default
scenes pass again after these changes. Rotation conversion accepts ordinary lists;
the optional tensor conversion explicitly detaches before its SciPy conversion
and is not an autograd operation.

The original schema class inventory was compared with the active tree. Renamed
items map as follows: FloatingBase to FreeBody, Objaverse bowl/cup to Bowl/Cup,
Room to BrickRoomLayout, LucidXRStaging to StagingLayout, DefaultStage to StageLayout,
and camera-position helper classes to calibration data. TableDummy is represented
by the primitive box component. Empty TableScene and UR5eForTable shells remain in
the archive; supported table/robot composition uses the reusable scene components.
The review includes source logic and template structure; it does not certify the
physical calibration of imported meshes or numerical equivalence to the old engine.

Final verification: the rebuilt installed wheel passes all 32 scene build-and-step
checks outside the checkout. All 32 scenes also compile using the separate installed
asset tree, with the adapter's original default root deliberately unavailable.
Every scene overrides only `build` and produces repeatable XML. The 174 reviewed
Python modules and their source hashes are listed in `sim/AUDIT.md`.

The primitive layer is named `simple_components/`; `scene_components/` retains
composed layouts and rigs. Build staging and `.egg-info` are generated, ignored
packaging outputs. Assets remain ordinary tracked Git files, without LFS.

### Environment migration: investigate contracts before replacing dependencies

Trace both directions: read base classes in external dependencies, then read
real consumers (collection, offline replay, policy evaluation). Record the
behavioral contract before designing a smaller replacement. Names alone can be
misleading: get_prev_action encoded current targets; MidasDepthWrapper did not
run a learned depth model; termination in dm_control returned a discount rather
than a boolean. Preserve the intended behavior and explicitly document changed
APIs rather than cloning these accidents.

Separate physical composition (Scene), simulation ownership (MujocoEnv), policy-side action
encoding, episode rules (Episode), and observation augmentation
(wrappers). Share the observation path between replay and rollouts. A read must
not silently step physics, alter success counters or resample model properties.
Use explicit body/site names and declared spaces instead of array-position
assumptions and hidden wrapper nesting. Keep partial recording restoration
separate from full simulator continuation, documenting what each captures.

Use a few meaningful checks: Gymnasium's checker on a small composed scene,
native command validation with multiple targets and zero actuators, snapshot
continuation, real image-space validation and seeded randomization. Then sweep
existing scene definitions with short rollouts. This found a real geometry-scale
problem that compile-only checks missed: sort_shapes used unit-scale meshes;
its original generated XML specifies box scale 0.1 and block scale 0.095. Restore
those explicit scene scales rather than hiding instability in the environment.

See sim/mujoco_env/DESIGN.md for the dependency audit and
sim/mujoco_env/README.md for the migration map and validation boundaries.

### Keep representation and wrapper responsibilities explicit

Return native physical dictionaries from the runtime. Rotation6d, flat vectors,
normalization and relative coordinate choices belong with policy adapters, not
simulator classes. Keep recording independent of the policy representation.

Review each wrapper for a single responsibility. CameraWrapper composes
observations; CameraView resolves configuration and captures images. Camera,
lighting and texture randomization are separate wrappers sharing a small
RandomizationWrapper lifecycle. Capture only each randomizer's owned rows so
restoring one camera does not erase another camera's randomization.

Measure wrapper overhead separately from actual requested work. Fuse adjacent
compatible lifecycle passes, refresh the model once per randomization reset,
cache identical renders only within one observation, and preserve third-party
wrapper boundaries. Add operation-count regressions for duplicated work; keep
machine-dependent timings in a manual benchmark. A hundred duplicate image
requests need one render, but a hundred distinct images still have a real cost.

### Extend coverage without rebuilding the monolith

Use a dedicated parameter dataclass per wrapper and share validated, model-independent
distributions by composition. Position sampling can serve cameras and lights without
a generic wrapper that knows every model field. Separate texture asset selection,
pixel transforms and lifecycle; material properties are a separate wrapper.

Read both current dependency documentation and old executable behavior. A texture's
shape does not establish its role: RGB, normals and ORM may all have three channels.
Resolve shared material references before editing pixels, preserve non-color channels,
and define explicit behavior for unsupported or conflicting roles. Count active
resources in an existing scene pool instead of changing topology in reset.

Keep a feature coverage table, test representative type/role combinations and verify
actual GPU updates, not just model array changes. A narrow compatibility bridge is
preferable to copying a renderer when an otherwise supported low-level upload API
needs access to its context; isolate and test that bridge, document the fallback.

### Port optional rendering by separating data contracts from execution

Read both the old wrapper and its downstream consumers before deciding something
is covered. A file named Lucid may prepare conditioning inputs without invoking a
generative model. Preserve that distinction: keep camera/label/depth products in
small observation wrappers and put checkpoint loading and GPU execution behind an
explicit renderer interface. Define mask polarity, units, coordinate conventions,
normalization and output types in the interface rather than inferring them from
key strings. Resolve names once, but refresh camera calibration after randomization.

Keep optional GPU dependencies out of core imports, share heavyweight renderers,
and cache identical requests only for one observation. Verify image preparation
and composition locally with real simulator renders plus a recording backend;
report CUDA execution separately. A mock backend proves the integration contract,
not checkpoint compatibility or GPU kernel execution. Supply a small cluster smoke
entry point for the latter. Channel ownership follows the same principle: RGB,
opacity and emissive exposure have separate semantics and independent restoration.

### Keep deployment locations outside application workflows

Identify the one infrastructure value a workflow actually needs before adding
backend abstractions. Recording currently needs an output directory: personal
configuration resolves it, while the recorder accepts a plain filesystem path.
Keep the episode format beside simulation code, not inside host-specific infra or
a future training dataloader. Add transfers and scheduling only when exercised by
a concrete workflow, with explicit host and credential configuration then.

For recording migrations, inspect timing and control semantics before naming data
as training actions. Save versioned numeric arrays and explicit source metadata,
validate shapes before accepting a frame, fingerprint the scene and asset content,
and publish files without overwriting earlier demonstrations. Exercise failed
writes and replay, not just happy-path serialization. Temporary browser exports
must preserve implicit asset names when filenames are rewritten. Test the exported
XML as a standalone model. Distinguish server-event verification from actual VR
interaction and keep that verification gap visible.

### Design model families around the actual axes of variation

Read the original papers and reference implementations before deciding that three
named methods need three independent stacks. Separate mathematical objective,
network architecture, representation and execution. Here diffusion versus flow
changes the training target and sampler, while U-Net versus MoT changes the network.
A shared trainer does not imply identical model internals or identical loss scales.

Specify tensor shapes, physical units, timing, masks and normalization ownership
before creating base classes. Check where removing a feature also removes an
input: OpenPI's pi05 language-token path includes proprioception, so a language-free
adaptation must explicitly restore a state input. Record departures from a reference
recipe rather than borrowing its name and implying identical behavior.

Trace one real datum from collection through preparation to rollout. Hidden label
shifts, source-group leakage and training augmentations during validation can make a
clean-looking rewrite incorrect. Mark missing evidence and proposed contracts in a
design PR; do not fill uncertain boundaries with unused implementations. Pin research
sources, distinguish paper claims from local choices, and implement bounded end-to-end
slices after the interface is concrete.

### Build the data-producing workflow before its consumers

When distributed rendering is a concrete requirement, give it an application-level
home and bounded delivery stages: local correctness, distributed execution, then
staging/recovery. Let that real workflow drive infra's configuration and operations.
Keep scheduler submission and transfers outside renderer logic, and reuse its worker
locally. Stable work identities, immutable attempt outputs and validated completion
records make retries inspectable without a bespoke queue service. Defer training
until the export contract exists; retain research without building unused scaffolds.
Shared infra setup means one source of deployment settings, not a global constants
module containing model mathematics and dataset semantics.

# Randomization design and coverage

Every randomizer has a frozen parameter dataclass. RandomizationWrapper owns
scheduling, baseline restoration, failure rollback and batched model refresh.
Concrete wrappers own selection and sampling; model-independent distributions
are shared through composition rather than another inheritance layer.

```python
from lucidxr.sim.mujoco_env import make_env
from lucidxr.sim.mujoco_env.wrappers import (
    CameraRandomization,
    CameraRandomizationParams,
    LightingRandomization,
    LightingRandomizationParams,
    MaterialRandomization,
    MaterialRandomizationParams,
    TextureRandomization,
    TextureRandomizationParams,
    PositionRandomization,
    RotationRandomization,
    Uniform,
)

env = make_env("pick_block")
env = CameraRandomization(
    env,
    CameraRandomizationParams(
        position=PositionRandomization(offset=(0.01, 0.01, 0.005)),
        rotation=RotationRandomization(max_angle=0.05),
        fovy=3.0,
    ),
)
env = LightingRandomization(
    env,
    LightingRandomizationParams(
        position=PositionRandomization(offset=0.1),
        rotation=RotationRandomization(max_angle=0.35),
        ambient=0.05,
        diffuse=0.15,
        specular=0.1,
        active_probability=0.75,
    ),
)
env = MaterialRandomization(
    env,
    MaterialRandomizationParams(
        color=0.15,
        specular=Uniform(0.1, 0.6),
        shininess=Uniform(0.1, 0.5),
    ),
)
env = TextureRandomization(
    env,
    TextureRandomizationParams(
        modes=("tint", "checker", "gradient", "noise"),
        blend=0.25,
    ),
)
try:
    obs, info = env.reset(seed=7)
    obs, reward, terminated, truncated, info = env.step(env.unwrapped.current_action())
finally:
    env.close()
```

Image observation wrappers go outside the randomizers. Their output reflects the
sampled model. For inexpensive appearance variation use MaterialRandomization
alone; adding TextureRandomization explicitly opts into pixel storage/upload.

## Shared parameters and sampling

RandomizationParams supplies `on_reset=True` and `every_n_steps=None`. Every
concrete parameter dataclass inherits these fields. Set `every_n_steps=10` to
sample before control steps 0, 10, 20, ...; reads and recorded-frame playback
never advance this schedule. `on_reset=False` restores defaults on reset without
sampling. Explicit `randomize()` and `restore()` affect only that wrapper.

PositionRandomization samples either symmetric scalar/xyz offsets from baseline,
or absolute lower/upper xyz bounds. Positions are in meters, in each camera/light's
parent-body coordinate system. RotationRandomization samples a uniform random
axis with a signed angle bounded in radians; camera quaternions stay normalized
and light directions stay unit length. Uniform samples an absolute scalar range.
These dataclasses validate configuration before it reaches the rollout loop.

The environment RNG drives sampling in inner-to-outer wrapper order. Fixed seed,
configuration and stack ordering reproduce samples. Baselines contain only owned
model rows or selected RGB pixels. Distinct selections therefore do not erase
each other when restored. Overlapping wrappers assign in order; outer assignments
win. Custom samplers implement `sample(rng)` and declare their owned fields to the
base; the base restores those fields if sampling raises.

## CameraRandomizationParams

| Parameter | Behavior |
| --- | --- |
| names | Exact camera names; None selects all |
| position | Shared local PositionRandomization |
| rotation | Shared RotationRandomization |
| fovy | Symmetric degree offset, bounded to [1,179] for fovy perspective cameras |
| focal_scale | Optional Uniform scaling fx/fy together for calibrated cameras |
| principal_offset | Symmetric fraction of physical sensor size for principal offsets |

FOV changes do not alter orthographic extents or explicit intrinsic calibration.
Focal/principal sampling requires the selected cameras to have perspective
intrinsics. Target-tracking cameras derive orientation from their target: request
`RotationRandomization(0)` instead of assigning an ignored quaternion. Recomputed
K/C2W camera observations reflect calibration/pose changes.

## LightingRandomizationParams

| Parameter | Behavior |
| --- | --- |
| names | Exact light names; None selects the scene's complete light pool |
| position / rotation | Local position and direction sampling |
| ambient / diffuse / specular | Independent symmetric RGB offsets clipped to [0,1] |
| active_probability | Independent activation probability; None preserves activation |
| active_count | Inclusive (minimum, maximum) count; supersedes active_probability |
| shadow_probability | Optional independent probability of casting shadows |
| cutoff / exponent / attenuation | Optional Uniform spotlight/Phong parameters |
| intensity / range / bulbradius | Optional Uniform values for supporting renderers |

For example, `active_count=(1, 3)` selects 1–3 lights without replacement from the
selected pool. A count larger than that pool is rejected. This controls **active
scene lights**, not model topology, the viewer headlight, or the number of lights
supported by a renderer. Define enough potential lights in Scene.build(); adding
bodies/lights and recompiling on every reset would invalidate model-bound IDs and
make the hot path unnecessarily expensive.

Direction is a normalized vector, not a quaternion: roll around the light's axis
has no meaning for these native light sources. Target-tracking lights derive that
direction, so rotation sampling must be disabled for them. Light types remain as
defined by the Scene; switching to unsupported renderer types is not randomized.

MuJoCo's default renderer supports spot and directional lights. PBR intensity,
image-based lighting and bulb-radius effects depend on the rendering backend;
setting those fields does not make them available in classic OpenGL. Shadow-casting
lights add rendering passes, so varying their count has a real runtime cost.
[MuJoCo light reference](https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-light)

## MaterialRandomizationParams

MaterialRandomization owns inexpensive appearance properties; it never copies
texture pixels. `names` selects materials and `geom_names` selects geom RGB rows.
By default, materials are all selected and only geoms without a material receive
independent color offsets, avoiding an unintended override of material appearance.

`color` controls symmetric RGB offsets, leaving alpha unchanged. Optional Uniform
ranges set emission, specular, shininess, reflectance, metallic, roughness and
texrepeat. Color-like material scalars are constrained to [0,1]; texrepeat must
stay positive. Shared materials are sampled once, affecting every referencing
geom/site/skin/tendon. PBR material maps can modulate these values and backend
support determines the final rendered appearance.

## TextureRandomizationParams and implementation

TextureRandomization coordinates the lifecycle. `texture_assets.py` handles
compiled asset selection and RGB-only baselines. `texture_patterns.py` handles
seeded pixel operations in bounded row chunks. Selection never relies on source
filenames or assumes that one geom owns one texture.

| Parameter | Behavior |
| --- | --- |
| names | Exact texture assets; None selects eligible color textures |
| kinds | 2d/cube by default; explicitly add skybox to modify the background |
| modes | Uniform per-asset choice of tint, flat, checker, gradient, noise |
| strength | Tint offset magnitude in normalized [0,1] color units |
| blend | Interpolate sampled RGB with original RGB; 0 preserves it, 1 replaces it |
| checker_tiles | Positive number of checker cells per axis |
| gradient_axis | x, y or random |
| noise_probability | Pixel probability for one of two sampled colors |

Tint shifts baseline RGB; other modes synthesize new RGB before blending. Cube
and skybox buffers contain six vertically packed faces: face-local patterns repeat
per face, while tint/flat color affects the complete cube. These are augmentation
patterns, not byte-for-byte implementations of MuJoCo's compiler-generated
patterns or seamless environment-map synthesis. File-backed and compiler-generated
color textures use the same compiled layout.

Selection inspects `tex_type`, `tex_adr`, `tex_height`, `tex_width`, `tex_nchannel`
and the multi-role `mat_texid` table. Stored pixel color space is preserved;
tint offsets apply in that stored encoding, not a linear-light exposure model. RGB, RGBA and emissive roles are eligible;
alpha and emissive exposure weights (fourth channels) are preserved. Normal,
occlusion, roughness, metallic, opacity and packed ORM maps are left untouched.
A texture shared between color and non-color roles is also excluded. Explicitly
naming an incompatible texture raises instead of silently corrupting its meaning.
Unreferenced assets are not inferred to be color maps. Image-light textures and
skyboxes are identified separately from material roles.
[MuJoCo texture/material layers](https://mujoco.readthedocs.io/en/stable/XMLreference.html#material-layer)
[Compiled texture/material fields](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html#mjmodel)

Changing scalar PBR maps or surface-normal maps would need a role-specific sampler;
this RGB wrapper does not claim to randomize them. UV coordinates, texture source
files, pixel dimensions and material topology are also preserved.

## Uploads and performance

Only selected RGB baselines are copied. Tint arithmetic uses int16 row chunks,
and patterns avoid full-texture float64 temporary arrays. Each shared texture is
sampled once; identical IDs from a wrapper stack upload once per render context.
Existing offscreen contexts use `mjr_uploadTexture`; the passive viewer uses
`update_texture`. No context is created for a physics-only process.
[MuJoCo upload API](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html#mjr-uploadtexture)
[Passive viewer API](https://mujoco.readthedocs.io/en/stable/python.html#passive-viewer)

MuJoCo 3.13's Python Renderer does not expose its render context publicly. The
small bridge in Rendering.update_textures isolates access to its current context
fields and falls back to lazy renderer recreation if that interface changes.
Live uploads were tested against the installed 3.13.0 renderer at two resolutions;
passive viewer updates use the documented method but were not exercised visually.

Adjacent compatible randomizers share one lifecycle pass and one model refresh.
Without a periodic schedule, ordinary steps skip randomization entirely.
Observation wrappers cache identical image requests within a single observation.
Real work—new images, shadow passes, or changing many large textures—still costs
time and memory; a hundred wrappers cannot make those operations free.

## Coverage against the original new wrappers

| Original feature | Current location |
| --- | --- |
| Camera position, rotation, fovy | CameraRandomization; also intrinsic calibration controls |
| Light position, direction, three colors, activation | LightingRandomization; also exact active count, shadows and optional physical fields |
| Per-geom color and material appearance | MaterialRandomization |
| RGB, checker, gradient, binary noise textures | TextureRandomization pattern choices |
| Local texture interpolation | TextureRandomizationParams.blend |
| Skybox variation | Explicit skybox selection |
| Reset and every-N-step randomization | Inherited RandomizationParams schedule |
| Save/restore model defaults | Shared lifecycle with selected-field ownership |
| RGB/depth/RGBD/calibration and multiview | CameraWrapper / CameraView |
| Segmentation, masks, overlays, inverse depth | CameraView products, int32 IDs and declared spaces |

The original dynamics flag raised NotImplementedError; physics dynamics are still
outside these visual wrappers. Real robots and old_info_wrappers remain excluded.
External Gaussian-splat model loading and ADE color-palette visualization remain
separate integrations. This is functional coverage, not identical historical
sampling distributions or an adapter for old training-worker APIs.

Validation includes seeded pattern/type/channel tests, untouched non-color/shared
roles, baseline restoration, active-light counts and normalized directions,
periodic scheduling, calibrated cameras, material properties and live GPU uploads.
An initial scalar builtin-texture fixture triggered a native compiler crash; scalar
and four-channel fixtures now use actual image files as documented for those
channel layouts. The wrapper operates on compiled arrays and does not generate
such MJCF texture declarations.

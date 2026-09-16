# Lucid conditioning and Gaussian splats

`LucidWrapper` prepares the inputs formerly spread through `lucid_wrapper.py`.
`GsplatWrapper` renders a reconstruction from the current simulation camera and
optionally preserves a MuJoCo foreground. Both use the common observation pass,
so reset, step and replay via observe produce the same declared dictionary.
Neither imports torch during normal environment use.

## Lucid conditioning

```python
from lucidxr.sim.mujoco_env.wrappers import Camera, LucidParams, LucidWrapper

env = LucidWrapper(
    env,
    LucidParams(
        camera=Camera(
            "main",  # use a camera from your scene
            masks={"object": ("object_body",)},
            semantic={"floor_geom": 4},  # exact geom name -> ADE20K class ID
            near=0.02,
            far=1.9,
        ),
        preserve_bodies=("robot_body",),  # exact roots, including descendants
    ),
)
```

Outputs use the `main/lucid/` prefix (or an explicit `LucidParams.key`):

| Product | Meaning |
| --- | --- |
| rgb | Original MuJoCo RGB uint8 |
| preserve_mask | True where the original foreground should be retained |
| overlay | Retained foreground over white |
| depth, segmentation, semantic | Hidden-scene metric depth, int32 geom IDs and class IDs |
| semantic_rgb | ADE20K colors; IDs 1..150, unmatched/background black |
| mask/name | Boolean object masks in the hidden scene |
| midas_depth | Relative inverse depth, float32 in [0,255] |
| masked_midas_depth | Inverse depth normalized over the union of object masks, zero elsewhere |
| normalized_depth | Full-scene depth clipped to near/far and encoded as uint8 |
| K, C2W | Current pinhole intrinsics and OpenCV camera-to-world transform |

`preserve_bodies` are removed from conditioning images so generation sees the
scene behind the robot. They remain in the original RGB and preserve mask.
`Camera.hide_bodies` hides body subtrees from both views. Object masks are boolean
arrays rather than packed bytes. Geometry IDs are never reduced modulo 256.
The ADE palette and label list live in `wrappers/ade20k.py`; rendering and plotting
libraries are not needed to import them.

The original “Midas” wrappers perform depth normalization, not learned inference.
Unmasked relative normalization retains the original low-minus-one convention;
masked normalization uses clipped depth and handles empty selections safely.
Outputs use float32 instead of the old float16/uint8 mixture. Generation itself
remains an explicit downstream operation; no queue, credentials or remote service
is constructed by the environment.

## Gaussian splats

On a CUDA Linux host, install the optional backend with `uv sync --extra splat`.
The extra locks torch 2.14.0 and gsplat 1.5.3; it is Linux-only and the core install
stays small. Installation resolution has been checked, but CUDA compilation and
rasterization have **not** been run in this macOS session. A compatible NVIDIA
driver and CUDA development toolkit are required by the backend.

```python
from lucidxr.sim.mujoco_env.splat import GsplatRenderer, SplatAlignment
from lucidxr.sim.mujoco_env.wrappers import GsplatParams, GsplatWrapper

renderer = GsplatRenderer("/data/reconstruction/3dgs/model.pt")
env = GsplatWrapper(
    env,
    renderer,
    GsplatParams(
        camera="main",
        alignment=SplatAlignment.from_json("/data/reconstruction/collision_tf.json"),
        foreground_rgb="main/lucid/rgb",
        preserve_mask="main/lucid/preserve_mask",
    ),
)
try:
    observation, info = env.reset(seed=0)
finally:
    env.close()
    renderer.close()
```

The foreground fields are optional; omit both for pure splat output. Their
resolution must match the splat camera. Output keys default to `splat/rgb`,
`splat/depth`, `splat/alpha`. RGB is uint8, depth is expected z-depth in simulation
world units, alpha is float32 in [0,1]. Depth and alpha describe the reconstruction,
**not the composited RGB**. Foreground is selected by mask, as in the old wrapper;
this is not physical alpha blending or depth-based occlusion between renderers.

The backend accepts the original `checkpoint['splats']` tensors: means, quats
(wxyz), logarithmic scales, opacity logits, sh0 and shN. It loads tensor-only
checkpoints, validates shapes, precomputes activations and renders without gradients.
No training strategy or modified gsplat fork is imported. `SplatRenderParams`
configures device, background, clipping, packing, rasterization mode and SH degree.
Near/far clipping parameters are in reconstruction units.

Alignment maps reconstruction points to simulation world as `scale * R * x + pos`.
Legacy mesh_euler uses intrinsic XYZ radians. The inverse mapping changes camera
position and rotates its axes; it never scales camera rotation. Camera K and pose
are refreshed on every observation, including camera randomization. Calibration
already uses OpenCV axes; there is no second axis flip. Orthographic cameras are
rejected by the pinhole calibration interface.

A caller can share one renderer between cameras and environments and owns its
lifetime. Identical requests for the same renderer within one observation reuse
one rasterization, with independent output arrays; the cache ends with that read.
Distinct viewpoints still require distinct renders. A backend implementing
`render(K, C2W, width, height) -> {rgb, depth, alpha}` can be injected for other
rendering engines or CPU integration tests.

The implementation follows the [released gsplat 1.5.3 rasterization API](https://github.com/nerfstudio-project/gsplat/blob/v1.5.3/gsplat/rendering.py).
Local checks exercise actual MuJoCo conditioning renders, ADE mapping, foreground
compositing, live calibration, scale conversion and 100-wrapper render sharing
with a recording backend. On the cluster, run
`uv run --extra splat python lucidxr/tests/smoke_gsplat.py` to exercise real CUDA
rasterization before using a reconstruction checkpoint. Then verify that your
checkpoint and collision transform align visually; the synthetic smoke cannot
validate dataset-specific alignment.

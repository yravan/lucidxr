# Recording and rendering verification

Verified on 2026-09-17 UTC with Python 3.14.7, native MuJoCo 3.13.0,
Gymnasium 1.3.0, NumPy 2.5.3, h5py 3.16.0 and PyAV 18.1.0.

## Local checks

The full PR stack passes 34 focused tests and `ruff check lucidxr infra`. These
include scene/schema construction, Gymnasium controls and existing wrappers as
well as new recording, replay, artifact and recovery contracts. The rendering
checks exercise real MuJoCo frames and actual HDF5/video writers. Injected transfer
failures leave no accepted record; retry publishes one verified result. A real
shell submission with a simulated lost SSH acknowledgement recovers its ID without
executing twice. A claim without an ID remains blocked for inspection.

The bundled Vuer 0.1.6 client was inspected, including its AutoSimLoop and embedded
MuJoCo 3.3.6 WASM engine. A Node harness loaded that engine and the collector's
exported scene/assets, initialized the published state, applied controls and emitted
frames after the same step sequence. A websocket client sent those engine frames
through the actual Vuer collector with alternating 10/70 ms arrival delays.

The saved state times were 0.02, 0.04, 0.06, 0.08, 0.10 and 0.12 seconds, agreeing
with WASM `getState(..., mjSTATE_TIME)`. This catches the clock sensor's one-step
sampling offset; adding `mj_forward` in the harness would incorrectly hide it.
Headset interaction was not exercised. The harness checks the real engine,
websocket, event handlers and save path, rather than inventing frame timestamps.

The new recording replayed and rendered into `pick_sphere`, seed 9, at 640x360,
with wrist RGB/depth/segmentation. HDF5 stores the newly simulated target states.
State replay and same-scene command motion have focused regression checks too.

An initial Mac-to-Linux run exposed last-bit differences in seeded positions.
Computed MJCF numbers now serialize consistently at 12 significant digits, and
legacy scene f-strings use the same numeric serializer. The target scene has the
same fingerprint on Mac and Engaging:
`b6e5793535d1ed2d0030b9611a22aefcf980fb9d948ee89e28e17f4e263c54a0`.
The identity check remains strict; changed request fields are reported explicitly.

## MIT execution

The final verification uses a six-frame browser recording and a 1,500-frame native
recording, replayed as commands into the same target scene above. Each request
produces one HDF5 and one MP4 containing RGB, with lossless depth and segmentation
arrays in HDF5. Workers use node-local scratch and publish to configured shared
storage. The launcher captures code and inputs without a remote checkout.

Captured run: `d907de06817b418daa077a840ba231a7`; source tree:
`e8d6dbc4142c57a4160adc4d0c6401d7d9fedb6e`.

- Job 22879159 completed the six-frame result on node3102.
- Job 22879160 was cancelled on node3406 after reporting 100/1,500 frames.
  The incomplete result had no shared completion record.
- `infra resume` reused the uploaded archive and saved commands. Job 22879202
  verified and skipped the accepted six-frame output; job 22879203 restarted the
  missing result from captured inputs on scratch.

Jobs 22879202 and 22879203 completed with exit 0 on node3202 and node3406.
The long render took 128.90 seconds, followed by verified publication to shared
storage. The resulting collection is
`1318e11b85cf1f79c8303fd4dd4b39468a8f85b61341be704522d7f78ff4905d`.
Both artifacts were downloaded and consumed by a separate process: completion
hashes, full MP4 decoding, frame counts, timestamps, RGB/depth/segmentation shapes
and camera calibration passed. Total output size was 437,062,490 bytes. The first
result's record and modification time were unchanged after resume.

A separate Linux process replayed both inputs and matched every saved physical
field across all 1,506 frames (maximum qpos error zero). The short Mac/Linux replay
agreed to about 1.2e-15 in qpos; the 30-second contact sequence differed by up to
1.0e-4 in a qpos component. Command integration is therefore not advertised as
bitwise portable across hardware. Calibration agreed within 1e-10. Cross-platform
RGB mean absolute error was 1.405 on the 0–255 scale; depth differed too, especially
at image boundaries. State restoration and output integrity are separate guarantees
from identical rasterization or contact integration.

An allocation-side check found only the assigned NVIDIA device accessible; the
other three device nodes were denied by Slurm's device isolation. MuJoCo's EGL
selection uses an accessible device without assuming that CUDA's logical index
is an EGL device index.

Earlier jobs also established failure visibility: deliberate worker failure
22837819 reached Slurm as FAILED with exit code 7. A failed portability check in
22878449/22878453 reached Slurm as FAILED with exit code 1 and published no results.
The reconciliation command recovered their two accepted IDs from remote receipts
when given a local verification copy with its acknowledgements removed.

## Limits

The exercised distributed renderer is native MuJoCo/EGL. This is a small workflow
and recovery test, not a throughput or GPU-utilization benchmark. Mac and Linux
OpenGL rendering need not produce byte-identical RGB/depth. Browser and native
MuJoCo versions differ, so recorded-state restoration and command integration have
different guarantees. Training, dataset export, gsplat/Lucid execution and actual
VR headset validation are outside this verification.

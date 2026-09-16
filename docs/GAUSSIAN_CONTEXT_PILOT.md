# Gaussian context pilot — development only

This is a bounded visual-context experiment following the user's clarification
that the intended capture format is 3D Gaussian Splatting. It complements the
[classified LiDAR ground pilot](SAN_FRANCISCO_LIDAR_PILOT.md). Splats never supply
the design ground, replace canonical archetypes, or rewrite proposal coordinates.

## Dataset selection

The selected sample is **Knock Community Hall**, captured by **scbenoit** from
185 Phantom 4 drone photographs and trained with Brush. The creator's
[SuperSplat page](https://superspl.at/scene/0ff2e6dc) explicitly offers CC BY 4.0.
The tested file and attribution are mirrored in the official
[PlayCanvas engine examples](https://github.com/playcanvas/engine/tree/3ee7522039027d98860eec3277220893b5afd871/examples/assets/splats).

- Source revision: `3ee7522039027d98860eec3277220893b5afd871`.
- File: `knock-community-hall.sog`, 27,830,709 bytes, 1,935,100 Gaussians.
- SHA-256: `2c9ef67e619878cdb85d8f972cc6b1b8a8c76cbd7b4ed1137ac97bbd78785202`.
- Format: SOG v2, including directional spherical-harmonic data; no retraining or
  mesh/point-cloud substitution. The exact archive is decoded locally.
- Attribution is shown with the capture. Data is outside Git and not shipped.

The creator identifies the real building in Innisfil, Ontario. The archive does
**not** establish a surveyed CRS, scale, vertical datum or coordinate transform.
The test therefore uses an explicitly artificial Calgary placement (ENU anchor
51.0169, -114.1249, height 1102; local offset 35/30/0; scale 4). This is not evidence
of alignment with Google's capture of the actual building. Axis orientation was
verified visually; the decoder's convention requires an X rotation of -π/2 into
the application's Z-up local frame.

Other candidates suggested by the user remain useful, with different constraints:

- [Mega-NeRF/Mill 19](https://github.com/cmusatyalab/mega-nerf): photographs, poses
  and pretrained **NeRF** models. These are not directly browser-ready Gaussian
  files. A particular third-party splat derivative needs its own provenance and
  source-data terms checked; the repository's software license alone is not a
  blanket license for every derivative.
- [UrbanScene3D](https://github.com/Linxius/UrbanScene3D): the published terms
  restrict commercial use and redistribution, including altered datasets. It was
  not imported for this product pilot.
- [Pix4D examples](https://support.pix4d.com/hc/en-us/articles/360000235126): the
  page supplies photogrammetry training data and states training/attribution
  conditions. These still require training and per-project metadata validation.
- SuperSplat and Hugging Face can host ready-trained files, but hosting alone
  establishes neither permission nor geographic registration. No claim is made
  that licensed ready-trained versions of all the exact benchmarks were found.

## Integration and dependency decision

The installed Drei `Splat` component was inspected first. It lacks the required
logarithmic-depth shader integration and explicit loader/worker lifecycle controls.
Spark **0.1.10**, MIT, is pinned for this development experiment. Its package adds
one dependency entry; fflate was already installed. `npm audit` found zero known
vulnerabilities at installation, and `npm ls three` confirmed a single deduplicated
Three.js 0.170.0. The package is approximately 2.4 MB compressed / 11 MB unpacked,
including maps; its unminified ES module is about 794 KB before application bundling.
It is dynamically imported only when the sample is first requested.

Current Spark 2.2 requires Three.js >=0.180.0. Upgrading the globe/render stack to
meet that requirement is a separate compatibility task, not hidden in this pilot.
Spark 0.1 has no renderer-wide disposal API. One renderer and decoded sample are
retained for the canvas session, with visibility changes on context switching;
R3F destroys the WebGL context with the canvas. This cache policy is not a claim
of production lifecycle completeness or a hard GPU memory limit.

The source decoder accepts only the fixed path, exact byte count and SHA-256.
It bounds streaming reads, aborts on timeout/unmount, and rejects missing,
truncated or substituted archives before decoding. There is no arbitrary upload
or URL importer. Missing/failed capture keeps Google visible with explicit retry.

The existing R3F canvas, WebGL renderer, projection and logarithmic depth buffer
are shared. Gaussian generation uses a local context scene and a **copy** of the
authored camera. CPU double-precision transformation removes ECEF translation
before any float texture/shader work. Initially packing Earth-scale positions
made the sample invisible; merely shifting its packing origin caused visible
quantization. The local camera adapter removes both defects without moving the
proposal or the authored camera. Its projection equivalence is tested numerically.

The existing polygon-mask GLSL is shared with Google/mesh context. Gaussian
centres within the replacement polygon and height range are suppressed in the
shader. Source bytes remain intact. Whole-splat suppression can leave soft tails
near the boundary; it is not exact per-pixel clipping or destructive mesh editing.
The authored building remains visible while the captured tree/ground is removed
from its plot. Sample context is blocked from professional render capture.

## Evidence and limits

Local fixture: `de135a47-778c-440a-8d49-e6581fd26466`. The API prepared the boundary;
the reviewed infill house was selected and placed through the actual catalogue.
This is not the full first-time student journey.

Evidence lives outside Git in
`C:/dev-artifacts/CityPrompt/student-design-transformation/gaussian-splat/`, with
`PHASE8-GS-*.png` in its parent. Source metadata, scripts, frozen camera and
before/after state are retained. Upright and masked views were visually inspected.

The complete saved zones were exactly equal after reload. An aborted source-file
request retained Google and the exact camera; explicit retry and a fresh reload
both succeeded. Those screenshots were visually inspected. Six further switches
kept the same renderer/source identity and 205 tracked textures, with 220–221
geometries as visible buffers changed. Resource timings remained at two sample
requests (the deliberate failure and successful retry), with no new downloads.
The sample capture guard returned its intended explanation. No new uncaught errors
appeared, and fresh-reload resource statuses had no failures.

Automated validation: 24 narrow tests across six suites, TypeScript, and targeted
ESLint passed. The shader compatibility test instantiates the pinned renderer's
actual material, so a missing injection point fails rather than silently disabling
context suppression. Browser inspection covers actual WebGL compilation.

User steering after this pilot: defer further LiDAR/Gaussian-splat work and
continue the core product mission. The production work below is explicitly
deferred, not accepted as complete.

Google → splat → terrain → Google kept the camera, native building matrices/UUIDs
and ground state exactly equal. At 1600 × 1000, three-second samples recorded
16.7 ms median / 16.8 ms p95 rAF cadence, with no intervals over 50 ms. Google /
splat / terrain submitted 407 / 26 / 25 draws and about 0.799 / 3.903 / 0.033 million
triangles across render passes. These are sampled observations, not GPU timings
or a performance improvement claim. Heap observations were roughly 0.83–0.95 GB
and depend on browser history and garbage collection.

Open production work: survey registration and independent ground control;
current renderer/Three.js compatibility and complete disposal; streaming LOD and
larger-scene memory budgets; precise replacement edges; broader street/park
switching; source-aware render/export provenance. No production Gaussian context,
metric alignment, final grounding acceptance or paid AI output is claimed.

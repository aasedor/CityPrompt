# Context provider engineering pilot

**Status: visual-source separation verified; survey/LiDAR/DTM integration remains
open.** This is an opted-in development fixture, not production capture coverage.
See [the Lux Modus delivery contract](LUX_MODUS_ADAPTER_CONTRACT.md).

## Architecture

`features/context` separates context presentation from saved proposal geometry.
The existing Google renderer, ground lifecycle, navigation, ENU frames and RLASM
layers remain mounted. Hiding Google changes only its materials' display state;
ground raycasts retain their original geometry. Loaded/disposed tiles and cleanup
restore material state. Context roots carry `sceneRole: existing`; proposals keep
their existing semantic capture roles.

An alternate `TilesRenderer` shares the world coordinate frame and existing
polygon suppression shader. It does not reparent the design or camera. Google
stays visible until a model loads, and returns on a loading error or timeout.
Retry requires an explicit selection. Unmounting the sample disposes its renderer.
The development handle exposes renderer draw/triangle and resource-count metrics.

Only `VITE_CONTEXT_PILOT=true` in development, the matching manifest project ID,
and an existing saved prepared site level enable the controls. The fixed
`/context-pilot/manifest.json` accepts only the curated local fixture path and
registration policy. Normal projects keep Google and no extra controls. This is
not an arbitrary URL importer or production dataset registry.

Sample/terrain pilot views are blocked from professional capture because their
context provenance is not yet integrated. Google captures remain available.

## Public sample and transformation

[Drone Building Scans](https://huggingface.co/datasets/Matt1up/drone-building-scans),
Matthew Guertin, 2026, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Pinned dataset revision `fde325fbd1d3636ffcf5d48aedc24cdbfc9a630f`.
Only the flat-roof GLB, attribution/licence and small metadata files were downloaded.
The original GLB is 21,822,576 bytes. Its SHA-256 is
`6c712d16b9ede8f5083d7fc82787cf75b913865b157f48db08a61f2154c6bd73`.

The source documents metric scale from a physical control bar. Absolute horizontal
registration and vertical datum are not established for this GLB. The pilot uses
an **artificial** local Z-up metre frame, converted by an explicit ENU-to-ECEF
matrix at Calgary's test anchor (51.0169°, approximately −114.124515°, 1102 m
ellipsoid height). This does not locate the Minneapolis capture in the real world.
The tileset records its complete matrix, local bounds and `gltfUpAxis: Z`.
Saved project grade, not this scan, remains the ground authority.

`tools/context_pilot/prepare_texture.py SOURCE OUTPUT` produces a 2K JPEG texture
derivative using the existing Python/Pillow environment. It requires the pinned
source hash and external paths, preserves compressed geometry byte-for-byte and
writes attribution/modification/checksum provenance beside the output. The
derived GLB is 14,797,376 bytes. No sample binary is committed or shipped.

## Browser evidence

Local project: `db54538d-8354-4235-b919-73ebde150c1f`. A reviewed infill house was
chosen from the catalogue and placed through the UI. Its boundary/grade fixture
was created through the API; this is not novice-journey evidence.

- Google → capture → terrain → Google preserves the exact camera, every tested
  proposal world matrix and live object UUID. The design is not remounted.
- Full reload preserves all saved zone objects exactly. The new session defaults
  to Google; selecting the sample again works.
- A browser-intercepted failed tileset request returns Google, preserves the
  camera and shows a useful retry message. Explicit retry succeeds; no retry loop.
- Source and derived texture views were inspected. The existing polygon mask
  cuts the part of the sample overlapping the prepared site.
- The ordinary Gold Standard project reloads with Google context, no pilot control,
  settled ground and no grounding issues. Its fixed aerial was visually inspected;
  no new uncaught errors or failed resource statuses were observed. The existing
  prepared-site edge defect remains visible and is not accepted.
- 22 narrow tests pass, including stale-project response cancellation, missing
  data, fixed-path validation, retained raycasts, fallback and mask regression.
  TypeScript and targeted ESLint pass.

An early test injected a camera before startup framing finished. Its screenshot
is diagnostic, not a registered comparison. Final views explicitly claim manual
camera control first; all four final measurements report exact invariance.

Evidence is outside Git at
`C:/dev-artifacts/CityPrompt/student-design-transformation/`: `PHASE8-FINAL-*`,
`PHASE8-FAILURE-FALLBACK.png`, `phase8-final-invariance-performance.json`,
`phase8-zones-*-reload.json`, sample transforms and texture provenance.

## Measured limits

At the fixed 1600×1000 view, 5-second samples for Google, 2K capture and terrain
all recorded 16.7 ms median/16.8 ms p95 rAF intervals, with no intervals over 50 ms.
Renderer draw calls were 397 / 27 / 25; submitted triangles were approximately
0.734 M / 11.034 M / 0.033 M. The source contains 5.50 M triangles; material passes
increase submitted counts. This remains a dense single-tile sample, not LOD proof.

The texture's estimated RGBA mip storage fell from 341.3 to 21.3 MiB (16×).
These are calculated allocations, not measured GPU memory. JS heap readings are
GC-sensitive and do not establish GPU use. No frame-rate improvement is claimed.
A warm-cache sample reload took 2.83 seconds from selection to two frames after
the loaded state; this is not a cold network benchmark. Google remained usable.
The sample cache targets 64 tiles/256 MiB; visible content can exceed those targets.

Still required: real surveyed registration, classified point-cloud/DTM delivery,
geoid conversion where applicable, multi-LOD/point streaming and churn profiling,
sloped ground authority, broader object invariance, source-aware render/export
provenance and final context acceptance. The artificial placement is intentionally
insufficient evidence for production Lux Modus alignment.

# Student walking performance — local quality-preserving pass

Status: local pilot on `codex/student-walking-performance`, based on
`d32558d54`. Not deployed or pushed. The separate terrain-contact experiment
remains deferred on `codex/terrain-placement-pilot`.

## Changes

- Ordinary architectural meshes with valid, finite bounds can now use camera
  frustum culling instead of disabling it for every imported object. Meshes
  outside the camera are skipped; visible geometry is not simplified.
- Explicit source no-cull flags, instancing, skinning, morph targets, custom
  shaders and displacement maps retain conservative drawing. Bias-only
  displacement is also excluded.
- Native PBR clones retain source material sharing within one placed model.
  Each placement still owns separate mutable materials. Legacy glazing retains
  per-mesh materials because its near/far pairing depends on mesh context.
- Shared owned materials are disposed once; cached geometry/textures are not
  disposed by this path.

No geometry, texture resolution, glass response, shadows, global scale,
working-view resolution, catalogue metadata or source assets changed.

## Measured local browser comparison

Edge on this desktop, Balanced, foreground tab, 1420 × 1151 screen buffer.
Project `6ecad402-d416-4400-a708-d453e34c193d` contains five native Claude
buildings and decorative trees. Focus plan, enter Walk, click `[760,850]`.
The same walking starting view was used before and after.

| Measurement | Baseline | Final |
| --- | ---: | ---: |
| Draw calls | 681 | 671 |
| Triangles submitted | 1,894,156 | 1,890,780 |
| Monitor frame rate | 57 fps | 57 fps |
| Monitor frame interval | 18 ms | 18 ms |

This is a **small reduction in drawing work, not a demonstrated FPS gain**.
Large joined meshes spanning the camera retain conservative whole-mesh bounds.
The five tested GLBs each have one unique material per mesh, so this scene
does not exercise material-sharing savings. The sharing/isolation/disposal
regression tests cover repeated source references; no runtime-memory saving
has been measured or claimed.

The culling-only screenshot's building region `[270,180,1420,730]` was
pixel-identical to baseline. Final combined changes produced mean absolute
RGB difference 0.0000411/255 in that region (a tiny 8 × 8 difference extent),
with no visible building change. Full screenshots are retained for review.

An initial turn trace concentrated CPU samples in renderer program/material
setup. Its camera route was not identical to the final comparison, so it is
diagnostic evidence only, not an FPS benchmark. Background-tab readings around
1 fps were discarded as browser throttling, not application performance.

## Verification

- Narrow Vitest: 6 files, 100 tests passed (material preparation, native
  placement, direct 3D capture, walking, inspection and measured doors).
- `npm run type-check`: passed.
- `git diff --check`: passed.
- Browser: walking entry, turning and movement, model visibility and free
  deterministic street-view preview succeeded. Captured browser error log: empty.
- Independent code review: no remaining P0/P1/P2 findings. Review caught the
  displacement-bias exception; a witnessed red/green regression test covers it.
- No paid image/video calls; account remained at 628 application tokens.

Evidence stays outside Git at
`D:/CityPrompt-student-performance-2026-10-14/`: baseline/final monitor text and
screenshots, walking views, final turned view, free street capture and diagnostic
traces. No generated binaries are part of this commit.

## Limits and follow-up

Student-laptop performance, long-session GPU memory and multi-device frame-time
percentiles remain untested. These results do not certify laptop suitability or
all catalogue models. Paid AI output and video output were not regenerated;
the deterministic input capture and its regression tests passed.

Keep further work evidence-led: repeat this project on the affected laptop,
measure sustained walking/turning, then target the largest measured cost.
Do not silently simplify authored buildings or lower final render quality.

## Second local trial: walking queries

The walking and building-inspection queries now reject distant models using
their existing local bounds before finding and serializing zone metadata.
Each query converts its camera position to world coordinates once. A WeakMap
caches inverse placement matrices, refreshing whenever the live world matrix
changes; ancestors are updated first. Nearby candidates still validate current
metadata on every query, including same-reference edits. No persistent zone
revision cache or relaxed entrance/floor rules were introduced.

Finite diagnostic timing on this desktop, 40 distant models and 200 queries
with approximately 11 KB of serialized metadata per model:

| Query fixture | Before | After |
| --- | ---: | ---: |
| Ordinary inspection shell | 116.72 ms | 5.06 ms |
| Building walking network | 98.17 ms | 3.73 ms |

These are synthetic query timings, **not whole-application frame times**.
Regression tests assert the stable work counts instead of wall-clock timing:
8,000 distant metadata serializations become zero; camera conversions become
200 instead of 8,000. Timing instrumentation was removed from the final tests.

Verification: seven narrow Vitest files / 70 tests passed; TypeScript passed.
Tests cover parent movement, rotation and scale, cached matrix invalidation,
in-place metadata edits, deletion/unmount, walking networks, inspection,
measured doors, keyboard walking and deterministic capture. Independent code
review found no remaining P0/P1/P2 issues.

Actual local browser checks passed for walking entry, turning, movement and
walking into the Scottish Baronial hotel's entrance passage toward its
courtyard. Browser error log was empty. The starting-view building region
differed from the previous full-quality view by mean RGB 0.0000411/255, confined
to an 8 × 8 extent. No authored model, texture, material or resolution changed.
Evidence: `query-optimized-walk.png`, `query-optimized-entrance.png` and
`query-optimized-courtyard.png` in the external evidence directory above. The
last image is a view toward the courtyard from the passage, not proof of
reaching every interior route.

## Separate repeated-building batching pilot

Standalone local experiment at `http://127.0.0.1:5205/`, source and bundle under
`D:/CityPrompt-student-performance-2026-10-14/instancing-pilot/` (outside Git).
It loads the existing `clay-baronial-railway-hotel-clay-v006.glb` directly and
compares 12 placements. Fifteen opaque parts use InstancedMesh in the grouped
mode; the glass part stays individually rendered. Geometry and material values
are retained. This pilot is **not integrated into the student editor**.

Same camera, 1420 × 640 buffer, 30 warmup frames then 120 measured frames:

| Measurement | Individual | Grouped |
| --- | ---: | ---: |
| Draw calls, including transmission passes | 398 | 68 |
| Triangles submitted | 2,049,892 | 2,049,892 |
| Mean CPU render submission | 6.49 ms | 1.33 ms |
| Mean frame interval | 17.63 ms | 17.61 ms |
| 95th-percentile frame interval | 18.1 ms | 18.1 ms |

Drawing submissions fell substantially; FPS did not materially change on this
desktop. CPU submission is not GPU elapsed time. Overview and close-view
screenshots showed no visible architectural loss, but were not pixel-identical:
mean RGB difference was 0.0655/255 and 0.0599/255 respectively across the canvas.
Browser error log was empty. Evidence is `instancing-*.txt/png` beside the pilot.

Before promoting batching, validate per-instance selection, transforms,
deletion, inspection material isolation, culling, shadows and semantic capture
IDs in the real editor. This pilot does not establish those behaviours or
student-laptop suitability. Both trials remain local; nothing was deployed and
no paid renders were generated.

## Extended verification before the user trial

On the same local branch, the broader selection of walking, building inspection,
door, park walking, keyboard, material and deterministic capture tests passed:
**14 files / 144 tests**. Additional transform assertions now use a genuinely
aliased input/output vector and cover independent placements and reparenting.
`npm run type-check` also passed. No production behaviour changed in this
verification follow-up.

Actual browser checks in the existing field project:

- Added Nordic Roof-Garden Apartments, rotated it to 30 degrees, dragged it to
  another position, reloaded and selected it again. Position and rotation
  persisted, with the model visible in overhead and oblique views.
- Walked toward the moved building, inspected its entrance and transparent
  windows, entered inspection and used Return to building entrance. This is
  exterior-shell exploration, not a claim of collision-safe furnished interiors.
- Walked forward, sideways and backward and dragged to turn in the mixed
  six-building scene with decorative trees. A subsequent Balanced monitor sample
  reported 56 fps / 18 ms, 628 calls and 2,574,190 triangles at 1420 × 1150.
  The camera and scene differ from the earlier five-building benchmark, so these
  counts are a regression smoke check, not an improvement comparison.
- Free street-view 3D preview succeeded and visibly contained the same models
  from the walking camera. No paid AI request was made; balance remained 628.
- Deleted the temporary apartment, undid the deletion (model restored), redid
  it and reloaded. The original five buildings remained; the temporary model
  was gone. The final captured browser error log was empty.

Production build passed with the existing local runtime profile's verified
public directory, catalogue packet and environment. The first default build
attempt exposed unhydrated render-example and policy-map LFS pointers; exact
files were hydrated without changing LFS policy. The recovered-details guard
then correctly required the existing configured public bundle. With that runtime
configuration, catalogue/model-contract checks, recorded render-image hashes,
12 policy maps / 724 images, TypeScript and Vite all passed. Vite retained its
large-chunk and polygon-clipping import warnings; these are not resolved here.

Evidence is in `extended-*.txt/png` in the same external directory. A compact
build receipt and Vite manifest are retained. The temporary multi-gigabyte build
output remains at `D:/CityPrompt-student-performance-2026-10-14/verification-build`:
automatic approval rejected its removal with "blocked by policy" and no further
reason. It is generated output, not source or the running app's asset directory.
Student-laptop measurements and the real-editor batching integration are still
outstanding. Nothing was pushed or deployed.

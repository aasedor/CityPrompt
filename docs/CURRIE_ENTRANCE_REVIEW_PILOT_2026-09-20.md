# Currie student entrance review pilot — 20 September 2026

## Scope and decision

Worktree: `C:/dev/CityPrompt-grounding-edit-race`, branch
`codex/grounding-edit-race-hardening`. This unit adds student-facing review of
existing shared runtime geometry. It does not change native house assets,
catalogue activation, RLASM 6.1 or its machine-readable method companions.

The runtime foundation envelope comes from the conservative whole native-model
bounds in `placedNativeFootprints`, rather than an authored terrace footprint.
The exposed cap therefore cannot be treated as a walking area or automatically
railed around its perimeter. Exact-variant evidence is needed before changing
that geometry. The new panel makes the outstanding design work visible instead
of converting a clear ground warning list into an architectural acceptance.

## Implemented behavior

`Review entrances` lists saved plot names with generated approach step count,
signed sidewalk-to-model-base rise, usable width after rail intrusion and maximum
foundation support height. Measurements come from the detailed renderer's solved
sections, detail metadata and foundation vertices. They exclude native house
steps. A nearly level generated approach does not establish step-free door access.
Support height is the maximum generated foundation skirt depth; it is not the
street-to-door rise or the height of an individual landing post.

`Select and review` selects and frames the saved plot, where the existing
Connections editor is available. Current route failures replace measurements
with repair guidance. Missing, pending, obsolete and non-detailed evidence never
becomes a success claim. There is no new approval flag or persistent review state.

The first live check found all seven measurements hidden: retained display ground
and current verification use different revision formats. The fix compares source
and measured snapshot identity, then attaches the current verification revision.
It rejects previews, sampling, synchronous invalidation and changed surfaces.
Renderer-scoped records prevent a departing fallback from clearing detailed
renderer evidence; removed buildings retire their rows.

## Live vacant Currie checks

Protected original: `f5bffc94-def9-4c43-942e-9ae7411872e9`.
Disposable copy: `54bb844c-1ff4-4d67-bc7f-0c8c36d0030e`.
All writes were through ordinary UI controls on west 3 in the disposable copy.

| Saved plot | Generated steps | Signed rise (m) | Clear width (m) | Maximum foundation support (m) |
| --- | ---: | ---: | ---: | ---: |
| Shared street west 2 | 14 | +2.35 | 1.64 | 1.48 |
| Shared street west 3 | 10 | +1.79 | 1.64 | 1.07 |
| Shared street west 4 | 3 | +0.41 | 1.49 | 0.77 |
| Shared street east 1 | 0 / nearly level | +0.04 | 1.96 | 0.51 |
| Shared street east 2 | 3 | -0.39 | 1.96 | 0.69 |
| Shared street east 3 | 4 | +0.60 | 1.96 | 1.53 |
| Shared street east 4 | 1 | -0.08 | 2.12 | 0.55 |

The ready panel was compared with actual scene approach metadata. West 3 selection
opened the correct Connections editor. Saving 1.2 m total width produced the
clear-width warning and hid its obsolete 1.64 m value. Escape closed the dialog;
Undo restored the value, Redo restored the warning, final Undo/reload restored all
seven approaches and rows. Every copy zone's coordinates and full properties,
including compiled markers, match this turn's baseline. The original's full zone
response matches the preceding checkpoint. No model plan/place API requests or
page errors were observed during this cycle. The request log contains one source
module GET whose filename starts with `plan`; it is not a compilation request.

A separate live reload opened the panel during sampling. No numeric measurements
were visible; they returned in the same dialog when ground became ready. Scrolling
to the final row and keyboard focus/Escape passed at 1024×768, with the initial
panel also inspected at 1440×900. Touch/mobile and screen-reader use were not tested.

Free exact 3D export downloaded and was visually inspected. Seven houses, street
and park are visible; the scene retains 18 approach/detail meshes, current ground
and no grounding issues. This aerial capture checks export continuity, not a new
close-view architectural approval. Prior side-detail low views remain the latest
geometry-specific evidence. No paid rendering or publication occurred.

One harness attempt ran after a source hot reload had closed Connections; it
stopped before any write while waiting for the width input. Reopening the actual
review/selection flow allowed the complete cycle above. The first freshness
failure was a real implementation defect and is covered by regression tests.

## Checks and local evidence

104 tests pass across 11 focused suites: `buildingEntranceReview`,
`BuildingEntranceReviewPanel`, `BuildingEntranceApproaches`,
`buildingEntranceApproach`, `BuildingGroundProblems`, `buildingGroundContact`,
`pedestrianCapture`, `pickBuildingEntrance`, `ConnectionEditor`,
`pedestrianConnections`, and `useAutomatic3D`. Type-check and changed-file ESLint
pass. React review: stable state setter/report callback, renderer cleanup,
no new fetching or persisted state, geometry retained while only review evidence
changes with verification. The panel uses the shared focus-managed dialog.

Artifacts are outside the source tree at
`C:/dev-artifacts/CityPrompt/grounding-batch-a/`:

- `review-panel.png`: initial unavailable-metrics failure.
- `review-panel-ready.png`, `review-panel-bottom.png`: corrected seven-row UI.
- `review-baseline-zones.json`, `review-width-warning.png`, `review-recovery.json`:
  selection, failure, recovery and fixture preservation.
- `review-pending.json`, `review-pending.png`, `review-1024-bottom.png`: live
  sampling/recovery, smaller desktop view and keyboard observation.
- `review-free-export.png`, `review-export-state.json`: exact capture and ownership.
- `review-evidence-sha256.json`: local manifest, not a shared artifact backup.

| Evidence | SHA-256 |
| --- | --- |
| `review-recovery.json` | `2055a86546cf474dda3e4a8028099c703821ba271ae3d3efaacb7598e3713414` |
| `review-pending.json` | `86b6154a47ba62c331758e80122b39abc9ab237725fa2f0ff151e0211180b855` |
| `review-free-export.png` | `b59b28b28f10fe831d2a3aa51fddb20622e97093b1918d30b3c344fb8736aa04` |

Shared runtime guidance and the per-variant template now require fresh measured
review evidence, preserved selection/recovery, and separate support/terrace and
approach/accessibility decisions for subsequent archetypes.

## Next bounded work

1. On one exact native house, document which step/landing edges are authored
   pedestrian surfaces, the generated-to-native rail join, and furniture clearance.
   Use front/side/low views and exact asset identity before changing an edge model.
2. Develop and test a supported accessible alternative through the whole route
   to the door. A flatter plot alone may leave native steps; the current UI keeps
   that limitation visible. Do not invent a ramp or claim accessibility from slope.
3. Complete a novice-authored placement → entrance → street/park → edit/recovery
   → presentation pilot using ordinary controls without supplied offsets.
4. Reproduce/fix the legacy Generate to 3D locked-recipe mismatch separately.

This checkpoint improves review visibility and recovery. The open architecture,
accessibility and novice workflow cases still prevent a student-ready declaration.

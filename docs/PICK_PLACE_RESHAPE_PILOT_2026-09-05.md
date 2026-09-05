# Pick, place and reshape — local student pilot

The globe now starts with a small object catalogue. Students choose an object,
position a live 3D preview and click to place it. Selecting a placed object opens
move, reshape, rotation and duplication controls. Saving automatically rebuilds
the 3D scene; a separate Generate step is no longer part of this pilot's normal
workflow. Custom drawing remains under More Tools.

## Scope and location

- Branch: `codex/pick-place-reshape-pilot`, worktree `C:/dev/CityPrompt-place`.
- Based on the prior neighbourhood park pilot, `d96ae32ac`.
- App: <http://127.0.0.1:5174/projects/de492723-417b-4729-a76c-f797cc8528d6>.
- Local project: **Pick, place and reshape — student pilot**.
- Empty field near Fort Calgary, centre 51.04542, -114.04677. The instructor
  setup supplied a 90 × 93 m boundary. Every building, park and road was then
  placed through the browser UI, rather than seeded into the database.
- The original OneDrive checkout and its pre-existing work were left intact.
  No deployment, push, new building generation or catalogue promotion occurred.

The catalogue has two choices: the existing exact `infill_flat_roof_minimal`
architectural-clay family, and the prior `neighborhood_park_v0` adaptive rustic
park pilot. The Road tool supplies a narrow residential street with sidewalks;
existing road settings remain accessible. This establishes the interaction
pattern before adapting additional families.

## What the student trial demonstrated

| Action | Observed result |
| --- | --- |
| Pick a home, move preview, click | A 12 × 16 m home plot saved and automatically displayed its exact clay asset. |
| Widen that plot to 36 m | Three complete houses appeared, each at native scale, separated by 3 m gaps. |
| Add a second, smaller plot | One more house appeared; the saved scene contains four homes across two plots. |
| Place a park | The initial 40 × 35 m park appeared without a Generate step. |
| Resize, move and turn the park | Numeric dimensions, body dragging, corner dragging and 15° rotation saved correctly. The final park is approximately 36.4 × 33.3 m. |
| Undo/Redo after an automatic rebuild | Restored the prior 40 × 35 m footprint, then reapplied the corner edit, without a revision conflict. |
| Attempt overlap or an oversized footprint | Placement/reshape was rejected and the saved scene stayed unchanged. Escape cancelled an unplaced preview. |
| Draw a street beside the park | A sidewalk street appeared automatically; the existing access solver produced a 2.2 m path from the near-side sidewalk into the park loop. |
| Turn the narrow home 180° and restore it | The chosen frontage and native dimensions survived server replay and return to 0°. |
| Reload the project | Both plots, four native houses, the rotated park and street persisted. No unnecessary rebuild was sent solely because of reopening. |
| Use a 390 × 844 viewport | Map controls remained accessible, picking exposed a centre crosshair and Place at centre/Cancel controls. Invalid placement and cancellation were tested. This was viewport emulation, not physical-device testing. |
| Open Render and run Check Direct Capture | The free capture succeeded with beauty, mask, class and instance controls. A separate full capture also produced depth, normals and material controls. |

The close oblique capture includes all four homes and the sidewalk connection.
Ground sampling was ready with 1,190 samples, two stable passes and zero
between-pass height difference at capture time. The maximum local residual was
approximately 0.165 m. This demonstrates seating on this Google tile surface;
it is not a survey accuracy claim or validation on every terrain type.

## Issues found and fixed

1. **Wrong model lookup:** the preview initially asked for a parent archetype.
   It now requests the exact approved variant used by placement.
2. **Surprise rotation:** long-axis fitting could turn a narrow plot by 90°.
   The explicit home-plot mode now preserves the first footprint edge as the
   frontage through aspect-ratio changes and a full turn. Client planning,
   server replay, containment and globe placement use that convention.
3. **Undo conflicts after automatic work:** derived compilation writes advanced
   zone revisions. Undo now follows those writes only over its own exact source
   revision; another editor's revision is not silently adopted. Automatic
   compilation does not recover a foreign source change by overwriting it.
4. **Extra landscaping:** automatic placement previously filled unused land.
   `include_residual_landscape=false` persists `placed_objects_only` on the
   boundary. Both UI and server render checks support that explicit state,
   while retaining physical-object fingerprints and instance ownership checks.
5. **Unnecessary ground resampling:** a metadata-only boundary update previously
   invalidated terrain. Physical sampling identity now depends on boundary
   geometry and tile masking; capture provenance still carries the current row
   revision. New tile detail continues to trigger real resampling.
6. **Plain road with no park arrival:** the new workflow now has a sidewalk
   street preset. The existing access solver can connect to that pedestrian
   band instead of inventing a crossing of the carriageway.
7. **Phone controls:** overlapping control rows and a placement-error toast
   covering Cancel were corrected. The guide now explains pick/place/reshape.

## Implementation contracts

- Zones remain the saved spatial source of truth. Moving and resizing updates
  that geometry; the compiler derives renderable 3D from the same data.
- `native_home_plot` is opt-in, exact-variant-only and limited to detached-home
  families. Native model scale is `[1,1,1]`; default clay placement remains one
  building. The pilot home stays two storeys. This adds no floor repetition or
  arbitrary deformation to RLASM v6.1.
- Park furniture retains metre dimensions. Its deterministic composer fits
  circulation, planting and activity areas into the edited boundary.
- Preview updates are local to the preview component and throttled. Asset
  loading and dimension-specific plan requests are cached. Compilation waits
  for saves, debounces edits and queues the latest change behind an in-flight
  request; it does not recursively rebuild its own metadata.
- Placement and reshape reject object overlap and full-footprint boundary
  violations. The controls describe plot dimensions rather than promising to
  stretch a fixed native building.
- No new packages or heavyweight production assets were added.

## Verification and evidence

- 114 frontend tests passed across 12 targeted files, including placement,
  geometry, compile coordination, undo, grounding and render readiness.
- 99 backend tests passed across native home plots, clay runtime, detached
  assembly and ground provenance; 12 Direct 3D preflight tests and two residual
  compilation endpoint cases also passed (113 total across these runs).
- TypeScript type checking, targeted ESLint and `git diff --check` passed.
  Both RLASM machine companions parse and contain identical pilot contracts.
- Browser trial used the isolated local student account and database. Paid
  image/video providers were disabled; no image/video API budget was spent.
  Existing Google Maps tile/elevation requests were used for the terrain test.

Screenshots, scripts and capture controls are ignored local output under
`C:/dev/CityPrompt-place/artifacts/pick-place-pilot/`, separate from source:

- `18-rotation-saved.png`, `19-undo.png`, `20-redo.png` — park editing.
- `23-invalid-preview.png`, `24-home-preview.png` — placement feedback.
- `26-sidewalk-street.png` — street and park connection.
- `27-guide.png`, `32-mobile-controls.png`, `33-mobile-ready.png` — guidance
  and responsive controls.
- `38-capture-passed.png` — the free render capture check.
- `final-beautyImageBase64.png` — close oblique, unenhanced 3D capture.
- `final-classIdImageBase64.png`, `final-instanceIdImageBase64.png`, depth,
  normal and material images plus `capture-manifest.json` — scene controls.

The running frontend uses the prior park pilot's local public-asset overlay at
`C:/dev/CityPrompt-park/artifacts/park-pilot/public`, with API proxy target
`http://127.0.0.1:8002`. The backend harness is the ignored
`artifacts/pick-place-pilot/runtime.py`. This setup is a local review environment,
not a portable production deployment.

## Limits and next steps

The interaction pilot is ready for review. The catalogue is intentionally small.
Each additional building family needs an explicit reshape rule: repeat complete
homes, adjust supported modules, or retain a fixed landmark. Freeform imports
and the broader catalogue still use the existing advanced drawing workflow.

The preview follows the cursor's tile height; final objects wait for shared
ground sampling and foundation checks. During new tile loading, objects can
temporarily disappear while ground is re-established. Reducing that interruption
is a remaining usability/performance improvement. Steep and irregular sites need
their own trials. Collision checks do not identify every existing object in
Google's photogrammetry, which is why this pilot used an inspected empty field.

The park is the inherited visual pilot, not a newly approved final asset. Its
ground edge and material integration still deserve refinement. The capture
tests validate inputs to rendering; they do not prove final AI image/video
fidelity, and no paid final AI render was generated. House plots currently have
one semantic capture identity per plot, with multiple physical home instances.
Individual household-level editing and per-house capture identities would need
a subsequent data-model extension.

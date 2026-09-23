# Ideation snapping — 2026-09-20

## Product direction

City Prompt is for fast, enjoyable student ideation. Ordinary placement should
help an idea fit: preview a usable position, settle beside neighbouring plots,
connect to a nearby sidewalk, and keep Undo simple. Manual connection coordinates
must be an optional adjustment, not the normal first task for each building.
Preserve useful geometry checks underneath this assistance; do not replace them
with a sequence of rejection messages the student has to solve.

## Implemented

- Shared bounded snapping for new building placement, live building moves and
  building shape commits. Translation preserves plot size and rotation; clear
  placements remain unchanged. Invalid moves retain their last valid preview.
  The search uses plot edges and site edges, including irregular sites, and
  validates candidates against all neighbouring plots. The nearest available
  candidate is chosen within a 30 m search; this is not a globally optimal CAD
  packing solver. Plot boundaries already include space around native models.
- Existing connected pedestrian approaches and street space are protected.
  Street reserves include 3 m outside the section for concept entrance room;
  this is a product spacing heuristic, not a regulatory setback. The new
  automatic approach must have at least 2.5 m of plan run.
- Place another now enables street-facing placement for the next building.
  Authored streets take precedence over mapped context roads, including stale
  proposed roads. Automatically connected homes also face the nearby street
  when moved; explicit manual connections retain their existing behavior.
- The shared entrance relationship can use `automatic: true`. The nearest
  supported authored sidewalk is resolved from the current scene on render,
  review and capture, so movement, street changes and coordinate Undo do not
  need a second asynchronous property save. Capture ownership follows the
  current target street. No nearby sidewalk means waiting for one, not inventing
  a path across empty ground. Obstructed routes remain unresolved.
- The reviewed **Calgary Modern Infill / Flat Roof Minimal, one 12 × 16 m plot**
  receives its native entrance automatically on placement. Its current clay
  model is `calgary-infill-flat-roof-minimal-clay-v006.glb`; the step-foot anchor
  comes from the inspected Currie exercise. Variant changes and unsupported
  repeated native plot sizes do not inherit this one-home automatic anchor.
- Connections retains manual controls and a nearest-sidewalk switch. Existing
  manually authored relationships are preserved, not bulk-rewritten.

## Bounded verification

78 focused Vitest tests passed across ten files; TypeScript and changed-file
ESLint passed. Cases cover clear/overlapping/rotated plots, multiple neighbours,
concave boundaries, impossible spaces, both street sides, target changes,
manual anchors, variant/size guards, and preserving existing pedestrian access.

Live student controls in the disposable project
`7e1e9037-b98c-4d18-8502-839160315869`:

1. Placed one additional native home without opening Connections. It created
   a connected path automatically. The saved scene now has eight homes and
   eleven total zones. Earlier seven-home evidence remains a historical checkpoint.
2. Dragged that house into its neighbour. An early attempt exposed a missing
   street/path reserve and an old mapped-road orientation; fixed both shared
   behaviors and repeated the test after reload.
3. The final move settled beside the neighbouring plots with all eight building
   routes connected, the street ready, and no grounding/entrance issues.
4. Undo changed the saved coordinates; Redo restored the snapped coordinates
   exactly and retained automatic mode. No page errors.
5. Reload preserved all eleven zone IDs, geometry and properties exactly, with
   no page errors or grounding issues.
6. Normal free exact export produced a visually inspected preview in 2,431 ms
   from a ready scene. The browser automation connection stopped responding
   during the subsequent download operation; this run does **not** claim a
   verified downloaded PNG. Prior exercise download evidence is separate.

External evidence remains under
`C:/dev-artifacts/CityPrompt/grounding-batch-a/currie-clear-route/`:
`snap-fresh-placement.png`, `snap-protected-move.png`, `snap-readback.json`,
`snap-undo-result.json`, `snap-reload-result.json`, `snap-export-preview.png`.
No paid generation, protected project edits, generated source-tree output or
remote push. The initial browser retained stale interaction listeners after
hot reload; acceptance was repeated with a full page reload.

## Catalogue rollout

Collision snapping is shared building behavior. Default automatic entrances
are currently registered for the one reviewed infill variant, not the entire
catalogue. Each new exact variant must register its actual step-foot anchor,
supported plot dimensions, width/base datum and model evidence in its placement
record, then pass the same place/move/Undo/reload/export exercise. Multiple
buildings on one repeated plot need a per-instance entrance design; one plot
anchor must not masquerade as access to all of them. No generic box-centre door
guessing and no variant-specific manual-coordinate instructions for students.

Next: expand the entrance contract to the next reviewed building variant and
per-instance repeated homes in a finite pilot. Keep the ordinary classroom
workflow simple; use advanced controls only when the student requests them.

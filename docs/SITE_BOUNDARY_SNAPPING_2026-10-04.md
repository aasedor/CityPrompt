# Site-boundary snapping — 2026-10-04

Shared authoring change on `codex/site-boundary-snapping-2026-10-04`, based on
street-edge checkpoint `4fc6ec39d`. Uses the existing maintenance checkout;
no extra worktree or asset generation is involved.

## Behavior

- Building/residential plots, parks, and complete street footprints attract to
  the active site boundary within three metres. Small overhangs within that range
  can move back inside. The target is 8 cm inside the boundary to avoid unstable
  point-on-edge classification. The earlier street endpoint entrance snap retains
  its six-metre range and perpendicular full-width end-cap behavior.
- The entire saved plot moves. No clipping, shrinking, automatic rotation,
  native-model change, street-width reduction, or automatic rearrangement of
  previously saved designs occurs. Existing manual/automatic entrance alignment
  rules remain in the building resolver.
- A shared bounded solver handles edge winding, rotated and concave boundaries,
  square and oblique corners, and narrow parcels. Existing contact constrains the
  next correction, avoiding oscillation between nearby opposite edges.
- Building/park candidates pass the existing plot, street, collision, entrance
  and reserved approach checks. Street candidates additionally preserve working
  junctions and refuse unsupported overlaps. Invalid or impossible placements
  retain the relevant validation error; deliberately authored public-road
  extensions retain their separate connection validator.
- Picker placement and body dragging use the shared snap. Freehand building/park
  polygons resolve on submission. Street drawing preview and submission share
  the same full-width geometry; endpoint editing reuses the endpoint resolver.
- Street translations carry both persisted centerline and authored route
  controls. The shared save helper now also carries source routes for rigid
  translations of older procedural streets. An irregular legacy outline edit
  does not infer a replacement source route.

The active boundary is the saved planning polygon. A decorative landscape inset
or satellite feature does not redefine it. No legal setback claim is introduced.

## Verification

251 focused tests passed in 12 Vitest files: boundary footprint and street
placement, existing endpoint snapping, drawing/preview geometry, snap placement,
connected street editing, street coordinate updates, zone persistence/recovery,
polygon geometry, building edge placement and three entrance/approach suites.
TypeScript checking and `git diff --check` passed. Tests include small overhangs,
oblique corners, concave containment, blocked attractions, narrow-site stability,
route-property parity through procedural body movement, public extensions, and
rejection of an already-disconnected street edit.

React review: both editor changes use existing event handlers/ref previews;
there are no new hooks, effects, requests, event listeners, dependencies or UI
controls. Candidate searches remain bounded; source inputs are not mutated.

Browser pilot used only the isolated copied database `cityprompt_repairs_20261004`
and frontend/API ports 5177/8008. Before/after zones, screenshots and measured
receipts are outside Git in:
`C:/dev-artifacts/CityPrompt/site-boundary-snapping-2026-10-04`.

| Pilot | Earlier boundary gap | Saved gap | Result |
| --- | ---: | ---: | --- |
| Rustic Pocket Garden | 7.709 m | 0.080 m | Moved near edge; shape, angle and identity preserved |
| Current Buff-brick infill | 4.076 m | 0.080 m | Dragged into attraction range; plot/model identity preserved |
| New Quiet Residential Street | N/A | 0.080 m | Full 18 m section saved parallel to the boundary |

The saved-coordinate verifier passed containment/collision checks for all three.
Street undo removed its row and redo restored the same coordinates. Reopening
Currie rendered the saved park/building placements with `3D saved`, `Drawings
saved`, and no captured console errors. The street's post-save state rendered
before reload; its post-reload browser inspection was interrupted by closure of
that temporary tab, so saved-coordinate recovery is the reload evidence there.

A transient native-route length warning appeared while the cursor was near the
second street control. Completing the same 251 m two-point route succeeded;
the existing cursor-continuation preview warning remains a recorded follow-up.
The pilot is bounded evidence, not a visual approval of every catalogue variant.
No paid image generation was used.

## Checkpoint

Source changes are local and ready for review. Original port-5176 runtime and
source database remain untouched; no main-branch integration or push was done.
Nine registered worktrees remain. No generated output is staged.

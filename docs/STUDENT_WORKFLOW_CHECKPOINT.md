# Student workflow checkpoint

The globe workspace now starts with **Site → Design → Present**. An empty
project shows boundary drawing and an explicit confirmation action. Existing
projects with a boundary open in Design. Buildings, Parks and Streets remain
the primary authoring controls. Render this view opens Image / Video choices
using the existing render handlers. Navigation does not replace the canvas,
change the camera or rewrite saved project state.

Custom drawing, history, properties, compilation and planning remain available
through existing advanced controls. Site analysis is explicitly optional and
loads only when expanded. The current image/video panels are unchanged; their
provider/style complexity is a later phase, not a completed simplification.

## Verification

- Three narrow Vitest suites / 35 tests: workflow, placement palette and object
  properties. Type-check and targeted ESLint pass.
- Live backend / frontend and Google context: Site, Design, Present, Image,
  return to Design. Camera position and quaternion remained exactly equal.
- Inspected 1600 × 1000, 1366 × 768 and 900 × 768 screenshots. Fixed a collision
  between view controls and project tools. Property panels sit below globe
  controls; desktop canvas remains the main workspace.
- Keyboard Tab / Enter navigation works with visible focus. Step targets are
  77 × 48 CSS pixels at the narrow tested width; no document horizontal overflow.
- New local test project `c5f73929-f949-41d2-ac7d-0340e09339e7`: searched Currie,
  selected the resolved address, created the project, drew a four-corner site
  with pointer input, saved, confirmed and opened Buildings. A detected early
  jump into Design was fixed and the drawing flow repeated successfully.
- Clean reload and boundary review: no new console errors or failed requests;
  collapsed site analysis made no requests. Older cumulative missing-asset
  failures are baseline setup evidence, not new UI failures.

Evidence: `C:/dev-artifacts/CityPrompt/student-design-transformation/PHASE2-*`,
`phase2-navigation.json`, `phase2-clean-review.json`, `phase2-fresh-project.json`.
Heavy screenshots and test projects are local only. No paid image/video request;
the API ledger reserves US $1 conservatively for Maps validation rather than
assuming free-tier coverage. The US $10 aggregate ceiling remains in force.

## Open findings

The full novice journey is not yet accepted. Catalogue coverage and editing
remain subsequent phases. A boundary undo attempt returned HTTP 409 after
derived grounding updated the zone; dedicated undo/revision investigation is
required before persistence acceptance. An agent navigation to `/projects/new`
produced 422s: creation actually uses the Projects page's New Project button.
This was not a visible broken link. No production data or benchmark geometry
was altered by this UI checkpoint.

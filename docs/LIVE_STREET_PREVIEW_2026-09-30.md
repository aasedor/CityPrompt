# Live street drawing preview

The 3D globe now previews the selected street after the first clicked waypoint.
The provisional segment follows the pointer; clicked points remain when the
pointer leaves the canvas. Backspace removes a waypoint and Escape clears the
draft. Enter saves only confirmed waypoints, using the same snapping, rounding
and buffering function as the preview.

The draft reuses the normal street surfaces, materials and verified native
modules. It does not fabricate a compiled recipe, call a generation service,
save zones or debit credits. It lives under the capture-excluded editor group
and unmounts during capture. Cursor updates are confined to a small subtree,
limited to roughly eight per second, with stable selected-street materials.
Production asset verification and final route/fit validation remain unchanged.

## Evidence

- PASS: 66 focused frontend tests across route geometry, preview lifecycle,
  snapping, editing, picker controls, native modules/readiness and drawing.
- PASS: TypeScript check and Git whitespace check.
- PASS: browser cursor preview of Amsterdam Gracht, Neighbourhood Main Street
  (including a bend), and BRT Bus Rapid Transit Corridor.
- PASS: browser Backspace and Escape; no new saved road from cancelled drafts.
- PASS: prepared-site pilot using ordinary drawing controls: first-point
  preview → second point → Enter → 3D saved; API readback confirms exactly one
  road with `student_main_street_v1` and compiled state.
- No paid images or videos requested. Native assets/variants are unchanged;
  this does not expand their visual approval or slope support.

External screenshots and the disposable QA setup script:
`C:/dev-artifacts/CityPrompt/live-street-preview-2026-09-30/`.
QA project: `d3794c04-7c7b-4b6f-a3ba-fdf6c8af953f` on localhost:5183.

## Limits

On an unprepared sloping site, a draft is an approximate placement preview;
existing prepared-level requirements still apply at save. Final intersections
and shared-ground reconciliation run after finishing. Browser coverage here is
three representative streets, not a new acceptance review of all variants.
The older 2D map remains a line-based editor; this feature targets the current
3D globe. Mobile touch interaction and paid capture are not browser-tested.

One existing route-edit test passed a sampled curve to the point-spacing check
without its stored authored controls. Updated that assertion to match the
production call, preserving the real minimum-spacing rule.

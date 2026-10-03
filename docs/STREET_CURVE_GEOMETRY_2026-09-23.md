# Curved street route checkpoint — 2026-09-23

Branch: `codex/native-street-catalogue-pilot`. This checkpoint gives students a
curved centreline for newly drawn roads and for bend edits on fixed-section
catalogue streets. It also exercises both exact native street candidates on
curved metric routes. It does not approve those candidate models for the picker.

## Source-informed geometry, not engineering certification

- [Calgary's current Street Manual project page](https://www.calgary.ca/planning/city-building-program/city-building-program/the-street-manual.html)
  identifies the Manual as still in development. The available
  [Draft 3.0, chapter 3](https://www.calgary.ca/content/dam/www/planning/temporary-pdfs/SM_DRAFT%203.0%20Street%20Manual%20Ch%201%20to%208.pdf)
  points Calgary horizontal alignment toward TAC and distinguishes ordinary
  street curves from higher-speed, superelevated designs.
- [TAC Geometric Design Guide chapter 3](https://www.tac-atc.ca/en/knowledge-centre/technical-resources-search/publications/ptm-geodes3-e/)
  covers horizontal/vertical alignment, cross slopes and lane widening. The
  full chapter is licensed and was not treated as an available table of
  minimum radii.
- [NACTO Urban Street Design Guide: Design Speed](https://nacto.org/publication/urban-street-design-guide/design-controls/design-speed/)
  calls for context-appropriate target speed rather than accidentally creating
  high-speed urban geometry. Its intersection curb-return advice is not a
  centreline-curve-radius rule.

The implementation uses tangent circular arcs in local metres. The authored
endpoints stay exact for snapping and intersections; bends consume at most 45%
of each neighbouring arm, so adjoining arcs have space between them. The
suggested radius scales with the full street section and is bounded by the
available site geometry. It is a visual teaching default, **not** a TAC or
Calgary design-speed check. It does not calculate superelevation, sight distance,
swept paths, lane widening, winter maintenance or drainage.

## Shared route contract for subsequent street archetypes

`frontend/src/utils/streetRouteCurves.ts` owns the reusable WGS84/metric curve
sampler. Newly drawn roads use its sampled centreline for the saved road
footprint and 3D surface; fixed-section streets additionally save their small
`plan_route_controls` array for editing. Bend edits round the controls and
update the footprint and `plan_centerline` in the same request. Moving and
rotating a sampled street carries the controls by the same rigid transform.
Undo/Redo restores controls, sampled line and paving together. Non-fixed
procedural roads still use their existing endpoint snap and server source
synchronization.

This is the route pattern to reuse for each new street archetype: keep the
authoritative metric cross-section and native assets unchanged; sample its
centreline once; construct every paving band, marking, curb, sidewalk and
furniture pose from that line; leave junction approaches tangent/clear; store
editing controls separately from surface stations. Do not stretch an assembly
or infer geometry from an image. A future target-speed-aware design assistant
may warn about curves that are too tight for a chosen street role, but should
not block a student's concept based on a fabricated standards threshold.

## Evidence and limits

The local `/native-street-pilot-review.html` now shows a main-street S bend and
a rounded 90-degree pedestrian market turn. The surfaces and native furniture
follow the route, and hardscape trees remain paired with their wells. A browser
visual inspection found no console warnings/errors. Focused geometry, editing,
Undo/Redo, module and curved-T-junction tests passed, as did TypeScript and
touched-file ESLint. The frontend production build and 20 narrow backend road
network/API tests also passed. The isolated review has no Google Tiles or saved
project.

The next acceptance gate is a disposable copy of the vacant Currie parcel in
the authenticated student UI: draw a curved street through several waypoints,
add/move a bend, connect it to another street, Undo/Redo, reload, export and
inspect 3D at ground level. Check the actual full ROW against the winding west
road and straight east road before any student-picker rollout. A curb-return or
crosswalk at a node needs its own intersection design review; smooth midblock
centreline geometry alone cannot certify it.

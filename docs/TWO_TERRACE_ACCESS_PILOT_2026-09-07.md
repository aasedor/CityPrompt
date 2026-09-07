# Two-terrace access pilot — 6–7 September 2026

## Scope and local trial

Branch: `codex/two-terrace-access-pilot`, based on `3e8afb6ff`.
Isolated checkout: `C:/dev/CityPrompt-building-next3`.
Frontend: `http://127.0.0.1:5178`; backend: port 8002.
The original OneDrive checkout and its runtime were not modified.

Student project: **Beta D - Two terraces and graded access**
`http://127.0.0.1:5178/projects/f289f565-1a52-43ec-accc-38cb5ac24ea2`

The project, boundary, park and building were created through the interface.
The site is on the open/wooded hillside near Salisbury Avenue SE, away from
existing buildings. The first narrow boundary could not fit the minimum
30 × 30 m neighbourhood park; it was replaced with a wider hillside boundary.
This is a grading experiment, not a recommendation to redevelop this location.

## Implemented

- Optional **Terrace & path** controls on catalogue building and park plots.
  A versioned `proposed_terrace.offsetM` is relative to the prepared site's level.
  It follows the plot when moved or resized, using ordinary property saves and
  undo/redo. Convex plots only in this pilot; no guessed concave cutouts.
- The existing shared prepared-ground resolver now includes this offset.
  Buildings, park structures, surfaces and their terrace use the same datum.
- The prepared site surface has actual cutouts beneath terraces and graded
  routes. A lowered terrace is not covered by the original flat site surface.
  Terrace retaining faces include path openings; connecting paths have side
  faces down/up to the prepared site level.
- An explicit versioned `terrace_connection` stores destination, edge positions,
  width and building approach length. Routes recompute from current plots.
  The park approach follows an inward line to its actual walking loop and avoids
  fixed modules. Trees, shrubs and loose details clear the new park approach.
- **Find a clear connection** performs a finite search on student request.
  A small plan preview identifies edges; detailed entrance controls are folded
  away. The preview reports length and connecting grade. Over 5% triggers a
  design prompt, not a design prohibition or a legal accessibility verdict.
- **Report** includes live terrace access notes, with a separate text download.
  These notes are not part of the versioned backend planning-report export.
- Existing simple building/park-to-sidewalk connectors report unresolved access
  when they would cross a terrace wall. They no longer claim that a flat
  connector through that wall is a valid connection. The saved design and
  rendering remain available.

## Bugs found and fixed during the trial

1. A family-pending backend marker hid the explicit adaptive neighbourhood
   park's local geometry. Its named procedural pilot now mounts independently
   of a pending external asset family. Generic fallback parks still do not
   acquire an inferred legacy assembly.
2. Rebuilding a square park from a building origin versus its own origin could
   change the longest-edge orientation and random planting. The park now builds
   once in its own stable coordinate frame and transforms that same layout for
   each caller. Rendered loop, planning diagram and path endpoint agree.
3. Nearest-point park approaches could clip a plot edge. The pilot searches an
   inward route to the loop and reports unresolved access when none fits.

## Observations and verification

- Saved two levels: initially building +1 m and park −1 m relative to the site.
- Moving the building increased the connecting run and reduced its grade from
  about 14.3% to 11.4%. After the coordinate-origin fix, the complete route
  measures 29.1 m, including its level approaches.
- Resized the building plot from 15 × 20 m to 18 × 20 m. Its terrace and path
  followed. Undo restored approximately 15 m and the earlier path; redo restored
  18 m and its corresponding path. Read-back confirmed both values.
- Changed site level from 1054 to 1050 m. Relative offsets and path grade stayed
  consistent; endpoints changed together to 1051 and 1049 m.
- Saved 110 repeatable boundary samples for the outer retaining edges. Original
  visible-surface samples ranged roughly 1042.5–1054.8 m, including vegetation.
  These are Google visible-surface heights, not a bare-earth survey.
- Finally lowered the building offset to −0.3 m. The park remained −1 m. The
  route reports approximately 29.1 m length and 4.0% connecting grade. Both
  objects remain editable, with the site surface cut away around them.
- Save/reopen preserved the geometry and connection. Exact 3D capture generated
  a loaded 1600 × 936 image containing the terraces, retaining edges, park and
  path. No AI renders or paid generation calls were used.
- Automated browser downloads of both the image and text notes returned
  `Download was canceled`. Image capture itself succeeded; its displayed data
  was saved directly for QA. Normal desktop download behavior still needs a
  manual check; do not report the download interaction as passed.
- The browser retained 12 earlier hot-reload exceptions from a missing
  `cutGeometry` import that was fixed during implementation. Final reload and
  saved-data verification did not add any new exceptions to that buffer.
- 176 tests passed across the nine affected geometry, park, connection and
  editor suites. TypeScript checking and targeted ESLint passed.

QA files are outside Git under
`C:/dev-artifacts/CityPrompt/student-beta-2026-09-06/`, with the `terrace-` prefix.
`terrace-final-direct3d.png` and the closer `terrace-detail-direct3d.png` are
free exact captures, not generative renders.
No catalogue models, generated binaries or local database fixtures are included
in this source checkpoint.

## Limits and next pilot

- This is a two-terrace concept workflow inside a level prepared site, not
  terrain-following earthworks. Broad sloping sites can still require large
  cut/fill and retaining walls. The pilot does not calculate earthwork volumes,
  drainage, wall structure, edge protection or accessibility compliance.
- The path reaches an explicit building plot approach; it does not automatically
  identify a model's door or stair landing. Students must align that end. Next,
  use the existing saved entrance anchors and explicit landing geometry.
- Connections to modelled streets or imported existing sidewalks need their own
  terrace landing/crossing design. This pilot neither invents existing sidewalk
  elevations nor routes through retained buildings or roads.
- Blocked/out-of-site approaches remain unresolved, with no substitute path
  placed elsewhere. Some oblique approaches require repositioning the objects
  or choosing better-aligned edges. Curved ramps and switchbacks are not built.
- The 30 m park is intentionally a reduced programme; equipment is not squeezed
  into it or relocated elsewhere. Test a larger park in the next composition.
- The placement size card covered a desired map click near the bottom of the
  screen. Recentring the map worked around it; a draggable/docked placement card
  deserves a separate UI initiative.

Next bounded trial: a building entrance landing → terrace path → explicit
sidewalk landing, with a longer alignment on the same hillside. Inspect at
ground level from both directions before extending the catalogue or claiming
student readiness. This branch is local only; no push or deployment performed.

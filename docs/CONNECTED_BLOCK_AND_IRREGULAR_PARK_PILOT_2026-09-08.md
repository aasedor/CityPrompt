# Connected block and irregular park pilot — 8 September 2026

## Outcome

Catalogue parks now have editable individual corners, triangle and L-shape
presets, and an Add outline point control. Resizing preserves the full outline.
Neighbourhood parks find room for full-size equipment and paths inside irregular
boundaries. Narrow or deeply concave spaces keep a lawn-and-planting layout when
the complete programme cannot fit. Basketball now has a bounded search for a
complete court precinct inside an irregular park, with its original metric
dimensions, clear run-off, paths and benches.

This does **not** certify every catalogue park for arbitrary shapes. Tennis,
soccer, cinema, teaching garden and concert parks still use their established
layout rules and need separate irregular-footprint pilots. Their fit notes are
now visible in the reshape panel. An unusable sports footprint never produces a
compressed or cropped court.

## Local fixtures and student actions

Runtime: frontend `http://127.0.0.1:5177`, backend port 8002, checkout
`C:/dev/CityPrompt-building-next3`. Branch: `codex/connected-block-pilot`.

- Connected block: project `4246a88b-1c06-4524-b48f-5c493144b7c3`.
  Four 12 × 16 m infill-home plots in a close row, two 16 m Calgary local
  streets forming a T, and a 35 × 35 m neighbourhood park. Created and arranged
  with the browser tools; entrance links selected through Connections.
- Irregular parks: project `8d0df60c-7cd5-4dec-9e21-49ffb02bd156`.
  A separate empty Currie site, drawn through the UI. One neighbourhood park
  was repeatedly reshaped, followed by a separate basketball park to its south.

| Live browser trial | Result |
| --- | --- |
| Triangle, about 76 × 55 m | Loop and three full-size modules fitted; saved and reloaded. |
| L shape, about 76 × 55 m | Loop and four modules used the connected arms. |
| Deep angled six-point notch | Lawn and planting fitted; no forced miniature equipment. |
| Trapezoid made with individual corner drags | Full programme fitted inside the narrowed outline. |
| Five-point concave notch made with Add outline point | Programme rearranged around the notch. |
| Small 30 × 30 m triangle | Landscape layout retained the outline and full-size planting. |
| Basketball, 74 × 55 m bounding area with a slanted edge | Full rectangular court, run-off, fence, paths and seating fitted inside the outer park. |
| Shrink five-point park to 30 × 30, Undo, Redo, Undo, reload | Matching ground measurements restored with each outline; final reload retained the larger measured park. |

Additional automated cases cover U shapes, narrow strips, reversed winding,
triangular/L-shaped/trapezoidal basketball footprints, complete path corridors,
module envelopes and tree-crown clearance. These are geometry checks, not claims
of additional browser trials.

## Bugs found and fixed

1. Four-corner parks were constrained like rectangular buildings; width/depth
   calculations also assumed the first three points described the entire plot.
   Park editing now measures the entire outline and permits independent corners.
   Crossing edges and collapsed outlines get a clear local explanation before a
   save request.
2. Neighbourhood layout search assumed too much rectangular space. It now uses
   polygon area and a finite second search over both axes. Existing successful
   rectangular compositions retain priority. A planted landscape is a valid
   fallback when the loop and play spaces do not fit.
3. Tiny Float32 differences at triangle corners caused the measured-ground
   containment check to throw and remove the park. Boundary inclusion now has a
   1 mm seam tolerance, including endpoints; concave notches remain excluded.
4. Reshaping within an already measured ground grid triggered avoidable new tile
   measurements. The saved two-pass support can now be reused after validating
   the new footprint, including newly exposed areas. Ground outside that grid
   still requires measurement. Quality thresholds were not relaxed.
5. Undo restored coordinates but retained the smaller park's derived ground
   grid. Coordinate history now retains each outline's valid terrain, merges it
   with current properties and preserves optimistic revision checks.
6. Google vegetation could intrude into a measured neighbourhood park. Its own
   terrain mesh now replaces tiles inside the park while preserving the measured
   hillside. The site boundary itself can still retain surrounding terrain.
7. Basketball required its whole-plot rectangular outer loop to fit before it
   would place a court. It now searches for a contained complete court precinct
   and retains the student's irregular outer lawn.
8. Near-kerb T endpoints were not actually connected. Catalogue street endpoints
   now snap to a nearby through-street centreline when nearly perpendicular.
   Endpoint editing supports Alt for free placement. Imported reference streets
   never become proposed streets through this operation.
9. A second flat road-zone slab hid detailed street bands. Detailed catalogue
   sections now own their ground consistently, including internal streets.
10. Drawing instructions intercepted canvas clicks beneath the banner. The text
    now lets clicks through; the Finish drawing button remains interactive.

## Ground observations and remaining work

The neighbourhood park's successful measured surface ranges approximately
1101.77–1103.48 m in the provider's ellipsoidal reference. Rough Google vegetation
elsewhere on the site still prevents some new measurements from being accepted.
This is not a surveyed bare-earth model.

The basketball park initially inherited the site's retain-existing-tiles choice,
allowing vegetation to show through. The final basketball inspection uses the
existing Review ground → Apply redevelopment level control at about 1102.01 m.
This demonstrates its shape and fixed court geometry on a prepared surface. It
does not establish automatic slope-following for basketball surrounds; the rigid
playing surface and surrounding landscape need a separate ground-treatment pilot.

After reproducing the old undo bug, the neighbourhood fixture's exact earlier
saved measurement was recovered with one revision-checked API write. The saved
measurement and current footprint were required to match exactly. No new heights
were invented. The subsequent shrink/Undo/Redo/reload verification used browser
controls only and passed with the new code.

The connected-block street still stops about 13 m short of the public road. Its
internal T is verified; public-road connectivity is not claimed as completed.
Editable entrances also need an irregular-edge follow-up: edge labels and saved
edge indices must remain understandable when students add or remove corners.
The original slope/boundary/building interaction matrix has not been exhausted.

## Verification and evidence

- 161 tests passed across 14 relevant Vitest files: park outlines, neighbourhood
  layouts, sports and other structured parks, park terrain, automatic ground,
  ground persistence, shared-ground containment, street snapping/placement/surface
  ownership, reshape UI, zone writes and undo revisions.
- `npm run type-check` passed; `git diff --check` passed.
- Browser saved/reloaded actual local data. The final runtime-error count remained
  at the prior 14 entries (12 historical texture-load failures and two earlier
  triangle-boundary failures); no new entries in the final basketball/undo trial.
- No paid image, street-view or video calls. App balance stayed at 7,605 credits.

Generated screenshots and fixture JSON are outside Git at:
`C:/dev-artifacts/CityPrompt/connected-block-pilot-2026-09-08/`.
Useful views: `11-street-ground.png`, `19-triangle-detail.png`, `23-l-saved.png`,
`27-deep-notch-overhead.png`, `28-trapezoid.png`, `29-five-point-notch.png`,
`30-small-triangle.png`, `41-basketball-detail.png`, and
`42-basketball-irregular-overhead.png`.

Readbacks `shrink-before-undo.json`, `undo-restores-ground.json`,
`redo-restores-ground.json`, and `final-reloaded.json` record matching footprints
and terrain snapshots. These are local test fixtures, not catalogue assets.
Pre-existing tower thumbnails, models and publication edits are excluded from
this initiative. No catalogue assets or paid visual outputs were generated here.

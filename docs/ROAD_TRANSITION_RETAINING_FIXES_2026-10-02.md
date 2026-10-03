# Road transitions: constrained edges and automatic recovery

The subsequent [raised-road pilot](RAISED_ROAD_TERRAIN_PILOT_2026-10-02.md)
replaces the below-ground result described here with above-ground grading and
safe refusal when fixed endpoints cannot be reached. This report records the
earlier checkpoint.

Follow-up to [the first terrain pilot](NATURAL_ROAD_TRANSITION_PILOT_2026-10-02.md).
This checkpoint addresses constrained edges and tile-refinement recovery. It
remains a local development trial, excluded from the production bundle.

## Result

The constrained Calgary route now works as an explicitly selected **5 m road
with two retaining edges**. Its original 6 m width conflicts with a narrow
roadside object and remains rejected. The user chooses the narrower width in
the trial panel; the system does not silently move or resize the route.

The retained version passed geometry checks, native walking, wall collision,
original/proposal toggling, and automatic rebuilding after new Google detail
loaded. It is a terrain and circulation demonstration, not an accepted design
for a public-road intersection. Existing traffic movements and junction layout
are not resolved by this change.

## Fixes

- **Separate edge treatments.** A finite planner tries natural slopes first,
  then one retaining edge, then two. Each candidate passes the same ground and
  obstacle checks. The planner also supports different slope widths on each
  side. The original ground and its imagery remain beyond the chosen edge.
- **Retaining geometry.** Concrete faces, stone coping, and guards over fill-side
  drops cover the steep ground transition. Dense samples on both wall edges
  check for narrow objects and missing support. Retaining height is limited to
  2.5 m; source uncertainty checks are unchanged. This is conceptual geometry,
  not an engineered retaining-wall or accessibility assessment.
- **Exact terrain joins.** Triangles are split at the inner and outer retaining
  boundaries, with interpolated texture coordinates. The outer split removed
  a measured 0.55 m seam caused by coarse triangles spanning a short blend.
  The inner split removed visible terrain protrusions at the wall's foot.
- **Endpoint grading.** The measured end crossfall transitions over the available
  connection length. The old fixed 6 m transition made an edge exceed the
  physical grade limit even when the centreline passed.
- **Walking.** Swept collision checks prevent crossing a wall between frames.
  Users can slide along it, retreat, and walk around its ends. Surface changes
  update a stationary walker's height as well, preventing a removed cut from
  leaving the camera below the restored Google ground.
- **Automatic recovery.** Tile changes trigger a delayed remeasurement. There
  is one active build and at most three automatic attempts per manual request.
  Geometry/obstacle failures are not retried. Show original cancels pending
  work; changing width or leaving the page aborts obsolete builds. Late results
  are disposed. Walking pauses during measurement and capture stays blocked.

## Real-site evidence

Same projects and source DEM inputs as the first pilot; no new source elevation
offsets or fixture relocation were introduced.

| Check | Retained roadside trial | Open-field regression |
| --- | ---: | ---: |
| Road length / width | 32 m / 5 m | 36 m / 6 m |
| Ground probes | 861 | 1,305 |
| Edge treatment | Two retaining edges | Two natural slopes |
| Maximum retaining height | 2.1306 m | None |
| Maximum sampled ground change | 2.1180 m | 0.2144 m |
| Maximum checked road grade | 11.010% | 1.989% |
| Maximum road-end mesh gap | 0.0196 mm | 0.0366 mm |
| Maximum outer terrain mesh gap | 0.0026 mm | 0.0170 mm |
| Replacement tile vertices | 40,908 | 142,251 |

The tiny gap values describe rendered mesh continuity, not survey accuracy.
The roadside trial's grade is too steep to call it a step-free access route.
Local visual registration remains separate from source elevations: approximately
-1.5067 m at the roadside and -1.2904 m at the field.

Through ordinary controls, the roadside browser run:

1. Built the 6 m version and confirmed an obstacle refusal with no installed cut.
2. Selected 5 m and built the retained version.
3. Toggled original/proposal and entered Walk.
4. Recovered automatically when walking view loaded different tiles.
5. Walked from station 2 m to approximately 15.24 m.
6. Tried to cross the left wall; stopped at about 2.79 m lateral offset.
7. Continued about 5.54 m along the wall and then moved back into the road.
8. Toggled to original ground while stationary inside the cut. The camera rose
   to the restored surface, then returned to the proposal height on reactivation.
9. Returned to an oblique view and recovered automatically there as well.

No uncaught browser errors or site-zone/building writes were recorded. The field
regression again walked along the road, across the verge, and back. Its harness
now waits for automatic remeasurement before asserting final readiness; the
older immediate assertion could observe the expected temporary pending state.

The retained-road restoration test also checks original geometry identities,
material callbacks, unchanged input and saved site-zone JSON, blocked capture,
and original ground after reload. The trial is deliberately not saved as a
student street.

## Verification and review

- 51 Vitest tests passed across eight narrow files: retaining edges, transition
  planning/mesh, rehearsal cancellation/lifecycle, automatic recovery, capture,
  spatial masking, authored camera ground, and native walking navigation.
- `npm run type-check` passed.
- Vite production build passed; emitted JavaScript contains no trial panel,
  retaining-edge builder, or automatic trial controller. Existing large-chunk
  warnings remain. Public assets were not copied for this compile-only check.
- Walking and oblique screenshots were inspected. The final wall feet are
  clean; surrounding fragmented photogrammetry remains original Google context.

Browser evidence remains outside Git in
`C:/dev-artifacts/CityPrompt/road-transitions-2026-10-02/`:

- `connection-retaining-ui.json`
- `connection-retaining-walk-middle.png`, `connection-retaining-wall.png`
- `connection-retaining-top.png`, `connection-retaining-oblique.png`
- `connection-edges-result.json`: the protected-object rejection at 6 m
- `retaining-restoration-recovery.json`, `retaining-reload.json`
- `field-ui-walk.json`, `field-walk-start.png`, `field-walk-verge.png`
- `edges-ui-test.cjs`, `retaining-restoration.cjs`, `field-auto-test.cjs`

Local preview, with the existing authenticated test account:
`http://localhost:5195/projects/40e85c35-018f-43d3-afc6-32c292a7033f?terrainTrial=connection`.
Choose **5 m · compact**. The default 6 m option intentionally demonstrates the
object refusal. The first pilot report contains environment/setup commands.

## Remaining scope

Curved/crossing routes, actual public-road junction layouts, normal catalogue
placement, persistence, Undo/Redo, and export integration remain separate work.
The automatic controller is currently wired only to the development panel.
Tests of different slope widths and a single retained side are synthetic; the
real-site checks here cover two retained sides and two natural slopes.

No catalogue assets, existing student designs, source DEM files, or unrelated
workspace changes were modified. Screenshots, generated inputs, browser state,
and build output are outside Git. This checkpoint is local and is not pushed.

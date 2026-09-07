# Park follows the hillside — corrected pilot

Follow-up: [Automatic park ground alignment](AUTOMATIC_PARK_GROUND_2026-09-07.md)
implements automatic remeasurement and supersedes the manual refresh requirement
and landscape slope cap described in this historical checkpoint.

User correction: parks should match the slope, not sit on a flat table.
This supersedes the whole-park terrace approach in the previous experiment.

Branch: `codex/park-follow-slope`, based on `a30acabbd`.
Local checkout: `C:/dev/CityPrompt-building-next3`.
Trial: `http://127.0.0.1:5178/projects/f289f565-1a52-43ec-accc-38cb5ac24ea2`.
No changes to the original OneDrive checkout, no push, no paid AI renders.

## Behavior

- **Review ground → Use measured park terrain** saves an explicit reviewed
  surface for each supported neighbourhood park, then removes the whole-site
  flat backing and restores the Google hillside. Existing projects are not
  silently migrated. This is a bounded neighbourhood-park pilot.
- Park ground, lawn, walking loop, trees and details share the same saved
  triangulated height field. The existing rigid amenity-pad behavior remains;
  activity equipment is not bent or stretched down a slope.
- Source is the original Google visible mesh, with WGS84 ellipsoid heights.
  Crop the site's measured grid to the park and retain its exact grid triangles.
  Every retained sample must be finite and two measured passes must agree within
  0.08 m. No missing samples are filled, and no roof/tree removal is claimed.
- Explicitly reviewed landscape may reach a gradient of 1.0 m/m, while retaining
  the existing 0.6 m local-discontinuity check. This is a bounded plausibility
  threshold, not an accessibility standard. The original shared-ground limits
  remain unchanged. A smooth roof can still pass: the review asks the student to
  confirm that the park is on open ground.
- Park measurements override a prepared site level. A saved park never becomes
  a new flat terrace merely because its underlying catalogue geometry is flat.
  Prepared backing also excludes measured parks when changing site modes or
  undoing the boundary change.
- Move/resize invalidates the footprint-specific measurements. The old slope is
  not stretched or translated to the new location. Review ground remeasures it;
  rendering explains the required refresh rather than capturing stale geometry.
- Building terraces can keep their own level while the surrounding site remains
  terrain. Their elevation still needs review when restoring the original ground.
- Old level-to-level and flat sidewalk connectors are marked unresolved and not
  drawn through the hillside. Their saved settings are retained. The park remains
  usable and renderable; the report explains the missing graded connection.

## Live trial and verification

The existing 30 × 30 m park was reused on the same Salisbury Avenue hillside.
Applied the new control through the interface and verified API read-back.
The saved profile contains 196 samples; maximum difference between passes was
0 m in this trial. Four park corner elevations were approximately 1054.05,
1054.29, 1054.16 and 1051.67 m. The rendered outer lawn mesh contains 271
vertices with about 2.64 m of vertical variation. The loop has 574 vertices and
about 0.45 m of vertical variation; it does not cross the steepest park edge.

The entire flat site table and park terrace were removed. Inspected at 30°, 71°
and 15° camera elevations. Restoring original ground exposed the old house
height below the hillside. Using its terrace editor, changed its offset from
−0.3 to +4.5 m (1054.5 m absolute) as a separate concept pad; the park's measured
heights did not change. This is not an engineered building foundation.

Reload preserved the park profile (`reviewed-park-d8a48784`). Exact 3D capture
produced a loaded 1600 × 936 image using the saved surface. Saved the displayed
image directly for QA; the previous automation-download limitation was not
retested. No paid image/video calls were made; app balance remained 9,445.

69 tests passed across eight affected terrain, terrace, park layout, connection
and editor suites. Tests cover sloping mesh vertices, serialization, stale
footprints, missing/unstable/abrupt measurements, retained building levels and
explicit UI application with retry after failure. TypeScript and targeted lint
checks passed for this checkpoint.

Evidence is outside Git in `C:/dev-artifacts/CityPrompt/student-beta-2026-09-06/`:
`park-hillside-exact3d.png`, `park-hillside-low.png`, and
`park-hillside-house-adjusted.png`. Earlier `park-follow-hillside-close.png`
captured a transient loading screen and is not acceptance evidence.

## Next bounded work

1. Derive an entrance/sidewalk route from measured endpoints and actual terrain,
   with explicit landings and reported grades; do not reuse the former 4% claim.
2. Automatically remeasure parks after a move/resize, preserving a visible draft
   and explaining measurement quality without requiring an extra review each time.
3. Trial a larger park with playground/pavilion pads, especially transitions
   between the sloping loop and level amenities. This compact park has no such
   modules, so that live behavior is not claimed as verified here.
4. Improve edge blending and survey/DTM support. Saved visible-mesh samples can
   differ from later Google LODs, and crisp rectangular lawn edges remain visible.

The whole scene is not student-ready solely because the park now follows terrain.
The next task must preserve this landscape-first behavior.

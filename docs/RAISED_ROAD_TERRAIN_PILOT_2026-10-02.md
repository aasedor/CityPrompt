# Raised roads over Google terrain: local pilot

Follow-up to [the retaining-edge trial](ROAD_TRANSITION_RETAINING_FIXES_2026-10-02.md).
This checkpoint implements the preference for roads above the existing scene.
It remains a development pilot, excluded from production builds and the normal
student draw/save workflow.

## Result

A 32 m long, 6 m wide road passed on the Calgary field site. Its interior sits
approximately 12–23 cm above the original Google ground. The adjoining terrain
is rebuilt locally with gradual slopes and its existing imagery; no retaining
walls were needed. The road ends meet the measured original ground.

Walking along the road, across its verge, and back passed in the browser.
Original/proposal switching, tile remeasurement, restoration, and reload also
passed. No uncaught browser errors or site-zone/building writes were recorded.

The original 36 m field route now refuses: a roughly 10.5 cm rise within 0.5 m
of its far endpoint cannot be cleared while keeping that endpoint fixed and
respecting the grade bound. A finite comparison of 28, 30, 32, and 36 m routes
identified 32 m as a feasible alternative. The panel exposes **End 4 m earlier**
as an explicit selection; it does not silently relocate the route or alter its
source data.

The roadside case also refuses safely. At 6 m wide, dense measurement finds an
object or uncertain surface. At 5 m, the route cannot stay above the ground and
meet both ends at the supported grade. It leaves the original scene intact and
allows navigation back to the field trial. This replaces the previous trial's
deep retained cut for that route.

## Implementation

- Measure across the road and aggregate shoulders at intervals of at most
  0.5 m, in addition to the existing two-pass corridor checks.
- Validate those Google surface measurements against the independently aligned
  DEM. Missing ground and object-like residuals cause a refusal.
- Compute a raised profile with nominal 12 cm clearance, tapering over 4 m at
  each fixed endpoint. Account for crossfall when bounding longitudinal grades
  to 10% at sampled strips. Use a finite smoothing pass while preserving the
  measured lower bound and feasible joins.
- Check original terrain vertices between measurement rays before replacing
  the mesh. Refuse if a ground rise would pierce the road.
- Verify clearance against the actual installed road geometry. Road and
  shoulder geometry share their edge height, as does the walking surface.
- Retain cancellation, tile-change recovery, original-geometry restoration,
  obstacle checks, capture blocking, and geometry budgets from the earlier
  pilot. The source DEM, registration inputs, and saved site remain unchanged.

## Measured field result

| Check | Result |
| --- | ---: |
| Road length / width | 32 m / 6 m |
| Corridor probes | 1,189 |
| Additional road/shoulder probes | 975 |
| Minimum interior clearance | 0.1200 m |
| Maximum road raise | 0.2300 m |
| Maximum checked road grade | 5.191% |
| Edge treatment | Two natural slopes |
| Maximum sampled ground change | 0.2166 m |
| Maximum road-end mesh gap | 0.0058 mm |
| Maximum outer terrain mesh gap | 0.0204 mm |
| Replacement tile vertices | 132,216 |

The gap values measure rendered mesh continuity, not survey accuracy. This is
not an accessibility certification. Local visual registration was about
-1.2738 m; it remains separate from the source elevation data.

Walking and oblique screenshots were reviewed. The tested road has gradual
shoulders without a trench or exposed floating edge. Fragmented trees and
low-resolution imagery outside the corridor remain part of the Google context.

## Verification

- 56 Vitest tests passed across nine narrow files: raised grading, retaining
  edges, transitions, rehearsal lifecycle, trial recovery, ground capture,
  spatial masking, camera ground, and walking navigation.
- `npm run type-check` passed.
- Vite production build passed with existing large-chunk warnings. Public assets
  were not copied for this compile-only check. Scanning emitted JavaScript found
  no raised-road planner or trial-panel markers.
- Real browser runs covered the successful field route, both roadside refusals,
  native walking, automatic remeasurement, original/proposal switching, capture
  blocking, original geometry/material restoration, unchanged source and saved
  design data, and original ground after reload.

## Reproduce and evidence

Local preview with the existing authenticated test account:
`http://localhost:5195/projects/a2f3a90a-52d3-42c1-8d45-8b4ae23bd5f7?terrainTrial=field`.
Select **End 4 m earlier**, leaving the width at 6 m. The earlier pilot report
contains the environment/setup commands.

Evidence is outside Git in
`C:/dev-artifacts/CityPrompt/road-transitions-2026-10-02/`:

- `field-raised-ui-walk.json`
- `field-raised-top.png`, `field-raised-walk-start.png`,
  `field-raised-walk-middle.png`, `field-raised-walk-verge.png`
- `raised-rejection-recovery.json`, `raised-connection-rejected-ui.png`
- `raised-restoration-recovery.json`, `raised-reload.json`
- `raised-restoration-before.png`, `raised-restoration-after.png`,
  `raised-restoration-oblique.png`
- `raised-field-ui.cjs`, `raised-rejection-recovery.cjs`,
  `raised-restoration.cjs`
- `production-raised-build/`

## Remaining scope

Normal street drawing, curved/crossing routes, real junction layouts,
persistence, Undo/Redo, and export integration still need implementation and
separate verification. The tested route is an open-field corridor; this result
does not establish that every street or steep site can be fitted seamlessly.

Only source and this report are committed. Screenshots, browser state, generated
inputs, and build output remain outside Git. This checkpoint is local and has
not been pushed.

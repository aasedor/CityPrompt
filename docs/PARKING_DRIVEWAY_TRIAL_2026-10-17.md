# Parking driveway and real-development local trial — 2026-10-17

Status: implemented, locally trialled, **not published or production-ready**.
Branch `codex/drawn-parking-pilot`; extends parking checkpoint
`939c4b4ed571c0c1046fa3bef64df36fd3b606e9`. No production services,
user scenes, migrations, providers, LFS rules or binary assets were changed.

## Try the development

Local frontend `http://127.0.0.1:5184`; API port 8012. Open
`/projects/dd6893db-311c-470d-8023-b223b3d56eb6`, “Drawn parking lots · local pilot”,
using the existing local Animation browser QA account. The API was guarded
against any database other than the local `cityprompt_repairs_20261004` database
before inspecting receipts or test data.

The first disposable scene contained a Timber Community Hall facing a 48-space
asphalt lot, a concrete entrance forecourt meeting its veranda and a 6 m
driveway from the lot's clear west side aisle to the existing Google-tile road.
The hall uses the existing fixed review model: 22.55 × 26.55 × 13.10 m native
geometry on its 27 × 31 m placement plot, rotated 90 degrees. It was not rebuilt
or stretched. The lot is approximately 40 × 35 m; stalls remain 2.7 × 5.5 m,
with 6 m aisles. Parking quantity is a visualization trial, not a demand,
traffic-engineering or accessible-parking assessment.

### Follow-up: keep the connection inside the prepared boundary

At the user's request, the same local scene was retrialled with an authored
road inside its existing prepared boundary. The earlier Google-road driveway
was removed through the plan editor. The existing catalogue's **Alley — No Deep
Utilities** (`calgary_alley_draft3_v1` / `calgary_alley`), 6 m wide and approximately
75 m long, was drawn north–south inside the west edge. **Connect to nearest road**
then created and saved the short 6 m driveway automatically. The hall, 48-space
lot and entrance forecourt were retained. This internal road segment is not
connected to the public Google road; a complete external access design remains
outside this follow-up.

Results: overhead, oblique and walking-height inspections showed a continuous
road/driveway/parking surface without the raised-strip clipping seen outside
the boundary. Walking input was exercised along the entrance. Full browser
reload and reopening the lot restored 48 spaces and the linked authored road;
the editor reported a connected driveway and no unsaved edits. Local database
readback at details revision 9 confirmed the road polygon, lot, all paving and
road target lie inside the boundary, with the target on the road edge (within
floating-point tolerance). The linked road ID is
`2e136314-df36-43fd-8fae-840a32688f52`.

A free exact 3D export included the internal road, driveway, parking, forecourt
and hall. No further paid calls were made: the audit count remains three and
the local account remains at 412 tokens. No application source changed for this
follow-up; earlier automated checks were not rerun or represented as new tests.
The successful prepared-ground case does not resolve arbitrary natural-terrain
connections or the earlier AI fidelity warnings.

Additional external evidence: `prepared-boundary-overhead.png`,
`prepared-boundary-oblique.png`, `prepared-driveway-road-seam-walk.png`,
`prepared-driveway-to-hall-walk.png`, `prepared-reload-plan.png`,
`prepared-boundary-free-capture.png`, `prepared-boundary-receipt.json` and
`prepared-boundary-scene.json`. A fresh local browser tab restored normal
screenshots and controls; it is retained on the local project for the user.

### Fresh connected-development project

The user's next request was exercised from a clean project through the browser:
**Connected development · road, parking and hall**, local project
`c8d16205-ef09-4662-a1ba-66629a1fa8ad`. A new boundary, 90-degree Timber Community
Hall, 6 m authored alley, 48-space asphalt lot and concrete entrance forecourt
were drawn/placed. The earlier pilot project was preserved. The internal road
is a separate conceptual road segment, not a public-road connection.

The actual saved scene was read back from the guarded local database. Its
driveway was derived with the current app's `parkingDriveway` and `parkingRoads`
functions through Vite SSR, then independently intersected in metre coordinates:
0.60 m² overlap with the road, 9.00 m² with the lot, and 0 m² outside the boundary.
The forecourt has zero gap to the lot and to the building's approximate native
rectangular envelope; that envelope check is not semantic door metadata.
Browser walking across the driveway join showed continuous asphalt without
visible sinking; the hall entrance veranda meets the forecourt. A full reload
and reopening the plan restored 48 spaces and the connected authored road,
with Save disabled because there were no unsaved edits. No new application
code or paid render calls were required, and automated suites were not rerun.

Evidence: `C:/dev-artifacts/CityPrompt/connected-development-2026-10-17/`, including
`saved-scene.json`, `connection-check.json`, `reload-plan.png`,
`driveway-walk.png`, `parking-aisle-walk.png`, `connected-final-overhead.png`
and `connected-final-oblique.png`. The new project tab remains open locally.

Choose **Add details → Arrange details & custom paving**. Select the lot in the
plan, then **Connect to nearest road** or **Choose driveway road edge**. Use
**Expand view** if the road is outside the initial plan frame. Road outlines are
estimated guides when context is available; the editor does not display Google
imagery behind the plan. Inspect explicit targets in 3D before using a result.

## Implementation and compatibility

- Optional `parking.driveway` recipe on existing `scene_details.surfaces`:
  `{version:1, source:'manual'|'mapped'|'authored', roadPoint:[lng,lat], streetId?}`.
  Stable lot IDs and the existing details API, revision checks, permissions,
  save/reload and shared undo/redo are retained. No migration is needed.
- The road target remains fixed when moving or rotating its lot. The runtime
  derives a separate asphalt quad, 6 m wide, from the reserved side aisle. A small
  seam overlap joins it to the lot and known road. Maximum connection length is
  60 m. Unsupported changes reject without replacing the current recipe.
- Known-road clicks retain road identity. Previously manual targets within 1 m
  of a subsequently loaded edge resolve to that road and its compatibility checks.
  Missing linked roads reject; they do not silently become manual targets.
- Authored streets are supported only when their current profile has motor or
  shoulder bands and no rendered curbs. Existing sidewalks, cycle bands and intact
  curbs are not painted over. This is not a curb-cut generator.
- Candidate connections reject intersections with parking bays, buildings,
  other paving surfaces, other known roads, mapped blockers and conservative
  detail footprints. The same footprints are used by the editor and 3D layer.
  Save is disabled if later edits in that details session invalidate a connection.
- A building or detail moved in a separate map workflow can invalidate a saved
  connection later; the invalid derived driveway is omitted, and reopening the
  plan reports the blocker. There is no global map warning or cross-workflow
  transaction guard in this pilot. Two derived driveways are not independently
  checked against each other.
- Derived geometry is memoized, and ground raycasts retain the existing maximum
  of two points per frame. One valid connection adds one two-triangle asphalt
  surface. Geometry/material disposal follows existing paving conventions.
  No new frame-time, memory, student-laptop or mobile benchmark was performed
  for this extension; the earlier parking measurements must not be presented
  as measurements of this new connected scene.

## Actual verification

| Check | Result | Evidence / qualification |
| --- | --- | --- |
| Hall, parking, road and pedestrian link | Locally verified layout | Created through actual browser catalogue and plan controls; hall front faces parking; entrance forecourt reaches veranda. |
| Fixed-bay parking and 6 m road connection | Passed plan/browser checks | 48-space count shown; connected driveway visible from overhead, oblique and walking height. |
| Move / undo / redo | Passed in browser | Lot moved approximately 2 m southwest; road endpoint stayed fixed. Undo restored it; Redo repeated the move; final Undo restored original layout. |
| Delete / restore | Passed in browser | Removed lot, then Undo restored lot plus driveway. Save correctly disabled when history returned to the original arrangement. |
| Save / full reload | Passed in browser and local DB | Lot, manual driveway, rotated hall and paving restored after reload; final details revision 7 recorded externally. |
| Obstruction / missing road / road types | Passed automated tests | Bays, building/furniture obstacles, absent mapped/authored targets, curbed targets, short edges, remote targets and context-loading regression. Browser obstacle rejection was not independently exercised after the final render. |
| Automatic nearest road | Geometry tests passed; service trial unavailable | Actual local `public-road-context` request returned HTTP 503. Nearest-road button was disabled. Used the authorized explicit road-edge option instead. |
| Ground contact on prepared site | Visually checked | Parking paint and asphalt readable at pedestrian height; forecourt uses the existing prepared-ground contract. |
| Driveway over natural Google terrain | **Failed** at this site | A raised terrain strip clips the long entrance. Corner-only ground sampling can bridge or intersect intermediate ground. No grading, culvert, retaining structure or terrain-mask fix was implemented. This is a release blocker for claiming general natural-ground support. |
| Free street capture | Passed | Actual clean street preview includes hall and parking; captured before paid generation. |
| Paid render pipeline | Three calls completed | Exactly three Sunburst 2.5 calls, described below. Two aerial automatic fidelity checks rejected the AI finish and returned the source fallback. |
| Frontend tests | Passed | 37 tests across parking lot, driveway, paving/editor, detail editor, paving ground and project details persistence suites. |
| Backend tests | Passed | 55 tests in `backend/tests/test_project_details.py`, including driveway round-trip and invalid target payloads. |
| Type / lint / build | Passed with existing warnings | TypeScript exit 0; changed production TS/TSX ESLint: zero errors, two existing `GlobeSitePlannerMap` hook warnings. Production code build: 3,815 modules, 18.91 s. Existing chunk-size/static-dynamic-import warnings remain. |
| Independent review | Passed focused source review | Reviewer found missing-road, stale blockers, first-lot lookup and manual known-road issues. All addressed; final focused rerun: 19 tests passed, no remaining Critical/Important source findings. Terrain limitation retained explicitly. |
| Final browser availability | Partial | Following final downloads, the in-app tab had zero-width viewport / screenshot timeouts. Existing recorded screenshots and API receipts remain valid. Temporary viewport override was reset; local project tab retained and reopening queued in Codex. |

Build used the established recovered public directory and local env, with external
output and `copyPublicDir:false`, avoiding large duplicate assets. It verifies
code compilation, not a standalone production asset publication. The shared
pre-existing landscape/capture limitations from the original parking report
remain: no automatic vegetation exclusion, boundary-only initial capture guard,
no accessible-bay/vehicle/island distribution and no arbitrary sloped-lot design.

## Three authorized Sunburst tests

All calls used `gpt-image-2.5-sunburst` via the actual local app. Each used
196 internal app tokens; total 588. The disposable local QA balance was seeded
from 20 to 1,000 and ended at 412. No live-account balance was changed and no
provider credits or subscriptions were purchased. Local receipts do not report
actual provider USD cost; internal tokens are not a USD-cost measurement.

1. `bf1c372d-04c6-43e2-994c-9681b7e85835`: earlier two-lot/house overhead trial.
   Automatic layout/silhouette gate failed; source fallback returned. Provider
   original retained and viewed separately. Broad layout looked preserved;
   do not call it automatically verified.
2. `43c7c93f-7852-4fb5-bea4-aefae0938eba`: hall and parking street view.
   AI output displayed and saved normally, with no fallback warning observed.
   Visual review: recognizable hall silhouette/front, parking outline, white
   bays and open aisle retained; enhanced timber, asphalt and grass. This view
   predates the final widened forecourt and does not show the public-road seam.
3. `2d360b76-a688-49c0-b5e5-1650f5b5c6a5`: final connected-development oblique aerial.
   Automatic layout/silhouette gate failed; source fallback returned. Provider
   original retained, downloaded and viewed: one hall, parking, forecourt and
   road connection remain in their broad source arrangement. Fine door/window,
   line-count and terrain accuracy are not certified by this visual review.

Generated evidence is outside Git at
`C:/dev-artifacts/CityPrompt/parking-driveway-trial-2026-10-17/`:

- `real-development-saved-overhead.png`: actual final 3D app scene.
- `community-hall-street-source.png`, `render-2-street-source.png`:
  actual walking browser / clean capture.
- `render-2-street-sunburst.png`: generated street output.
- `render-3-development-provider-original.png`: generated final aerial original.
- `render-3-development-aerial-sunburst.png`: **clean source fallback**, despite
  its initial filename; not the AI original.
- `render-1-provider-original.png`: initial two-lot AI original;
  `render-1-aerial.png` is its source fallback.
- `driveway-ground-inspection.png`, `move-redo-plan.png`: actual terrain and
  edit-history evidence.
- `render-receipts.json`, `scene-details-snapshot.json`, local API logs and
  external production-code build output. No signed asset tickets or secrets
  are intentionally included in the report or receipt inventory.

## Changes and next gate

Sources: new `parkingDriveway.ts` and tests; optional driveway recipe in
`parkingLot.ts` and backend API; road/context adapters and save validation in
the existing project/detail/paving editors; renderer context plumbing and
derived asphalt in `GlobePavingSurfaces`; focused UI/API regressions.

Local rollback: return to `939c4b4ed571c0c1046fa3bef64df36fd3b606e9` in a separate
clean checkout and restart the local frontend/API. Preserve the disposable
project snapshot before testing an older API which does not accept driveway
recipes. Production remains unchanged. Before publication, fix/guard uneven
terrain, restore and verify live mapped-road lookup, resolve capture fidelity
warnings, and measure a representative connected scene on target hardware.

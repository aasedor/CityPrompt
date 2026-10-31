# Ground pathways across building and park plots

Local runtime review, 28 October 2026. Base commit `a6c682d17`; initiative
`codex/ground-pathway-overlaps-20261028`. No asset publication or deployment.

Students can draw simple paths and standalone sidewalks over building and park
plots without exclusive-plot collision errors. Building/park placement over an
existing path also retains the chosen position. Real vehicle streets and site
containment keep their previous protections. This changes ground authoring;
walls, stairs and raised equipment remain physical occluders.

## Reproduction and correction

The ordinary Concrete Neighbourhood Walk drawing rejected a route across Timber
and Stone Square with "This overlaps Timber and stone square." Regression tests
reproduced both directions of the conflict. Removing the collision alone exposed
a second cause: synthetic parking reservations and edge magnets still displaced
plots when paths were drawn first. Those reservations now exclude exact surface
paths. New, reshaped, duplicated and replaced sections pass their candidate
properties into placement validation.

Browser inspection found a third defect: native path finishes at +0.025 m were
buried by the level building contact's +0.04 m cap. The eight narrow-path programmes
now use the shared +0.08 m public-realm surface datum. Source recipes, widths,
materials and building geometry remain intact; depth testing remains enabled.
Eight geometry regressions failed at +0.025 m before this correction and pass
afterward. This is a ground finish clearance, not a new grade/access design.

## Exact variant scope

All eight variants passed automated draw, reverse placement, serialization,
boundary-placement and shallow-cap visibility checks. Exact recipe/assembly hashes
and full per-variant runtime template copies are in the external evidence package.

| Exact variant | Width | Browser evidence in this initiative |
| --- | --- | --- |
| garden_gravel_path_v1 | 1.5 m | NOT TESTED |
| concrete_neighbourhood_walk_v1 | 1.8 m | New cross-park route; initial move across plaza; save/reopen |
| brick_courtyard_path_v1 | 2 m | New route into existing bungalow plot, overlapping asphalt; bend point Undo/Redo |
| timber_garden_walk_v1 | 2 m | NOT TESTED |
| asphalt_shared_path_v1 | 3 m | Variant replacement across plaza; bungalow placed over path; endpoint extended under entrance |
| standalone_narrow_sidewalk_v1 | 1.5 m | NOT TESTED |
| standalone_neighbourhood_sidewalk_v1 | 2 m | NOT TESTED |
| standalone_urban_sidewalk_v1 | 3 m | NOT TESTED |

## Bounded browser review

Edge, mouse/keyboard, 1681 × 1234 viewport; localhost:5174. Disposable project
`8ef6fab3-ad0b-4225-89ff-46e28921e317`. Existing 640 × 680 m synthetic prepared
test boundary at 1026.0727244567706 m; this is a software test pad rather than a
surveyed vacant-land proposal. No other user project was edited.

| Case | Result | Evidence |
| --- | --- | --- |
| Original path/park rejection | REPRODUCED | Browser error text and unfinished route; before screenshot was captured after the toast disappeared |
| Path moved through existing park | PASS | Concrete move, then Asphalt variant replacement; black surface continuous across native plaza |
| Building placed over existing path | PASS | Post-War Bungalow compiled and saved at requested position, facing path |
| New path in building plot | PASS | Brick route saved within bungalow plot and across existing asphalt |
| Shallow cap visibility / occlusion | PASS | Close overhead and 30° views show path reaches steps; house and steps cover underlying path normally |
| Route endpoint edit | PASS | Asphalt endpoint extended under building; server retained the line |
| Bend point Undo/Redo | PASS | Brick controls changed 2 → 3 → 2 → 3, with saved status after redo |
| Save / reopen | PASS | Project reload retained building, square and all three paths |
| Site and motor-road exclusions | PASS (automated) | Ground-path regression retains outside-site rejection and normal vehicle-section collisions |
| Duplicate through ordinary controls | NOT TESTED | Candidate identity is propagated; live duplicate action not exercised |
| Natural/sloped terrain, every building or park surface | NOT TESTED | Prepared-level pilot only; raised decks, water and equipment can still occlude ground paths |
| Walk traversal, accessible grade, paid render/export | NOT TESTED | Drawability and source views do not certify physical access or final rendered output |

Verification: 10 focused Vitest files, **218 tests passed**; `npm run type-check`
passed. No backend or generated asset files changed.

## Evidence and delivery

Local evidence: `C:/dev-artifacts/CityPrompt/ground-pathway-overlap-20261028`.
Screenshots are original browser captures of the 3D source, not AI render
originals. No paid image/video jobs were requested; job IDs are N/A.

Private Drive review folder:
<https://drive.google.com/drive/folders/17IDytORVXP681tu4Jd-ddN3Ea_Rk-mnv>.
The local delivery manifest records individual upload IDs, byte sizes, hashes and
metadata readback. Existing sharing settings are preserved.

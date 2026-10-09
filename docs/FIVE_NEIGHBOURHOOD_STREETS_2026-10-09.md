# Five neighbourhood street concepts — local pilot

Branch: `codex/five-neighbourhood-streets`, based on park checkpoint
`ff7643df7b25764f022cf1f7012f1b765fd44e9e`. No publication or push.

All five reviewed streets are installed locally at this checkpoint.
Search **Rain-Garden Residential Street** in Streets. Its exact variant is
`student_rain_garden_residential_street_v1`: 15 m total width, 5.5 m two-way
road, paired 2.25 m planted strips and paired 2.5 m clear sidewalks. It needs
prepared level ground and a 40–300 m route. Its bounded browser pilot passed
ordinary placement, unchanged Apply, bend addition/drag, Undo/Redo and hard reload.

The rain pilot preceded the other four installations. Each exact candidate
passed independent offline review; full runtime acceptance remains separate:

| Candidate | Width | Motor lanes | Assembly triangles | Module bytes / unique set |
|---|---:|---:|---:|---:|
| Rain-Garden Residential Street / rain-v002 | 15 m | 2 | 593,772 | 1,923,412 |
| Compact One-Way Shopping Street / shopping-v001 | 15.5 m | 1 | 65,883 | 1,546,736 |
| Neighbourhood Cycle Street / cycle-v003 | 13 m | 2 | 548,624 | 1,923,412 |
| Separated Walking & Cycling Greenway / greenway-v002 | 10 m | 0 | 474,116 | 1,919,768 |
| Neighbourhood Transit-Stop Street / transit-v001 | 17 m | 2 | 322,758 | 2,123,416 |

Cycle Street is a shared low-traffic two-way carriageway with bicycle-priority
markings. The separate greenway has no motor lanes. These are original teaching
concepts, not Calgary standard sections or certified traffic/drainage designs.
No buildings or invented storefront facades are included.

The shared native street engine reconstructs surfaces and bends and repeats
rigid amenity poses once per 40 m fixture interval. It batches shared source
meshes through `THREE.InstancedMesh`; it never stretches or repeats the preview
assembly at route samples. There is no new LOD or decimation. At 300 m, submitted
geometry may approach 7.5 times the fixture inventory before clipping. Initial
browser trials are bounded 40–60 m desktop routes, not laptop/long-route claims.

## Reproduction and staging

`scripts/register_five_neighbourhood_streets.py` defaults to dry run. Pass
`--repo <checkout> --package <reviewed-package> --public-root <checkout>/frontend/public
--output <external-evidence>`; add `--install` for an authorized local install.
It checks exact independent-review locks, zero P0/P1 findings, source lane counts,
immutable bytes and additive registry bindings. It refuses conflicting cards,
module bounds, public assets or seed files and writes backups externally.

For a clean checkout, use `--repo <checkout> --from-seed --public-root <empty-directory>
--output <external-evidence>` to verify closure; add `--install` to stage the exact
modules and heroes. Seed restaging compares placements, tree wells, sections,
fixture dimensions and programme against the reviewed source recipe, then checks
all bytes before writing. Hash-bound source/evidence uses scoped `-text` Git
attributes; images and GLBs use existing LFS rules.

Authoring sources are in `tools/public_realm_assets/build_neighbourhood_streets.py`.
Use each selected package's frozen builder to reproduce its exact correction
revision. Kit/source hashes, full commands and per-module budgets are preserved
under `C:/dev-artifacts/CityPrompt/parks-streets-ten-2026-10-09/streets`.
Generated preview assemblies and render experiments stay there.

## Evidence and checks

The dry run, one-pilot install and subsequent five-package install passed. The external installer suite passed
13 regressions using temporary repository copies and the real backend candidate
contract. These cover additive preservation, mirror parity, exact lane/width
bindings, no-op reinstall, fresh staging closure, conflicting/tampered bytes,
unsafe paths, review gates and executable pose/well/fixture edits.

Rain's independent offline audit passed 1,044 full-width route rays, eight tree
root checks, 126 midpoint-link rays and all five module base datums. Its recipe,
review and native modules are in `seed/classroom-streets/neighbourhood-five`.
All five independent reports and reviewed recipes are now in that seed directory.
Fresh staging into an empty external public directory verified every locked
module and exact hero. Frontend/backend native registry and roster parity passed.

The focused frontend run passed 108 tests across thirteen files, including actual
five-binding, canonical catalogue and native street runtime/programme/instance
checks. The backend candidate contract passed 11 tests and TypeScript checking
passed. Old inventory tests were updated from 24 to 29 explicit native variants.
An additive comparison against the park checkpoint confirmed every old native
registry, roster and expansion-card record remains unchanged.

The five-binding regression exposed parent photos overriding exact native heroes.
The shared canonical catalogue now uses each native module candidate's locked
thumbnail. The transit card is classified under Transit corridors. Other existing
street bindings remain unchanged; the photographic rule also corrects older native
candidates that had the same parent-photo precedence issue.

## Bounded browser evidence so far

The parent authored roughly 60 m routes for all five through ordinary UI controls;
saved exact IDs, widths and lane counts were checked through read-only database
evidence. Rain additionally passed unchanged Apply, adding a bend and dragging it
approximately 10 m, Undo/Redo, hard reload and visible curved planting/surface
inspection without browser errors. Its walking screenshot is
`C:/dev-artifacts/CityPrompt/parks-streets-ten-2026-10-09/streets/rain-browser-walk.png`.
The earlier parent-photo observation is superseded by the exact-native hero fix.

Greenway unchanged Apply preserved its exact ID, 10 m width and zero motor lanes,
but initially removed its native geometry until another authored edit triggered
a rebuild. The shared Apply path cleared the derived native recipe without
changing authored inputs. Readiness then incorrectly accepted its surviving
compiled marker as a legacy/manual street and skipped automatic compilation.
The shared readiness check now requires a valid exact recipe for registered
native streets, while retaining the explicit fixed-fixture compatibility path.
Both a missing-recipe regression and an unchanged-authored-key rebuild/recovery
regression failed before this fix and pass afterward. Parent post-fix UI and
read-only database checks passed: all five exact native recipes persist after
Apply, including the greenway at 10 m and zero motor lanes.

Its edit panel labels it Other streets while its catalogue card is Active; record
this as a minor metadata follow-up. Its section identity and saved dimensions are
correct. Shopping, cycle and transit low-view walkthroughs were inspected by
the parent. Greenway Walk entry exposed a hidden-terrain pick mismatch: Google
tiles at 1047.78 m were compared with prepared ground at 1044.64 m. Native
pavement already used the prepared datum. A bounded Walk-only picker now
intersects prepared ground, excludes masked tile hits, and retains visible
authored meshes and off-site foreground roofs for the unchanged entry guard.
Five pick regressions and seven existing camera-ground tests pass, and
TypeScript type-check passes. Parent reloaded and entered Walk at the exact
previously rejected clear-path point: PASS. The resulting low view shows the
clear 3 m walking path, benches and separate cycle path. Evidence:
`C:/dev-artifacts/CityPrompt/parks-streets-ten-2026-10-09/streets/greenway-browser-walk-fixed.png`.
All five Walk entrances and low views have now been inspected; sustained walking
and route traversal were not tested. Exact hero URLs were verified for all five;
rain, shopping and transit cards were visually inspected and cycle/greenway image
loads confirmed. Final hard reload passed: all ten new parks/streets visible, 3D saved, all five
street native recipes present in the refreshed database, no browser console
errors, and credit balance unchanged at 7676. Parent evidence is
`C:/dev-artifacts/CityPrompt/parks-streets-ten-2026-10-09/all-ten-browser-final.png`
and `saved-trial-zones.json` in that same external directory. Exact capture/export, joins, terrain recovery and
full acceptance are not established by these bounded checks.

Original built-in imagegen prompts and adaptations are recorded in
[the photographic reference record](FIVE_NEIGHBOURHOOD_STREET_REFERENCES_2026-10-09.md).
No paid City Prompt image calls occurred. Independent offline review, browser
acceptance and human publication approval remain separate checkpoints.

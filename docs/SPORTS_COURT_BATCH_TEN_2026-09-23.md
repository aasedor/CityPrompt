# Ten sports-court park candidates

User requested ten more native 3D sports parks in the style of the pickleball
garden, and explicitly deferred browser testing. Scope is offline asset creation,
native visual review and geometry checks; no picker, seed, provider call or push.

Branch: `codex/sports-court-batch-ten`, based on the shared tree-well checkpoint
`771b904da`. All heavy output is external:
`C:/dev-artifacts/CityPrompt/sports-ten-2026-09-23/`.

## Completed batch

All ten packages are built, reimported, checked and visually reviewed in native
Blender previews. Each uses the actual exported meadow furniture, vegetation
and tree-well geometry, a fixed native sport module, clear approaches, planted
seating and a shaded terrace. Trees on the terrace have planted wells; grove
trees have soil beds. Full crowns stay outside the sports reserve.

Dimensions below are metres across x along. Playing rectangles, clear reserves
and total park sizes are separate; the park footprint must not be mistaken for
the court dimensions. Each package ID is `student_<kind>_garden_v1`.

| Kind | Playing rectangle | Whole park | Triangles | Assembly MB |
| --- | --- | --- | ---: | ---: |
| basketball | 15 x 28 | 41 x 56 | 169,510 | 4.89 |
| three_x_three | 15 x 11 | 39 x 37 | 161,844 | 4.50 |
| tennis | 10.97 x 23.77 | 38.3 x 56.6 | 171,350 | 5.02 |
| padel | 10 x 20 | 32 x 42 | 167,600 | 4.82 |
| volleyball | 9 x 18 | 35 x 44 | 160,250 | 4.44 |
| beach_volleyball | 8 x 16 | 34 x 42 | 159,414 | 4.44 |
| badminton | 6.1 x 13.4 | 30.1 x 37.4 | 160,894 | 4.47 |
| netball | 15.25 x 30.5 | 41.35 x 56.6 | 168,994 | 4.87 |
| bocce | 4 x 26.5 | 26.4 x 49 | 153,747 | 4.12 |
| petanque | two 4 x 15 lanes | 32 x 39 | 152,748 | 4.07 |

Basketball includes cantilever-supported hoops and painted keys; 3x3 has one
hoop. Tennis has singles/doubles lines and a sagging net. Padel includes real
transparent glass, upper mesh and paired side entrances. Volleyball has raised
nets, padded posts and antennae. Netball uses ring-only posts and goal circles.
Bocce has timber boards and open access leaves; petanque has two marked gravel
lanes, throwing circles and low edging outside the playing boundaries.

Exact hashes, bytes, IDs, native footprints and primary source links are in the
[source delivery ledger](SPORTS_COURT_BATCH_TEN_2026-09-23.json). Governing-body
dimensions and explicit recreational adaptations live in
`tools/public_realm_assets/court_specs.py`; park layouts are original.

Each external `<kind>/` folder contains `assembly-preview.glb`, a separate
`sport-module.glb`, reusable furniture/vegetation `modules/`, `recipe.json`,
`geometry-verification.json`, archived builder/verifier source and a pending
runtime review. `renders/` contains aerial, top, detail and court views of the
reimported GLB: **40 native images, zero image-provider calls**.

The root contains `ten-sports-gardens.png`, `ten-court-layouts.png` and
`ten-court-details.png`, plus `manifest.json` and `delivery.json`. The contact
sheets only arrange native renders; they are not AI render enhancements. Heavy
GLBs, kit output, images and rejected pilots remain external, outside Git.

## Pilot checkpoint

Dry-run preceded one basketball pilot. The first native preview revealed
coplanar playing/underlay surfaces; it is preserved under `basketball-pilot/`
as rejected visual evidence. The corrected `basketball/` asset passed native
visual review, all generic geometry checks, full-width entry rays, two measured
3.05 m rims, full tree-envelope clearance and the new coplanar-floor regression.
The corrected underlay is 12 mm below its finish. Scale-up also revealed a
separate coplanar bocce lane/gravel overlap in visual review. The rejected model
is preserved in `bocce-rejected/`; final `bocce/` lowers surrounding gravel 10 mm
and its underlay a further 12 mm. Walk checks accept less than 25 mm finish
differences, without claiming accessible construction. Both preserved failures
are now rejected by explicit mesh-height regression checks.

Checkpoint `134fc78e9` captured the verified basketball pilot before the bounded
nine-model expansion. The runner used at most two concurrent Blender processes.
Final native review covered all ten courts and the two full-batch overview
sheets; the corrected bocce finish was reviewed again before indexing delivery.

## Verification and reusable method

Three pure-Python tests pass: unique finite IDs/native reserves, source-based
run-off dimensions, and sport-specific equipment with isolated recipe copies.
All ten pass the generic and sports-specific exported-geometry verifier:

- Self-contained GLB buffers, delivered hashes, finite bounds and bounded mesh
  counts; final assemblies have 125-129 mesh instances.
- Full-width material-aware approach and court-entry rays, including sand and
  gravel entries without mislabelling them paved routes.
- Native net/rim heights where relevant, padel walls and paired open doors.
- Tree root openings and full tree-part envelopes outside the sports reserve.
- Separate floor finishes and underlays, including bocce lane/gravel separation.

Python compilation passes. Exact candidate IDs have no collisions in backend
or frontend source. No production TypeScript or backend endpoint changed.

Use `run_court_batch.py` with an explicit finite `--kinds` list and a fresh output
directory: it dry-runs all requested recipes before generating, then verifies
each delivered GLB. `review_court_batch.py` indexes the ten verified folders,
archives verification source and produces the contact sheets and hash ledger.
No existing package is overwritten by the builder.

The shared [runtime integration checklist](ARCHETYPE_RUNTIME_INTEGRATION.md)
and [review template](ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md) now capture sports
reserve dimensions, sourced equipment, full crown clearance, gates and floor
separation for future archetypes.

## Deferred integration

All browser/runtime terrain, edit/Undo/reload, access and capture gates remain
NOT TESTED by user direction. Native GLBs and source recipes are for the next
integration trial, not automatic student catalogue activation.

Next, integrate a bounded selection on a disposable vacant Currie layout at
native court size, using shared terrain/access/recovery/capture systems. Check
actual browser appearance, transparent padel walls, arrivals, terrain contact,
edits, Undo, reload and export before promoting these exact IDs. Local source
is checkpointed; nothing in this batch has been pushed or published.

These are neighbourhood ideation assets. Badminton is a calm-weather outdoor
adaptation; volleyball nets use the adult-men height; padel is not approved for
out-of-court competition play; bocce access leaves are shown open. Recipes
retain these limits. Never stretch the rigid courts or claim engineering,
competition, lighting or accessibility certification from the native checks.

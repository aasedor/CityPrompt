# Picnic and rain gardens — bounded model batch

User asked for more archetypes before browser testing. Two new original concepts
were built in `C:/dev/CityPrompt-market-plaza-model` on
`codex/park-garden-model-batch`, following the summer-market prototype. Existing
catalogue cards and saved projects were not altered. No API/image-provider calls,
runtime activation or publication occurred. Browser checks remain deferred.

| Concept | Footprint | Programme | Final package |
| --- | --- | --- | --- |
| `student_picnic_garden_v1` | 28 × 24 m | Timber pergola, four picnic tables, two benches, two lights, connected paving and open lawn | `picnic-v002` |
| `student_rain_garden_v1` | 24 × 20 m | Dry planted basin, surrounding walking loop, four benches, interpretation panel, two lights | `rain-v001` |

Packages live under
`C:/dev-artifacts/CityPrompt/public-realm-batch2-2026-09-22/`.
Exact assembly/module hashes, byte sizes, triangle counts and checks are recorded
in the companion `PARK_GARDEN_BATCH_2026-09-22.json`. Separate furniture GLBs
remain at native origin; placement recipes record metres and rotations. Geometry
is intentionally simple and texture-free. Optional trees must use the shared
stand, with full crown/roof/route clearance checks; no new tree proxy was baked.

## Verification and reusable lessons

Dry runs passed before either finite build. Final GLBs were reimported and all
four individual views inspected per concept. Offline checks pass finite geometry,
whole-envelope containment, and paved clear walking routes: 266 ray samples for
the picnic garden and 798 for the rain garden. Basin samples confirm the bottom
is 0.35 m below grade and the bank slopes; no flat surface closes the hole.
Asset hashes, self-contained buffers and absence of external textures pass.
Builder visual review passes for the model concept only. Independent review and
all runtime gates remain untested.

Picnic v001 had a missing 1.2 m paved link between the main path and pergola.
The material-aware ray check reproduces the failure; v002 adds the link and
passes. Keep both packages. Future route checks must verify the actual intended
surface, not merely any flat surface at the right height. A lawn hit is not a
pass for an advertised paved connection. Ground cells have one surface owner,
preventing coincident lawn and paving planes.

## Sol integration requirements

Read `ARCHETYPE_RUNTIME_INTEGRATION.md` and each package's pending runtime-review
template. These are **not installed executable parks**. Add exact-ID local trial
adapters, preserve fixed footprints, and do not stretch furniture or crop layouts
into smaller/irregular plots. Use the shared park surface, support measurements,
access resolver, landscape exclusion, edit freshness and capture guards.
`assembly-preview.glb` is an inspection fixture, never a rigid runtime park slab.

The rain garden needs explicit prepared-ground depression/masking integration.
Placing its negative bowl over intact Google tiles would bury the basin and is a
runtime blocker. Do not pretend the geometric basin establishes runoff capacity,
infiltration, overflow design, accessibility or engineering compliance. The
interpretation panel is a blank physical placeholder, with no invented text.

Begin trials on disposable vacant Currie layouts. Check ordinary placement,
entrance connections, move/rotate, supported plot behaviour, Undo/Redo, reload,
landscape application and exact export. Natural slopes and ground failures require
their own checks; offline level renders do not transfer acceptance.

Replay with Blender 5.2 and `--python-exit-code 1`:
`tools/market_plaza_model/build_gardens.py -- --kind picnic|rain --output <fresh-dir>`.
Run first with `--dry-run`; after building run
`tools/market_plaza_model/verify_gardens.py -- <candidate-dir>`.
Heavy assets and Python caches are external/ignored; only source and checkpoints
are committed. The sibling active-path batch is in
`C:/dev/CityPrompt-greenway-street-model`, branch `codex/active-travel-model-batch`.

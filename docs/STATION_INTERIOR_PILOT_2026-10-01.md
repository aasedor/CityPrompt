# Victorian Grand Station interior pilot

This is the first detailed-interior building in the new station / art school /
courtyard hotel proposal. Only the station is part of this checkpoint. It is a
local RLASM v6.1 architectural-clay pilot, using the library's restrained palette
and physical geometry. Remote publication and human visual activation remain
separate gates.

## What visitors can explore

The 60 × 96 m station includes an open entrance arcade, ticket booths, departure
board, café furniture, four platforms, two static passenger coaches and a tall
iron-and-glass barrel vault. Two 30-tread staircases connect the concourse to
galleries and a crossover 5.1 m above it. Each tread rises 0.17 m and is 0.32 m
deep. The clock tower and coaches are decorative and cannot be entered.

The exact catalogue identity is `historic_grand_station /
station_victorian_iron_glass`; the local picker title is **Victorian Grand
Station**. The complete model retains its authored proportions in a 64 × 100 m
plot. The three existing catalogue references lock the exterior identity.
Interior planning and unseen rear details are explicitly authored inferences.

## Walking implementation

The exported GLB embeds a version 2 walking network derived from the visible
floor and stair faces. Selecting the floor nearest the current walking height
keeps the ground-level concourse usable beneath the galleries. Height-bounded
obstacles cover walls, railings, columns and furniture. Movement is subdivided
and cannot jump between disconnected levels.

Registration waits for the detailed model and prepared ground, then uses the
actual scene transform for rotation, centering and elevation. Saved-zone changes
invalidate stale registrations. Deliberate entry starts at the front door, with
a **Return to building entrance** button available during exploration. The
existing park network retains its version 1 behavior, and buildings without the
optional network keep their existing walking behavior.

## Evidence and reproduction

Immutable candidate packages, authoring blends, source locks, reimport renders,
phone comparisons, independent reviews and browser evidence are external:

`C:/dev-artifacts/CityPrompt/station-interior-2026-10-01/`

The constructor, walking verifier and guarded local registration commands are
documented in `tools/station_interior/README.md`. Only the reviewed runtime GLB
and its compact evidence record belong in the source tree; the GLB uses Git LFS.
Earlier candidates remain preserved. Their visual findings concern façade
articulation, structural bearing and roof contacts; no rejected model is
registered as the final pilot.

The companion JSON records the final candidate, exact checks and runtime result.
The route verifier checks every declared route in both directions against the
actual exported mesh. It does not claim exhaustive coverage of every possible
movement sequence. This pilot targets a prepared level site.

## Final verification

`victorian-station-interior-clay-v007` passed independent review of all 21 renders
and three phone boards with zero unresolved P0/P1 findings. Its SHA-256 is
`fd009321f395d1d17410997c392805a0bcb5c199f22038377d8cb7e39019faa7`.
The exported model has 234,162 triangles, 14 meshes and no external textures.

- All 7,276 deterministic walking samples pass against the exported geometry.
- Normal browser keyboard controls complete both staircases and the crossover
  in both directions at a 90-degree placement. A separate walk reaches the
  gallery after project reload. Both rise by 5.1 m.
- The gallery rail blocks crossing while allowing sliding and backing away.
  Return to building entrance, Exit walk and Escape pass.
- The saved zone retains the exact variant and v007 revision. Local seed
  dry-run, additive installation and stored-object readback pass.
- 48 focused frontend tests, 38 backend clay tests, 24 compiler/workflow tests,
  TypeScript type-check, carrier-aperture audit and deterministic preflight pass.
- The fresh reload/walk records zero new application errors and no grounding
  issues. Harness mistakes and their corrected reruns are disclosed in the JSON.

Local preview: [QA - Victorian station interiors](http://localhost:5186/projects/d7a93188-9802-4d04-89d5-436207ecc56f).
Use **Walk**, then click inside the station footprint; **Top View** makes the
ground position easiest to select. The completed-catalogue flag remains false
pending human visual activation. No remote push or publication is included.

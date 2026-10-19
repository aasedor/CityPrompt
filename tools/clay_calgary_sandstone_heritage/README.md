# Calgary sandstone heritage block (RLASM v6.1 architectural clay)

Candidate G8 of wave G of 2026-10-18, one of ten catalogue types that have quality reference images but
no in-use RLASM model (`docs/showcase/MODEL_GAP_LIST_2026-10-18.md`). State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `calgary_sandstone_heritage / variant_0`
(catalogue variant id `sandstone_romanesque_revival`) from `frontend/public/archetypes/buildings/calgary-sandstone-heritage/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,406,587 | `629de326189254e0` |
| oblique | `variant_0_angle_60.jpg` | 955,727 | `2fdc718649d51b41` |
| top | `variant_0_angle_90.jpg` | 860,843 | `c73923f39bcfd440` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 46 x 46 m, 37.3 m to the highest point; 4 storeys (rusticated basement and four storeys of offices round a light court).
- storey programme: rusticated basement and four storeys of offices round a light court
- plan: 45.6 m square block round a 14 x 13 m light court (top view), corner pavilions stepping 0.8 m forward, a clock tower projecting from the middle of the east wing
- facade: rock-faced buff sandstone; paired first-floor windows; round-arched second-floor windows; third-floor arcades; coped gables with pinnacles; deep arched portal
- inferred: interiors, the light court elevations and the north and west fronts follow the visible grammar
- levels (m): 2.00, 6.00, 10.40, 15.00

## Construction and delivery (Phases C to F)

`family_sandstone.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, clock_tower, portal_arch, gables_pinnacles, east_side, roofs_court, interior, rear_north`.

Run:

```
python tools/clay_calgary_sandstone_heritage/lock_sources.py
python tools/clay_calgary_sandstone_heritage/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_calgary_sandstone_heritage/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_calgary_sandstone_heritage
```

## Version history

See `VERSIONS.md` beside this file; the independent review records live in
`evidence/<version>/independent-review.md`.

## Where the artefacts are

- `candidates/`: the delivered GLB as an ordinary Git blob under 4 MiB (Git LFS uploads are
  refused from the cloud build host).
- `evidence/<version>/`: build report, source entry, prework manifest, aperture audit, reviewer
  brief, independent review record, and sub-megabyte JPEG copies of every render and phone board.

## Not done, by design

Keeper approval, runtime integration (`docs/ARCHETYPE_RUNTIME_INTEGRATION.md`), zoning use
program, picker enrolment, catalogue splice and human activation.

## Open blockers after v002 (the v003 rework targets all three)

- P0 #1: the outer bays of the east and west faces of all four corner pavilions are filled with stone (the openings fall in the corner 2.6 m that belongs to the perpendicular wall); the builder's aperture audit fails on the same 20 openings.
- P1 #2: the projecting arched entrance porch with a balustraded balcony at the foot of the clock tower is missing; the render has a flush door.
- P1 #3: the interior view shows the openings of the opposite wall as blind recesses with solid backs.
- All ten v001 findings are resolved in the pixels.

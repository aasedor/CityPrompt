# Garden-court senior residence with copper roofs (RLASM v6.1 architectural clay)

Candidate D2 of the five-building wave of 2026-10-15, chosen to fill catalogue gaps (building types
with no clay or runtime family yet). State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `senior_living_complex / variant_0`
(catalogue variant id `senior_garden_courtyard`) from `frontend/public/archetypes/buildings/senior_living_complex/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,532,839 | `a227bca8b295ca79` |
| oblique | `variant_0_angle_60.jpg` | 907,010 | `4c73f5e4c3e4b0fd` |
| top | `variant_0_angle_90.jpg` | 869,994 | `9cac74459ec9ee05` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 74 x 64 m, 16.9 m to the highest point; 3 storeys (three residential storeys under hipped copper roofs with dormers; one-storey linking loggias; one-storey octagonal garden room).
- storey programme: three residential storeys under hipped copper roofs with dormers; one-storey linking loggias; one-storey octagonal garden room
- plan: ring of five blocks round a 39 x 27 m court (top view at 0.10 m/px): north-west pavilion 19.5 x 23.5 m, north-east pavilion 18.5 x 23 m, south-west pavilion 22 x 15 m, east wing 11.5 x 32 m, south wing 31.5 x 11.5 m; six one-storey loggia links 4 to 8 m wide; octagonal garden room 10 m across on the north link
- roofs: pavilions hipped at about 34 degrees to a flat top with rooftop units; wings hipped to a ridge; gabled dormers on every slope; loggias under hipped copper roofs; garden room under an eight-sided copper roof with a glazed cupola
- facade: red brick with stone sills, white double-hung windows on a 3.6 m bay, arched garden doors with iron balconies above on the court faces
- inferred: storey height and interiors are teaching assumptions; the outer faces of the ring are not visible in the front or oblique and repeat the visible grammar; the front and oblique disagree on block positions, so the top view governs the plan
- levels (m): 0.15, 3.45, 6.75

## Construction and delivery (Phases C to F)

`family_senior.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, loggia_arcade, dormer_roof, hub_cupola, garden_beds, pergola_terrace, interior, court_view`.

Run:

```
python tools/clay_garden_court_senior_residence/lock_sources.py
python tools/clay_garden_court_senior_residence/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_garden_court_senior_residence/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_garden_court_senior_residence
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

## Open blockers after v001 (v002 follows)

P0 three detail cameras inside solids; P1 dormers pierce the ridges; P1 garden doors not round-arched; P1 drive loop missing; P1 court_view framing; P1 tree blocks the loggia view; aperture audit FAIL behind the south-east loggia.

# Steel and ETFE stadium bowl with a truss roof ring (RLASM v6.1 architectural clay)

Candidate F4 of wave F of 2026-10-17, one of five catalogue types with no clay, runtime or
seed-library model yet, chosen to replace the Beltline mid-rise slot that duplicated an existing model. State: **stopped at v003 under the rework stopping rule (0 P0 / 6 P1; best-reviewed candidate v003)**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `outdoor_sports_stadium / variant_0`
(catalogue variant id `contemporary_steel_etfe_bowl`) from `frontend/public/archetypes/buildings/outdoor-sports-stadium/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,183,615 | `d869c63243e7959f` |
| oblique | `variant_0_angle_60.jpg` | 931,240 | `426425c0e150e48b` |
| top | `variant_0_angle_90.jpg` | 874,993 | `ceb3953968966184` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 192 x 160 m, 38.0 m to the highest point; 3 storeys (glazed concourse at grade, upper concourse behind the facade, continuous seating bowl to the back row, truss roof ring).
- storey programme: glazed concourse at grade, upper concourse behind the facade, continuous seating bowl to the back row, truss roof ring
- plan: 192 x 160 m rounded rectangle (top view); pitch 68 x 104 m with run-off, long axis north-south; inner roof opening 112 x 128 m
- facade: raking steel V-columns before the grade glazing; exposed crossing steel diagonals to the roof; diamond ETFE cushion band on the south and west, round the south-west corner
- inferred: tier count, concourse depth and the north and east facades are teaching assumptions; the north face is not visible in any source and repeats the exposed-steel grammar
- levels (m): 0.15, 7.00, 22.00, 26.00

## Construction and delivery (Phases C to F)

`family_stadium.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, v_columns, etfe_cushions, roof_truss, inner_ring, seating_bowl, interior, rear_north`.

Run:

```
python tools/clay_etfe_truss_stadium/lock_sources.py
python tools/clay_etfe_truss_stadium/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_etfe_truss_stadium/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_etfe_truss_stadium
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

## Open blockers after v003 (family stopped at v003 under the rework stopping rule)

1. P1: black slits at the mid-height crossings of the exposed diagonals and notches at the column feet. Survived two targeted fixes (stopping rule).
2. P1: the ETFE band's east end is ragged, with a black hairline between the end plate and the cushions.
3. P1: the roof structure does not read in the top view (hairline radials, no visible perimeter ring, no X-bracing in the bays).
4. P1: black holes behind the facade at the bowl corners, and the stand ends cut off.
5. P1: the stand undersides behind the facade read as planks with black slots instead of a closed underside with raker beams.
6. P1: the bowl still reads hollow from above; the pitch shows through the open perimeter truss and the clear roof panels, with no near-side seating visible.

# Steel and ETFE stadium bowl with a truss roof ring (RLASM v6.1 architectural clay)

Candidate F4 of wave F of 2026-10-17, one of five catalogue types with no clay, runtime or
seed-library model yet, chosen to replace the Beltline mid-rise slot that duplicated an existing model. State: **candidate under review**. Nothing here is keeper-approved,
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

## Open blockers after v001 (v002 targets every P0 and P1)

1. P0: the front camera clips the south-west corner where the ETFE band wraps.
2. P1: the pitch long axis runs across the bowl's long axis; side stands are about 2.5 times deeper than the ends (source: near-equal depth).
3. P1: the facade reads as stacked tiers; the source has long diagonals crossing from the concourse ring to the roof ring.
4. P1: a blank grey sheet behind the diagonals instead of concourse slabs and stepped stand undersides.
5. P1: the ETFE cushions are hard pyramids, about 5 rows at 1.6:1 (source: soft domes with thin frames, about 7 rows at 2.2:1).
6. P1: serrated top and bottom edges of the ETFE band with dark backing triangles; raw band ends.
7. P1: ETFE extent: about 60% of the west face (source about 90%) and 75-80% of the south face (source 50-65%).
8. P1: the radial roof trusses do not read under the hazy roof panels.
9. P1: open black holes at the steel joints.
10. P1: white aisle planks float on the seat rows and break through the back wall.
11. P1: no north street; streets stop abruptly; plain rectangular plaza.

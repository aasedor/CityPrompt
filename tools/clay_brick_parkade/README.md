# Campus parking structure with bronze stair towers (RLASM v6.1 architectural clay)

Candidate D4 of the five-building wave of 2026-10-15, chosen to fill catalogue gaps (building types
with no clay or runtime family yet). State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `campus_parking_structure / variant_0`
(catalogue variant id `urban_infill_brick_concrete_tower`) from `frontend/public/archetypes/buildings/campus-parking-structure/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,300,542 | `62d9d0e8d6f47353` |
| oblique | `variant_0_angle_60.jpg` | 913,132 | `76c59fdae32da33b` |
| top | `variant_0_angle_90.jpg` | 775,532 | `4ebd4cf049da9e4b` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 56 x 44 m, 23.0 m to the highest point; 5 storeys (glazed retail ground storey, four open parking decks, roof parking deck).
- storey programme: glazed retail ground storey, four open parking decks, roof parking deck
- plan: 54 x 40 m deck block (top view); 10 x 8 m bronze stair tower at the south-east corner projecting 1 m east and 1.4 m south; 12.4 x 11 m tower at the north-east corner; 4.5 x 5 m glazed stair tower at the west end of the south face; lift overrun, plant and open stair well on the roof
- facade: brick piers on an 8 m bay, open deck openings over pale precast spandrels with dark horizontal guard screens, glazed retail bays at grade, brick parapet
- towers: dark bronze frame dividing each face into strips of precast panel, glass and vertical louvres; bronze band at the first deck; louvred crown 4 m above the parapet with a patinated coping
- inferred: deck heights and interiors are teaching assumptions; the north and west faces are not visible in the front or oblique and repeat the visible grammar
- levels (m): 0.15, 4.50, 7.70, 10.90, 14.10, 17.30

## Construction and delivery (Phases C to F)

`family_parkade.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, tower_crown, retail_base, vehicle_entry, roof_deck, stair_penthouse, interior, north_lane`.

Run:

```
python tools/clay_brick_parkade/lock_sources.py
python tools/clay_brick_parkade/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_brick_parkade/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_brick_parkade
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

P1 black squares across the roof; P1 black voids at tower frame crossings; P1 bronze too pale; P1 crown patina panel missing; P1 coping corner open; P1 south-face bay variety missing; aperture audit FAIL on the hidden tower face.

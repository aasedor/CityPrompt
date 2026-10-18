# Mid-century CMU distribution warehouse with loading docks (RLASM v6.1 architectural clay)

Candidate F1 of wave F of 2026-10-17, one of five catalogue types with no clay, runtime or
seed-library model yet, chosen to replace the Beltline mid-rise slot that duplicated an existing model. State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `mid_century_distribution_warehouse / variant_0`
(catalogue variant id `cmu_dock_utilitarian`) from `frontend/public/archetypes/buildings/mid-century-distribution-warehouse/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,123,308 | `6c9e95381c52e186` |
| oblique | `variant_0_angle_60.jpg` | 777,019 | `1618e8e8aac9fab2` |
| top | `variant_0_angle_90.jpg` | 778,752 | `c8c0dc60c289633e` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 34 x 26 m, 8.6 m to the highest point; 1 storeys (single-storey warehouse on a dock-height floor with an office corner behind the entry).
- storey programme: single-storey warehouse on a dock-height floor with an office corner behind the entry
- plan: 34 x 26 m block (top view); four loading bays along the west half of the south face; entry with a canopy and a concrete landing east of them
- facade: painted beige CMU with horizontal coursing; dock doors in dark steel surrounds with black bumpers and yellow guides; aluminium entry door and windows; flat parapet with a thin pale metal coping
- inferred: the dock-height floor and interiors are teaching assumptions; the north and west faces are not visible in the front or oblique and repeat the visible grammar
- levels (m): 0.15, 1.20, 7.00

## Construction and delivery (Phases C to F)

`family_warehouse.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, dock_doors, entry_canopy, roof_units, east_windows, parapet_corner, interior, rear_north`.

Run:

```
python tools/clay_cmu_dock_warehouse/lock_sources.py
python tools/clay_cmu_dock_warehouse/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_cmu_dock_warehouse/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_cmu_dock_warehouse
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

## Open blockers after v004 (v005 targets every finding; a second review without a reduction stops the family at v003)

1. P0: the landing steps stand in front of bay 4's east jamb and guide post, blocking the bay (the dock band now runs to 68% of the face against about 62%; the landing was not moved).
2. P1: no wall between the bays and the entry; the canopy touches the bay 4 shelter (gap about 8% of the face against about 15%).
3. P1: front_corner is taken from the south-west at about 37% fill; the locked oblique is the south-east corner at about 90% fill.

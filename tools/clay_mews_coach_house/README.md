# London mews coach house (RLASM v6.1 architectural clay)

Candidate G1 of wave G of 2026-10-18, one of ten catalogue types that have quality reference images but
no in-use RLASM model (`docs/showcase/MODEL_GAP_LIST_2026-10-18.md`). State: **stopped at v006 by the stopping rule (independent review PASS_ZERO_P0_P1); v006 is the candidate, not keeper-approved**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `london_mews_house / variant_0`
(catalogue variant id `london-mews-house-original-stable`) from `frontend/public/archetypes/buildings/london-mews-house/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,447,859 | `8032e120df23417e` |
| oblique | `variant_0_angle_60.jpg` | 1,041,599 | `4514710e2328d10f` |
| top | `variant_0_angle_90.jpg` | 957,191 | `3a78fd0666cc8add` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 14 x 7 m, 9.7 m to the highest point; 2 storeys (coach house and hall on the ground floor, living rooms above; the attached neighbour the same).
- storey programme: coach house and hall on the ground floor, living rooms above; the attached neighbour the same
- plan: 8.6 x 7.4 m end house and a 5.2 m attached neighbour (top view); hipped at the corner end, party gable west
- facade: painted white brick on a black plinth; red boarded coach door with glazed transom; panelled front door with fanlight; six-over-six sashes
- inferred: interiors and the rear face are teaching assumptions; the rear repeats the visible grammar
- levels (m): 0.15, 3.05, 6.00

## Construction and delivery (Phases C to F)

`family_mews.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, coach_door, front_door, roof_chimneys, east_side, eaves_corner, interior, rear_north`.

Run:

```
python tools/clay_mews_coach_house/lock_sources.py
python tools/clay_mews_coach_house/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_mews_coach_house/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_mews_coach_house
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

## Open blockers after v006 (stopped)

- No P0 or P1 findings remain. Twelve P2 refinements are listed in evidence/v006/independent-review.md.
- This is an independent RLASM review result only; it is not keeper approval, runtime integration or catalogue enrolment.

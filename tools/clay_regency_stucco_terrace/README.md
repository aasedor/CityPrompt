# Regency stucco terrace (RLASM v6.1 architectural clay)

Candidate G6 of wave G of 2026-10-18, one of ten catalogue types that have quality reference images but
no in-use RLASM model (`docs/showcase/MODEL_GAP_LIST_2026-10-18.md`). State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `regency_stucco_terrace / variant_0`
(catalogue variant id `regency-stucco-terrace-nash`) from `frontend/public/archetypes/buildings/regency-stucco-terrace/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,326,016 | `7d8afe037a358b92` |
| oblique | `variant_0_angle_60.jpg` | 940,787 | `58577ff931e7766b` |
| top | `variant_0_angle_90.jpg` | 886,252 | `15d256fb8ee3b91b` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 40 x 34 m, 18.6 m to the highest point; 4 storeys (rusticated ground floor over a basement, first and second floors in the giant order, a mansard attic).
- storey programme: rusticated ground floor over a basement, first and second floors in the giant order, a mansard attic
- plan: 40 x 34 m block round a light court (top view), streets south, east and west, terrace houses north
- facade: cream stucco; channelled ground storey; giant engaged Corinthian order; entablature and balustrade; three paired-column porches with balconies; end pediments; iron balconettes
- inferred: interiors, the light court and the north party wall are teaching assumptions
- levels (m): 0.60, 4.40, 8.20, 11.60, 13.00

## Construction and delivery (Phases C to F)

`family_regency.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, porch_balcony, giant_order, end_pediment, mansard_dormers, east_side, interior, rear_north`.

Run:

```
python tools/clay_regency_stucco_terrace/lock_sources.py
python tools/clay_regency_stucco_terrace/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_regency_stucco_terrace/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_regency_stucco_terrace
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

## Open blockers after v003 (v004 reworks these four)

- P1 #1: front still hides the mansard, dormers and fins behind the balustrade; the camera is near ground level and too close, about 35% sky, the south face runs off the right edge (the v002 front finding, partly fixed, surviving one targeted fix).
- P1 #2: the lower mansard is about 30-40 degrees and too deep, reading as a low hipped roof; dormers become long tunnel boxes where the sources show a steep slate band with short dormers.
- P1 #3: solid black squares at every crossing of a voussoir strip and the rustication channel over every ground-floor window (new black-void defect).
- P1 #4: every Corinthian capital shows a dark gap between bell and abacus (floating abacus); the leaves are splayed stick blocks reading as a crown.

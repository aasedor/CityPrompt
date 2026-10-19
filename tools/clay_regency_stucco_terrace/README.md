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

## Open blockers after v005 (v006 reworks these two; a second non-improving review or a second failed court fix stops the family)

- P1 #1: slate and lead are the wrong way round: about three quarters of the visible roof is pale standing-seam lead with slate only as thin steep strips; the sources show broad slate on the outer and inner slopes with lead only as a narrow ribbed ridge band (source slate about 13% outside and 12% inside of block width with lead about 8%; render slate about 3% and 4% with lead about 25%).
- P1 #2: the inner court is still under-scaled: inner dormers about 1.3-1.5x street size on a steep strip about 4% of block width; the source has large lead-topped box dormers (2.5-4x street size) on broad inner slate slopes with the cream court walls and windows showing below (the v004 court finding, surviving one targeted fix).

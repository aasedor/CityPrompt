# Georgian terrace house with a slate mansard (RLASM v6.1 architectural clay)

Candidate G5 of wave G of 2026-10-18, one of ten catalogue types that have quality reference images but
no in-use RLASM model (`docs/showcase/MODEL_GAP_LIST_2026-10-18.md`). State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `georgian_terrace_house / variant_0`
(catalogue variant id `georgian-terrace-house-early`) from `frontend/public/archetypes/buildings/georgian-terrace-house/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,696,238 | `0d0bfcc66e8b46e7` |
| oblique | `variant_0_angle_60.jpg` | 1,024,378 | `84d22818aebfd4b4` |
| top | `variant_0_angle_90.jpg` | 918,332 | `292db9f5bda226c3` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 11 x 9 m, 15.9 m to the highest point; 4 storeys (three brick storeys (ground, piano nobile, second floor) and a mansard attic).
- storey programme: three brick storeys (ground, piano nobile, second floor) and a mansard attic
- plan: 11 x 9 m five-bay end-of-terrace house (top view), a side passage east, a small hipped rear wing
- facade: yellow-brown stock brick; six-over-six sashes under gauged flat arches; tall first-floor windows; stone doorcase with balconette; string course; coped parapet; slate mansard with five dormers
- inferred: interiors, the rear face and the rear wing are teaching assumptions
- levels (m): 0.30, 3.80, 7.60, 10.60

## Construction and delivery (Phases C to F)

`family_georgian.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, doorcase_balconette, mansard_dormers, chimney_stacks, east_side, roof_lead, interior, rear_north`.

Run:

```
python tools/clay_georgian_terrace_house/lock_sources.py
python tools/clay_georgian_terrace_house/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_georgian_terrace_house/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_georgian_terrace_house
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

## Open blockers after v003 (the v004 rework targets it)

- P1 #1: the rear range does not match the locked top: the east rear extension's flat roof is brick-coloured with no rooflight, reading as an open yard, where the source shows a grey roof inside a stone rim with a long hipped glazed lantern; the hipped rear wing has overhanging eaves where the source encloses its roof in a coped parapet.
- Both v002 findings are resolved in the pixels.

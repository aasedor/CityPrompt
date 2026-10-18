# Amsterdam step-gable canal house (RLASM v6.1 architectural clay)

Candidate G2 of wave G of 2026-10-18, one of ten catalogue types that have quality reference images but
no in-use RLASM model (`docs/showcase/MODEL_GAP_LIST_2026-10-18.md`). State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `amsterdam_step_gable_house / variant_0`
(catalogue variant id `step_gable_gothic`) from `frontend/public/archetypes/buildings/amsterdam-step-gable-house/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,403,581 | `1ebb96b3a30b4e30` |
| oblique | `variant_0_angle_60.jpg` | 904,563 | `a14df8d73530f0cd` |
| top | `variant_0_angle_90.jpg` | 902,196 | `e7b1f8dedf3da424` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 7 x 12 m, 19.2 m to the highest point; 5 storeys (raised ground floor over a half-basement, three upper floors, a gable attic).
- storey programme: raised ground floor over a half-basement, three upper floors, a gable attic
- plan: 6.6 x 12 m narrow-front house (top view), ridge running back from the street, alley east
- facade: dark red-brown brick; three bays of white small-paned sashes; a crow-stepped gable with one window; iron anchors; a stoop to the door
- inferred: interiors and the rear are teaching assumptions; the rear gable repeats the front grammar
- levels (m): 0.15, 3.60, 6.60, 9.60, 12.60

## Construction and delivery (Phases C to F)

`family_stepgable.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, stepped_gable, entrance_stoop, wall_anchors, east_side, roof_chimney, interior, rear_north`.

Run:

```
python tools/clay_step_gable_canal_house/lock_sources.py
python tools/clay_step_gable_canal_house/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_step_gable_canal_house/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_step_gable_canal_house
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

## Open blockers after v002 (P0+P1 fell from 14 to 8; the best so far, so v002 is the candidate)

P1 brick still reads as siding (no head joints); roof lighter than the brick; rear gable should be plain raked with the chimney at its apex; small east windows should stack over the rear tall window; north face grammar; front_corner and aerial too wide; glass_close crops the sash; short umbrella street tree

# Stepped terraced plaza (RLASM v6.1 architectural clay)

Candidate G9 of wave G of 2026-10-18, one of ten catalogue types that have quality reference images but
no in-use RLASM model (`docs/showcase/MODEL_GAP_LIST_2026-10-18.md`). State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `stepped_terraced_plaza / variant_0`
(catalogue variant id `stepped_terraced_plaza_v0`) from `frontend/public/archetypes/openspaces/stepped-terraced-plaza/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,223,732 | `ebc35d2d3930e520` |
| oblique | `variant_0_angle_60.jpg` | 809,953 | `4b491e5419a8e263` |
| top | `variant_0_angle_90.jpg` | 802,638 | `dd114f5db2320dc9` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 20 x 52 m, 15.8 m to the highest point; 0 storeys (open space: eight terraces climbing 8.8 m, flanked by one-storey houses).
- storey programme: open space: eight terraces climbing 8.8 m, flanked by one-storey houses
- plan: 20 x 52 m stair-plaza strip (top view): central stair, west and east terraces, east parapet and side stair, a lower plaza
- facade: white-rendered risers and parapets, stone-paved platforms and treads, metal handrails, terracotta pots with geraniums, white houses with blue doors
- inferred: the hillside below grade is not modelled: the terraces stand as solids on a level base; house interiors are assumptions
- levels (m): 0.00, 1.10, 2.20, 3.30, 4.40, 5.50, 6.60, 7.70, 8.80

## Construction and delivery (Phases C to F)

`family_steps.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, central_stair, seating_terraces, parapet_pots, side_stair, chapel_top, interior, rear_north`.

Run:

```
python tools/clay_stepped_terraced_plaza/lock_sources.py
python tools/clay_stepped_terraced_plaza/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_stepped_terraced_plaza/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_stepped_terraced_plaza
```

## Version history

See `VERSIONS.md` beside this file; the independent review records live in
`evidence/<version>/independent-review.md`.

## Where the artefacts are

- `candidates/`: the delivered GLB as an ordinary Git blob under 4 MiB (Git LFS uploads are
  refused from the cloud build host).
- `evidence/<version>/`: build report, source entry, prework manifest, aperture audit, reviewer
  brief, independent review record, and sub-megabyte JPEG copies of every render and phone board.

## Open-space notes

This is an open space, built with the RLASM v6.1 clay method. It was authored after reading
`docs/HIGH_QUALITY_3D_PARK_MEMORY.md`, which sets the conservatory botanical garden (`botanical_garden_v3`,
`conservatory-v013`) as the benchmark for an authored, legible plan, controlled planting and finish at
pedestrian scale. It was also authored after reading `docs/ARCHETYPE_RUNTIME_INTEGRATION.md`; the park gates
P1 to P4 there (program, terrain, remeasurement and access) are a separate runtime checkpoint and remain
NOT TESTED. The model sits on a level base. Shared terrain registration is not attempted.

## Not done, by design

Keeper approval, runtime integration (`docs/ARCHETYPE_RUNTIME_INTEGRATION.md`), zoning use
program, picker enrolment, catalogue splice and human activation.

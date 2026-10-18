# Amsterdam twin-gabled canal warehouse (RLASM v6.1 architectural clay)

Candidate G3 of wave G of 2026-10-18, one of ten catalogue types that have quality reference images but
no in-use RLASM model (`docs/showcase/MODEL_GAP_LIST_2026-10-18.md`). State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `amsterdam_canal_warehouse / variant_0`
(catalogue variant id `canal_warehouse_spice`) from `frontend/public/archetypes/buildings/amsterdam-canal-warehouse/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,458,012 | `313bbdcdc234d777` |
| oblique | `variant_0_angle_60.jpg` | 968,518 | `df416c6ee276cc79` |
| top | `variant_0_angle_90.jpg` | 899,962 | `a7565bc91fbc3175` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 20 x 16 m, 22.1 m to the highest point; 4 storeys (ground-floor cart bays and four storeys of storage lofts under the gables).
- storey programme: ground-floor cart bays and four storeys of storage lofts under the gables
- plan: 20 x 16 m corner warehouse (top view): an 8 m west and a 12 m east section, quay south, street east
- facade: red-brown brick; twin coped street gables with shoulder piers, pinnacles and hoist beams; green loading doors and shutters over arched cart doors; segmental windows; iron anchors
- inferred: interiors and the north face are teaching assumptions; the rear gables repeat the front outline without openings
- levels (m): 0.00, 4.20, 7.20, 10.20, 13.20

## Construction and delivery (Phases C to F)

`family_canalwh.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, loading_doors, arched_doors, gable_tops, east_side, roof_deck, interior, rear_north`.

Run:

```
python tools/clay_amsterdam_canal_warehouse/lock_sources.py
python tools/clay_amsterdam_canal_warehouse/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_amsterdam_canal_warehouse/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_amsterdam_canal_warehouse
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

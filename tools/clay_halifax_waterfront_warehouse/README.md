# Halifax waterfront stone warehouse (RLASM v6.1 architectural clay)

Candidate G7 of wave G of 2026-10-18, one of ten catalogue types that have quality reference images but
no in-use RLASM model (`docs/showcase/MODEL_GAP_LIST_2026-10-18.md`). State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `halifax_waterfront_warehouse / variant_0`
(catalogue variant id `warehouse_privateers_wharf`) from `frontend/public/archetypes/buildings/halifax-waterfront-warehouse/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,280,609 | `ad42ba20d9728133` |
| oblique | `variant_0_angle_60.jpg` | 918,623 | `9b2a732476ea85a9` |
| top | `variant_0_angle_90.jpg` | 818,721 | `721b8ef5aff6c9e4` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 24 x 17 m, 13.4 m to the highest point; 2 storeys (tall shop and warehouse floor, an upper loft floor).
- storey programme: tall shop and warehouse floor, an upper loft floor
- plan: 24.2 x 17 m corner block (top view), a neighbour attached west
- facade: red brick bays between rusticated granite piers; shopfront glazing and entrance; granite belt; round-arched upper windows with archivolts; verdigris copper bracketed cornice; parapet with raised blocks
- inferred: interiors, the north wall and the west party wall are teaching assumptions
- levels (m): 0.50, 5.80, 10.00, 11.15, 11.80

## Construction and delivery (Phases C to F)

`family_halifaxwh.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, arched_windows, copper_cornice, granite_piers, east_side, roof_chimneys, interior, rear_north`.

Run:

```
python tools/clay_halifax_waterfront_warehouse/lock_sources.py
python tools/clay_halifax_waterfront_warehouse/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_halifax_waterfront_warehouse/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_halifax_waterfront_warehouse
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

## Open blockers after v002 (the v003 rework targets all four)

- P1 #1: the two upper arched windows in east bay 1 overlap their archivolts, with a black triangular void between them.
- P1 #2: a black slot runs between the south-east corner pier cap and the copper frieze and cornice soffit.
- P1 #3: the east copper cornice ends open and black at the north end, and the belt course and plinth show black slots against the north wall.
- P1 #4: a black slit runs full height between the north wall and the attached west neighbour.
- The v001 P0 and all five v001 P1s are resolved in the pixels.

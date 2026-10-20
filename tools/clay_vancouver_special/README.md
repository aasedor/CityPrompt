# Vancouver Special house (RLASM v6.1 architectural clay)

Candidate I1 of wave I of 2026-10-20, one of the ten catalogue additions the user approved
(four buildings, three parks and squares, three streets); a building option from the building catalogue. State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `vancouver_special / variant_0`
(catalogue variant id `vancouver_special_v0`) from `frontend/public/archetypes/buildings/vancouver-special/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,198,511 | `d35ea463c540674c` |
| oblique | `variant_0_angle_60.jpg` | 869,740 | `052e9e31318baf4b` |
| top | `variant_0_angle_90.jpg` | 846,284 | `4eb1722a8e99aee7` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 11 x 9 m, 10.3 m to the highest point; 2 storeys (raised ground floor (suite, entry hall) and the main living floor above off the front balcony).
- storey programme: raised ground floor (suite, entry hall) and the main living floor above off the front balcony
- plan: 10.8 x 9.2 m box (top view) under one front-gable roof with 0.6 m overhangs; balcony across the east two thirds of the front
- facade: red-orange brick ground storey on the street front, white stucco above and on all other walls; bronze aluminium sliders; white door with sidelight; aluminium picket railings
- inferred: interiors, the west face and the rear face are teaching assumptions; the rear carries a small upper deck as glimpsed in the front view
- levels (m): 0.90, 3.95, 6.69

## Construction and delivery (Phases C to F)

`family_vspecial.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, balcony_rail, entry_stair, brick_base, east_side, side_entry, roof_ridge, interior`.

Run:

```
python tools/clay_vancouver_special/lock_sources.py
python tools/clay_vancouver_special/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_vancouver_special/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_vancouver_special
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

## Open blockers after v002 (x)

x

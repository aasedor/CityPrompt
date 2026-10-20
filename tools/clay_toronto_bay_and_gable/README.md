# Toronto bay-and-gable house (RLASM v6.1 architectural clay)

Candidate I2 of wave I of 2026-10-20, one of the ten catalogue additions the user approved
(four buildings, three parks and squares, three streets); a building option from the building catalogue. State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `toronto_bay_and_gable_house / variant_0`
(catalogue variant id `toronto_bay_and_gable_house_v0`) from `frontend/public/archetypes/buildings/toronto-bay-and-gable-house/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,488,963 | `d95d3c86850b2d98` |
| oblique | `variant_0_angle_60.jpg` | 1,002,820 | `de99a823f3eba0c6` |
| top | `variant_0_angle_90.jpg` | 913,422 | `8997950a8420a55a` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 8 x 11 m, 11.3 m to the highest point; 2 storeys (two full storeys over a raised stone foundation and a half-storey attic in the gables).
- storey programme: two full storeys over a raised stone foundation and a half-storey attic in the gables
- plan: 7.6 x 11.0 m detached corner house (top view); canted bay and porch on the south front, side street to the west
- facade: red brick with buff stone sill and lintel bands; two-storey canted bay under an ornate front gable; hipped porch on turned posts
- inferred: interiors, the east and rear faces and metric dimensions are teaching assumptions; the rear repeats the visible grammar
- levels (m): 0.95, 4.25, 7.25

## Construction and delivery (Phases C to F)

`family_baygable.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`bay_window, gable_bargeboard, porch_entrance, porch_frieze, west_side, west_gable, roof_chimney, foundation_fence, interior, rear_north`.

Run:

```
python tools/clay_toronto_bay_and_gable/lock_sources.py
python tools/clay_toronto_bay_and_gable/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_toronto_bay_and_gable/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_toronto_bay_and_gable
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

# Campus lecture hall under a pillowed barrel vault (RLASM v6.1 architectural clay)

Candidate F3 of wave F of 2026-10-17, one of five catalogue types with no clay, runtime or
seed-library model yet, chosen to replace the Beltline mid-rise slot that duplicated an existing model. State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `campus_lecture_hall_complex / variant_0`
(catalogue variant id `parametric_vaulted_pavilion`) from `frontend/public/archetypes/buildings/campus-lecture-hall-complex/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,067,159 | `e7f819d374a16c2b` |
| oblique | `variant_0_angle_60.jpg` | 844,366 | `de695961f8821855` |
| top | `variant_0_angle_90.jpg` | 814,790 | `79552a40b97bd731` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 36 x 34 m, 32.1 m to the highest point; 4 storeys (glazed ground-floor lobby, three storeys of lecture halls and seminar rooms in the white mass, a vaulted hall and roof terrace above).
- storey programme: glazed ground-floor lobby, three storeys of lecture halls and seminar rooms in the white mass, a vaulted hall and roof terrace above
- plan: 34 x 34 m block (top view); vault 30 m east-west by 23 m north-south over the middle of the roof; four angular masses in a pinwheel under its flanks and ends; fin screen on the west face
- facade: white composite panels with horizontal slot windows; tall vertical aluminium fins on the west face turning the south-west corner; full-height ground-floor glazing behind branching Y-columns
- inferred: storey heights and interiors are teaching assumptions; the north face is not visible in any source and repeats the visible grammar
- levels (m): 0.60, 5.40, 17.00

## Construction and delivery (Phases C to F)

`family_lecture.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, y_columns, fin_screen, vault_ribs, roof_masses, entrance_steps, interior, rear_north`.

Run:

```
python tools/clay_vaulted_lecture_hall/lock_sources.py
python tools/clay_vaulted_lecture_hall/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_vaulted_lecture_hall/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_vaulted_lecture_hall
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

## Open blockers after v001 (v002 targets every P0 and P1)

1. P0: the interior view is black.
2. P0: the four louvred roof masses are small orthogonal boxes in mirrored pairs outside the vault ends; the source has a rotated pinwheel of large angular masses rising under the arch.
3. P1: the louvred sloping faces read as staircases.
4. P1: the vault is a full semicircle with closed flat glass ends; the source arch is flatter, springs from the outer parapet edges and has open ends.
5. P1: the crown cushions are flat pads in a narrow band, not a pillowed membrane field.
6. P1: the white mass is a plain box without the faceted planes, sloping soffit and deep carved slots.
7. P1: the glazed ground floor is too squat.
8. P1: black triangular holes at the Y-column nodes.
9. P1: the fin-screen return at the south-west corner stops in mid-air.
10. P1: a gap at the east end-rib foot, and the end glazing floats above the roof deck.

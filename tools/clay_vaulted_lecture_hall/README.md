# Campus lecture hall under a pillowed barrel vault (RLASM v6.1 architectural clay)

Candidate F3 of wave F of 2026-10-17, one of five catalogue types with no clay, runtime or
seed-library model yet, chosen to replace the Beltline mid-rise slot that duplicated an existing model. State: **stopped at v003 under the rework stopping rule (0 P0 / 6 P1; v003 kept as the candidate because it has no P0)**. Nothing here is keeper-approved,
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

## Open blockers after v003 (family stopped at v003 under the rework stopping rule)

1. P1: roof masses only partly fixed: tilted about 15 degrees against about 40, two-thirds hidden under a vault spanning the full width (source about 60%), reading as thin louvre strips from above. Survived two targeted fixes.
2. P1: the front view shows no dark louvred faces under the arch, only a plain white block.
3. P1: the louvred faces are warped and clash with the vault rim and glass flank.
4. P1: the white mass is still a flat box; the facets barely read and the soffit slopes only 2-3 degrees. Survived two targeted fixes.
5. P1: a black band along the soffit line across the south face.
6. P1: front_corner and aerial look from the south-east; the source oblique looks from the south-west, and the building fills only about 30% of the frame.

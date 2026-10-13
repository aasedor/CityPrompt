# Scottish Baronial railway hotel (RLASM v6.1 architectural clay)

Candidate C1 of the five-building wave of 2026-10-13. State: **candidate under review**. Nothing
here is keeper-approved, runtime-integrated, enrolled in a catalogue or activated;
those remain separate checkpoints that need the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `chateauesque_grand_railway_hotel / variant_0`
(catalogue variant id `scottish_baronial_granite_tower`) from `frontend/public/archetypes/buildings/chateauesque-grand-railway-hotel/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,350,586 | `c3d62e25c041ad01` |
| oblique | `variant_0_angle_60.jpg` | 944,635 | `61c519072f8ecc21` |
| top | `variant_0_angle_90.jpg` | 898,813 | `cb03f9474ec9e17d` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png (LFS pointer locally; composite hero, not a locked view).

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- 58 x 50 m granite quadrangle of 14 m wings around a 30 x 22 m court (top view), streets south and west; square entrance tower 10 m wide a quarter of the way along the south face, projecting 1.6 m.
- Levels 0.15 / 4.6 / 8.4 / 12.2 / 16.0 / 19.8 m (six storeys); eaves 23.2 m; slate hipped ring roof to a 29.8 m ridge with gabled dormers and chimney stacks.
- Bays at 3.6 m of sash windows 1.4 x 2.2 m with stone surrounds in rusticated granite; string courses at each floor; crow-stepped wall gables 5.2 m wide rising through the eaves every third bay on the street faces.
- Entrance tower to 34 m with a crenellated parapet, pointed-arch porte-cochere 5 x 7 m through the south wing to the court, round tourelles at its front corners with conical caps to 39 m; round corner tourelles 4.8 m across corbelled out at 7 m with conical slate roofs to 31.5 m at the four outer corners.
- Iron fence on a low wall with gate piers, lawn strips and trees on the south and west; north and east faces repeat the grammar without wall gables; court faces plain.

## Construction and delivery (Phases C to F)

`family_hotel_baronial.py` composes the building with the repository's own `clay_core`,
`geometry` and `assemblies` modules, unchanged. `build.py` is the pilot runner with
the light rig parametrised per family. Side carriers are butted into front and rear
carriers, every opening is cut through its carrier, faces that no source shows carry
lighter window assemblies to keep the delivered GLB under the 4 MiB blob cap, every
vertex sits at or above grade, and rooms behind glazing carry low-power inspection lights.

Camera roster: the ten required baseline views plus `top` and the family contact
views `entrance_tower, porte_cochere, corner_tourelle, crow_gables, roof_court, interior, rear_court`.

Run:

```
python tools/clay_baronial_railway_hotel/lock_sources.py
python tools/clay_baronial_railway_hotel/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_baronial_railway_hotel/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_baronial_railway_hotel
```

## Version history

See `VERSIONS.md` beside this file; the independent review records live in
`evidence/<version>/independent-review.md`.

## Where the artefacts are

- `candidates/`: the delivered GLB as an ordinary Git blob under 4 MiB (Git LFS
  uploads are refused from the cloud build host; limit lifted from 1 MiB on 2026-10-12).
- `evidence/<version>/`: build report, source entry, prework manifest, aperture
  audit, reviewer brief, independent review record, and sub-megabyte JPEG copies
  of every render and phone board.
- Full-resolution PNG renders, the locked sources and the GLB were delivered to
  the user as a zip archive per version.

## Not done, by design

Keeper approval, runtime integration (`docs/ARCHETYPE_RUNTIME_INTEGRATION.md`),
zoning use program, picker enrolment, catalogue splice and human activation.

## Open blockers after v006 (Both v005 P1s resolved in the pixels (porch on a paved slab at grade, no void lines in the passage). PASS_ZERO_P0_P1; becomes the candidate. Keeper approval, runtime acceptance and publication remain separate human checkpoints.)

none (P2 only: pinhole notches at the arch crowns and haunches and at string-course ends on the east jamb, and five others in the review)

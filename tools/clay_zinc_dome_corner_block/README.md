# Haussmann corner block with zinc dome (RLASM v6.1 architectural clay)

Candidate C5 of the five-building wave of 2026-10-13. State: **candidate under review**. Nothing
here is keeper-approved, runtime-integrated, enrolled in a catalogue or activated;
those remain separate checkpoints that need the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `parisian_corner_with_dome / variant_0`
(catalogue variant id `parisian-corner-with-dome-zinc-mansard`) from `frontend/public/archetypes/buildings/parisian-corner-with-dome/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,404,367 | `abed71053e7f90d7` |
| oblique | `variant_0_angle_60.jpg` | 1,004,937 | `4c5d48f6f4bae362` |
| top | `variant_0_angle_90.jpg` | 964,784 | `7c0dff0f3930d314` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png (LFS pointer locally; composite hero, not a locked view).

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- 34 x 30 m corner block with a 12 x 10 m inner court (top view), streets south and west, a 6.5 m chamfer at the south-west corner under the dome.
- Levels 0.15 / 4.6 / 8.0 / 11.3 / 14.6 m (ground plus four storeys); cornice 18.0 m; zinc mansard set in 1.5 m over 3.6 m with arched dormers at every bay and a flat zinc top.
- Bays at 3.3 m of French windows 1.3 x 2.6 m with stone surrounds in red brick with stone string courses; individual iron balconies on the first and third storeys, continuous iron balconies on the second and fourth; stone ground and first storeys; quoins at the corners and chamfer edges.
- Stone drum 7 m across and 2.5 m high on the chamfer with three oeil-de-boeuf windows; ribbed zinc dome 7.9 m across and 4.9 m high with an oculus dormer; open lantern and gilded finial to 29.6 m.
- Cafe on the chamfer and two bays each side under a red awning projecting 2.6 m, terrace tables on the sidewalk; north and east faces plain; court faces plain.

## Construction and delivery (Phases C to F)

`family_zinc_corner.py` composes the building with the repository's own `clay_core`,
`geometry` and `assemblies` modules, unchanged. `build.py` is the pilot runner with
the light rig parametrised per family. Side carriers are butted into front and rear
carriers, every opening is cut through its carrier, faces that no source shows carry
lighter window assemblies to keep the delivered GLB under the 4 MiB blob cap, every
vertex sits at or above grade, and rooms behind glazing carry low-power inspection lights.

Camera roster: the ten required baseline views plus `top` and the family contact
views `corner_dome, cafe_awning, balcony_ironwork, mansard_dormers, roof_court, interior, rear_court`.

Run:

```
python tools/clay_zinc_dome_corner_block/lock_sources.py
python tools/clay_zinc_dome_corner_block/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_zinc_dome_corner_block/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_zinc_dome_corner_block
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

# Chamfered corner block with domed turret (RLASM v6.1 architectural clay)

Candidate M3 of the towers and mixed-use batch. State: **candidate under review**. Nothing
here is keeper-approved, runtime-integrated, enrolled in a catalogue or activated;
those remain separate checkpoints that need the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `barcelona_corner_chamfer / variant_0`
(catalogue variant id `chamfer_classic`) from `frontend/public/archetypes/buildings/barcelona-corner-chamfer/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,405,636 | `4b2c66d9cf36c949` |
| oblique | `variant_0_angle_60.jpg` | 1,000,771 | `205c7e179e1b931d` |
| top | `variant_0_angle_90.jpg` | 950,494 | `d85ec8b20ff9e9e4` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png (LFS pointer locally; composite hero, not a locked view).

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- 30 x 26 m corner block read from the top view with a 9 m chamfer at the south-west corner carrying the bowed bay; streets south and west.
- Levels 0.15 / 5.0 / 9.0 / 12.6 / 16.2 m; cornice 19.6 m; balustraded parapet to 20.9 m.
- South face six bays and west face five bays of French windows 1.3 x 2.8 m with stone surrounds; continuous iron balcony at the piano nobile and individual balconies above; arched shop openings 3.2 x 4.2 m in rusticated stone.
- Bowed stone bay projecting 1.6 m with glazing between columns over three storeys; round drum 6.4 m across and 2.4 m high; copper dome to 27.6 m; lantern to 30 m.
- Flat terracotta-tiled roof with a pyramid rooflight 5 m square, two small rooflights and three chimney stacks; north and east faces authored plain.

## Construction and delivery (Phases C to F)

`family_chamfer.py` composes the building with the repository's own `clay_core`,
`geometry` and `assemblies` modules, unchanged. `build.py` is the pilot runner with
the light rig parametrised per family. Side carriers are butted into front and rear
carriers, every opening is cut through its carrier with lined reveals, every vertex
sits at or above grade, and rooms behind glazing carry low-power inspection lights.

Camera roster: the ten required baseline views plus `top` and the family contact
views `chamfer_dome, balcony_ironwork, ground_arcade, cornice_contact, roof_terrace, interior, rear_court`.

Run:

```
python tools/clay_chamfer_corner_dome_block/lock_sources.py
python tools/clay_chamfer_corner_dome_block/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_chamfer_corner_dome_block/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_chamfer_corner_dome_block
```

## Version history

See `VERSIONS.md` beside this file; the independent review records live in
`evidence/<version>/independent-review.md`.

## Where the artefacts are

- `candidates/`: the delivered GLB as an ordinary Git blob under 1 MiB (Git LFS
  uploads are refused from the cloud build host).
- `evidence/<version>/`: build report, source entry, prework manifest, aperture
  audit, reviewer brief, independent review record, and sub-megabyte JPEG copies
  of every render and phone board.
- Full-resolution PNG renders, the locked sources and the GLB were delivered to
  the user as a zip archive per version.

## Not done, by design

Keeper approval, runtime integration (`docs/ARCHETYPE_RUNTIME_INTEGRATION.md`),
zoning use program, picker enrolment, catalogue splice and human activation.

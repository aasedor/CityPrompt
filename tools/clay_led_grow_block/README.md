# LED grow block (indoor food production) (RLASM v6.1 architectural clay)

Candidate 2 of the ten-building batch. State: **candidate under review**. Nothing
here is keeper-approved, runtime-integrated, enrolled in a catalogue or activated;
those remain separate checkpoints that need the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `vertical_farm_indoor_agriculture / variant_1`
(catalogue variant id `dark_panel_led_grow_block`) from `frontend/public/archetypes/buildings/vertical-farm-indoor-agriculture/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_1.png` | 1,127,172 | `dcc6de1743ecbe97` |
| oblique | `variant_1_angle_60.jpg` | 922,578 | `198be7669524d9cb` |
| top | `variant_1_angle_90.jpg` | 879,218 | `d30ef53d33d3f5d8` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png (LFS pointer locally; depicts variant_0, not enrolled).

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- Near-square corner block 22 x 23 m read from the 540 x 560 px top view; streets west and south.
- Concrete plinth level 4.8 m with a glazed entrance near the south-west corner and narrow lit slits; five grow levels at 4.2 m in charcoal composite panels.
- Six slot windows (0.95 x 3.25 m) per face per level with lined reveal rings; magenta-lit hydroponic racks and backboards behind them.
- Parapet roof at 25.8 m with five gabled glasshouses (north-south ridges) on the southern half, planter strips, an open-topped plant penthouse at the north-west, four raised beds at the north-east and a perimeter rail.
- Source conflict recorded: the front view shows four slot rows, the oblique five (the oblique governs); the oblique places the penthouse toward the north-east, the top view at the north-west (the top view governs plan).

## Construction and delivery (Phases C to F)

`family_grow_block.py` composes the building with the repository's own `clay_core`,
`geometry` and `assemblies` modules, unchanged. `build.py` is the pilot runner with
the light rig parametrised per family. Side carriers are butted into front and rear
carriers, every opening is cut through its carrier with lined reveals, every vertex
sits at or above grade, and rooms behind glazing carry low-power inspection lights.

Camera roster: the ten required baseline views plus `top` and the family contact
views `entrance_contact, slot_close, roof_greenhouses, penthouse_contact, parapet_corner, interior, beds`.

Run:

```
python tools/clay_led_grow_block/lock_sources.py
python tools/clay_led_grow_block/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_led_grow_block/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_led_grow_block
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

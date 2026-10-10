# Crane-way hall with rail yard (heavy industrial) (RLASM v6.1 architectural clay)

Candidate 7 of the ten-building batch. State: **candidate under review**. Nothing
here is keeper-approved, runtime-integrated, enrolled in a catalogue or activated;
those remain separate checkpoints that need the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `early_20c_megastructure_industrial / variant_1`
(catalogue variant id `heavy_craneway_hall`) from `frontend/public/archetypes/buildings/early_20c_megastructure_industrial/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_1.png` | 1,216,317 | `fb465a8b7cba59a7` |
| oblique | `variant_1_angle_60.jpg` | 893,797 | `848bf059b3312001` |
| top | `variant_1_angle_90.jpg` | 937,510 | `a2d3f265b150e7bc` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png (LFS pointer locally; depicts variant_0, not enrolled).

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- Hall 84 x 36 m: 16 m nave between two 10 m lean-to aisles; twelve 7 m bays; west gable end; yard apron all round; two sidings with a boxcar on the north.
- Section: aisle eave 10.0 m rising to 13.0 m at the nave wall; nave clerestory band 13.4 to 16.4 m; nave eaves 17.5 m; ridge 20.5 m.
- Aisle walls: lattice columns with X-bracing every bay, hooded windows between, two roll-up doors per side; nave walls: columns, glazing band, cladding above.
- West gable: three green sliding doors across the nave, open lattice frame above revealing the crane girder, clad gable triangle; east gable clad with a roll-up door.
- Eleven gabled monitors (four per aisle roof, three on the nave ridge) glazed on their long sides; overhead crane bridge with trolley and hook; external stair at the south-west corner.

## Construction and delivery (Phases C to F)

`family_craneway.py` composes the building with the repository's own `clay_core`,
`geometry` and `assemblies` modules, unchanged. `build.py` is the pilot runner with
the light rig parametrised per family. Side carriers are butted into front and rear
carriers, every opening is cut through its carrier with lined reveals, every vertex
sits at or above grade, and rooms behind glazing carry low-power inspection lights.

Camera roster: the ten required baseline views plus `top` and the family contact
views `gable_mouth, crane_interior, monitor_close, stair_contact, yard_sidings, interior, side_doors`.

Run:

```
python tools/clay_craneway_hall/lock_sources.py
python tools/clay_craneway_hall/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_craneway_hall/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_craneway_hall
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

## Open blockers after v003 (no further version permitted)

- P0: re-aim the side_doors camera on the aisle roller door (one bay further east than
  the current frame).
- P1: open the west gable full width: full-height open end bay with lattice corner
  columns and braces in the aisle shoulders, not only over the nave.
- P1: widen the lattice columns to roughly 0.35 to 0.45 of the bay module.
- P1: raise the monitor_close camera so the monitor gables are inside the frame.

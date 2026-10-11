# Cantilevered modern fire station (RLASM v6.1 architectural clay)

Candidate 3 of the ten-building batch. State: **candidate under review**. Nothing
here is keeper-approved, runtime-integrated, enrolled in a catalogue or activated;
those remain separate checkpoints that need the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `modern_fire_station / variant_2`
(catalogue variant id `fire_cantilevered_modern`) from `frontend/public/archetypes/buildings/modern_fire_station/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_2.png` | 1,073,268 | `6715ca6d2f3fde8f` |
| oblique | `variant_2_angle_60.jpg` | 786,954 | `256755fda932c4d8` |
| top | `variant_2_angle_90.jpg` | 753,818 | `3936e8d805938931` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png (LFS pointer locally; catalogue hero is the mass-timber sibling, not enrolled).

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- Rectangular box 44 x 32 m (490 x 350 px in the top view) with the glass clock tower on the east side projecting 4 m south of the front.
- Apparatus hall level 5.5 m and one upper storey; roof 10.0 m, parapet 10.6 m; tower 24 m with clock faces south and east, sign band below, red cap.
- Four 4.6 m glazed apparatus bays on the east half of the south face, recessed 2 m under the upper storey with a light strip at the soffit edge; full-height curtain wall under the cantilever to the west.
- Deep glazed loggia in the south-west of the upper storey; ribbon window on the west; dark concrete ground walls; white membrane roof.
- Forecourt: concrete apron, bollards at each bay, flagpole, memorial wall and benches to the south-west, flat shelter east of the tower, lawn panels; four appliances in the hall.

## Construction and delivery (Phases C to F)

`family_fire_station.py` composes the building with the repository's own `clay_core`,
`geometry` and `assemblies` modules, unchanged. `build.py` is the pilot runner with
the light rig parametrised per family. Side carriers are butted into front and rear
carriers, every opening is cut through its carrier with lined reveals, every vertex
sits at or above grade, and rooms behind glazing carry low-power inspection lights.

Camera roster: the ten required baseline views plus `top` and the family contact
views `apparatus_bays, soffit_corner, tower_clock, loggia_close, apron_contact, interior, rear_door`.

Run:

```
python tools/clay_cantilever_fire_station/lock_sources.py
python tools/clay_cantilever_fire_station/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_cantilever_fire_station/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_cantilever_fire_station
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

## Open blockers after v004 (v005 in progress)

- P0: a black square at the south-west corner at the top of the ground pier under the red box: the south ground carrier's end plane and the cantilever slab's end plane coincide. v005 stops the ground carrier under the slab and makes the slab one solid volume up to the upper box.
- P1: the west loggia spans only 40 percent of the face with a thick pale frame; the sources show about 80 percent with the oxblood panel as the frame and a lit edge. v005 opens it to 26 m with red reveals and lit edges.
- P1: the south hall reads as six identical headed glazed bay modules; the sources show four doors over about 59 percent of the face inside a glazed hall that runs to the corner. v005 uses four 5.2 m doors with glass-to-glass ends.
- P1: the cantilever is about 1 m deep against 2.5 to 3 m. v005 sets it to 2.8 m.
- P1: the north leg is a proud plate. v005 runs it flush over the ground wall for 43 percent of the face.
- P1: the three-window cluster on the south upper face is missing. v005 adds it at the east end and removes the east-face windows the sources do not show.
- P1: the memorial wall and flagpole stand on the apron. v005 moves them to the west plaza beside the south-west corner.
- P2 (recorded): north leg length, shelter and rooftop unit positions, wide grey corner pier (v005 goes glass-to-glass), thin seam at the north box and base junction, interior partition windows through the loggia glass, under-framed elevations, flagpole crossing facade_close, interior camera outside (v005 moves it into the hall).

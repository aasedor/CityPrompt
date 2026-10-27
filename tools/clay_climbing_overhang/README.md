# Climbing wall building: The Overhang (RLASM v6.1 architectural clay)

Candidate K2 of wave K of 2026-10-23, one of five catalogue additions the user asked for
(all four variants of the climbing wall building, and the covered passage); a building option from the building catalogue. State: **stopped at v004 by the stopping rule (v003 and v004 did not lower v002's count); v002 (0 P0 / 2 P1) is the candidate, not keeper-approved**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `climbing_wall_building / variant_1`
(catalogue variant id `climbing_overhang`) from `frontend/public/archetypes/buildings/climbing_wall_building/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_1.png` | 1,349,697 | `345d575a53846738` |
| oblique | `variant_1_angle_60.jpg` | 837,723 | `55c334948355972c` |
| top | `variant_1_angle_90.jpg` | 775,997 | `a6854c9b52d8ccd1` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 39 x 36 m, 21.0 m to the highest point; 3 storeys (three-storey pool block (lobby, gym floors) with a one-storey penthouse lounge and a four-storey east block).
- storey programme: three-storey pool block (lobby, gym floors) with a one-storey penthouse lounge and a four-storey east block
- plan: 39 m by 36 m corner building (top view) on a south plaza, a west street and an east street; the climbing shell stands on the plaza at the south front
- facade: white precast: west front of ten bays of tall recessed windows between fins and spandrels over a recessed glazed ground floor; south front: a projecting white frame box of two glass ribbons over recessed ground-floor glazing with two pairs of doors; a deep parapet band; white facade with glass ribbons under the overhang
- climbing wall: hollow open-topped shell of honey CLT in folded planes: foot on the plaza, south-west face in two facets with a fold at the parapet, triangular south face, overhanging east face, light timber rim fascia, dark and white holds, three climbers
- roof: pool deck with an infinity pool along the west edge, glass balustrades, loungers and a roof garden of planters and small trees; penthouse with a glazed pool side and an air-handling unit; east block membrane roof with skylights and plant
- streetscape: granite plaza with two raised planters of ornamental grasses and steps to the south sidewalk; west sidewalk with street trees in pits and lamp posts; west and east streets with crossings and parked cars; brick mid-rise and residential blocks around
- inferred: interiors, the north and east fronts and the hollow interior follow the visible grammar; the shell corners were triangulated from the fitted views; metric dimensions are authored teaching assumptions
- levels (m): 0.15, 5.00, 9.40, 13.80, 15.00

## Construction and delivery (Phases C to F)

`family_overhang.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`climbing_face, wall_base_contact, rim_interior, pool_deck, facade_close, architecture_close, glass_close, interior, plaza_planters, entrance`.

Run:

```
python tools/clay_climbing_overhang/lock_sources.py
python tools/clay_climbing_overhang/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_climbing_overhang/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_climbing_overhang
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

## Open blockers after v006

Candidate: `clay-climbing-overhang-clay-v002.glb`. The v006 independent review (`evidence/v006/independent-review.md`) left these P0/P1 findings open:

- **P1** (front, front_corner, right_side, aerial (vs source front, oblique)): The climbing shell narrows to a sharp point where it meets the plaza and reads as an inverted cone or horn. In both sources the shell stands on a broad base: the bottom edge of the south face sits nearly flat on the granite for a long stretch east of the doors, then rises gently to a low east corner. In the render... Likely fix: Widen the foot along the facade to about 0.3× the rim width. Drop the lower east corner of the south face to about z = 0–1.5 m so the bottom edge runs low and nearly level before the east edge rises. Make the lower...
- **P1** (front, front_corner, left_side, facade_close (vs source front, oblique)): The rhythm of the west front is wrong. I count 13 window bays (14 piers) on each upper storey; the source shows 11 bays (12 fins) between the north end and the frame-box corner, in both the front and oblique views. In the oblique render views the windows read as narrow slots between broad, deep piers, where the... Likely fix: Rebuild the west front at 11 bays over the same length. Thin the fin faces and reduce their projection so the glazing takes about 55–60 % of each bay in the oblique view. Keep the spandrel bands and the recessed...
- **P1** (top, rim_interior (vs source top)): Inside the open top, the inner walls twist into a converging funnel with a diagonal ridge, and only a thin dark sliver shows along the west inner wall. The source top shows a thick-walled rectangular box: four inner walls running parallel to the rim, white holds on the inner north and south walls, and a large dark... Likely fix: Model the inner shell as a box whose walls are near vertical or slope slightly inward, parallel to the rim. Add a flat dark crash-mat floor that can be seen from above. Re-render top and rim_interior.
- **P1** (front, front_corner, aerial (vs source front, oblique)): In both plaza planters a black lamp post rises out of the middle of the grass bed. In the source, lamp posts stand on the paving and the sidewalk, outside the planters. Likely fix: Move the lamp posts onto the paving or sidewalk at the source positions (by the SE corner and along the south sidewalk), and keep the planter beds clear.
- **P1** (front, front_corner, aerial, rim_interior, top (vs source front, oblique, top)): Both plaza planters read as bright green lawn with thin, scattered straw tufts. In the source the beds are completely filled by dense, tall, straw-coloured grass masses, with no green ground showing. Likely fix: Raise the grass density and height until the bed reads as a continuous straw mass. Change the bed ground to a dark mulch or straw tone, not green.

The candidate v002's own open findings are in `evidence/v002/independent-review.md`.

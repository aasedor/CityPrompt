# Climbing wall building: The Overhang (RLASM v6.1 architectural clay)

Candidate K2 of wave K of 2026-10-23, one of five catalogue additions the user asked for
(all four variants of the climbing wall building, and the covered passage); a building option from the building catalogue. State: **candidate under review**. Nothing here is keeper-approved,
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

## Open blockers after v001

Candidate: `clay-climbing-overhang-clay-v001.glb`. The v001 independent review (`evidence/v001/independent-review.md`) left these P0/P1 findings open:

- **P1** (front, front_corner, top, architecture_close): The shell's west side is one inclined plane from the foot (front ~780,800) to the rim corner (front ~905,150). Its west edge leans away from the pool block, leaving a wedge of white roof/penthouse visible between the shell and the parapet end (front ~805-840, 300-420; front_corner ~820-840, 420-500). In top... Likely fix: Split the west side into (a) a lower flared face from the foot to a crease at parapet height and (b) an upper panel whose west edge sits on the pool-block parapet SE corner and rises to the rim's west edge. Close the...
- **P1** (front, front_corner, climbing_face, rim_interior, wall_base_contact): Only one climber sits on the south face, and it is at the extreme SE fold. The other two hang beyond the shell's silhouette with their hands gripping nothing: against the plaza and grass strip (front ~1235-1280, 455-520; front_corner ~1175-1220, 540-590), against the east-block glazing (climbing_face ~830-910,... Likely fix: Move all three climbers onto the south-face mid-panel, in the band between about one third and half of the height. Snap the hands and feet to hold positions on that plane and verify from front, front_corner and...
- **P1** (top, rim_interior): The open top shows the inner walls and white holds, but no crash mat. The hollow floor appears only as a thin light blue-grey sliver along the inner west edge (top ~700-715, 730-840). In source top a broad dark crash mat fills the centre of the hollow floor (~590-720, 620-670) and is the most legible feature inside... Likely fix: Add a dark crash-mat slab across the hollow floor, sized and positioned so that, as in source top, it is visible from the top camera through the rim. If the lean hides it, pull the north inner wall back so the mat reads.
- **P1** (front, front_corner, top, right_side, climbing_face, wall_base_contact): The timber reads as pale greyish beige or cardboard rather than honey CLT. The lit west face measures RGB ~(183,160,127), saturation 0.31 (front ~1000-1060, 200-260), against the source's lit west face of ~(247,182,83), saturation 0.66 (source front ~600-700, 200-300) and ~(250,179,76) in the oblique. The... Likely fix: Set the CLT base colour to the source palette (about #E8B05A lit, about #8A5530 shade, hue ~35°, saturation ≥0.6), then re-check against the source on the board. Reduce the global haze so the white precast stays...
- **P1** (rear, left_side): The whole-envelope cameras clip the asset. In rear, the left frame edge cuts the east block's north facade mid-bay (x=0) and the right edge cuts the pool block's NW corner (x~1380-1440). Rear is also underexposed. In left_side, the frame cuts the west elevation at its north end (x=0, partial bay), so the full west... Likely fix: Pull rear and left_side back, or widen them, until each full elevation plus a margin fits the frame. Raise the exposure on the north elevation.

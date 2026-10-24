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

## Open blockers after v005

Candidate: `clay-climbing-overhang-clay-v002.glb`. The v005 independent review (`evidence/v005/independent-review.md`) left these P0/P1 findings open:

- **P0** (front, front_corner, aerial, right_side, top, wall_base_contact, entrance): The shell lands on a broad splayed quadrilateral that runs from the frame-box jamb right across the plaza. Measured foot-width ÷ rim-width: locked front 0.20, locked oblique 0.16; render front 0.84, render front_corner 0.63 — about 4× too wide. In `sources/oblique.jpg` the shell narrows to a compact foot about 4–5... Likely fix: Re-cut the base quadrilateral to ~8–9 m along the facade and ≤1.5 m of forward projection, keeping the rim, lean and cantilever as built; re-loft the west flare and south face to the narrower foot.
- **P0** (right_side, aerial, rear_side): The shell's east face runs all the way down to the plaza — its lower edge sits on the paving at (200–660, 1250–1320) in right_side. In `sources/front.png` the east face terminates in a sharp point about two storeys up, with the blank white facade and the open east sidewalk visible beneath it. Consequence: in... Likely fix: Lift the east face's lower edge clear of the plaza so it terminates as a free blade above the white facade; re-trim the south/east fold so the only ground contact is the south-face foot and the west flare.
- **P1** (right_side, aerial, front, front_corner): Hold coverage is confined to a narrow band either side of the south/east fold. The east face is nearly bare — about 20 scattered holds across a ~20 m plane in right_side — where `sources/front.png` shows that face densely stippled with dark holds edge to edge. The lower half of the south face and the whole west... Likely fix: Extend the hold scatter to cover the whole east face at source density (dark-dominant) and continue the south-face scatter down to the foot; leave the west flare blank as the source does.
- **P1** (top (pool west edge), front_corner, pool_deck): No infinity edge. `sources/top.jpg` shows, west to east: parapet coping → a pale overflow trough → a frameless glass weir → water. The render shows: parapet coping → a close-spaced balustrade → a dark teal vertical side face → water. The water is modelled as a solid slab standing proud of the deck with its west... Likely fix: Sink the water into a basin, add a frameless glass weir wall at the west edge and a recessed overflow trough between weir and parapet; hide the slab's side faces.
- **P1** (climbing_face, front_corner, aerial): Climbers do not engage the wall. In climbing_face the middle figure's two feet land on blank CLT at (290–330, 700–740) and (490–540, 660–700); the right figure's raised hand, horizontally outstretched arm and both feet all land on blank CLT. Limbs are flat extruded sticks lying flush on the surface, so the figures... Likely fix: Snap each hand and foot to an existing hold (or add a hold under it), give the limbs some stand-off from the plane, and re-pose the right figure into a climbing stance.

The candidate v002's own open findings are in `evidence/v002/independent-review.md`.

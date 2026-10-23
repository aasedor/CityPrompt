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

## Open blockers after v004 (stopped)

Candidate: `clay-climbing-overhang-clay-v002.glb`. The v004 independent review (`evidence/v004/independent-review.md`) left these P0/P1 findings open:

- **P0** (front, front_corner, aerial, entrance, wall_base_contact, right_side, phone-01): Envelope and contact of the shell foot. In front and front_corner the shell's west and south faces taper to a single sharp point on the plaza, about 2 m in front of the entrance doors. The shell reads as an inverted crystal balanced on its tip. right_side and entrance show that its only ground line is a short wedge... Likely fix: Re-author the shell's lowest section as a base polygon on the plaza. The long side should run E–W, parallel to and just in front of the south facade, from the east door jamb to roughly under the rim's east end. The...
- **P1** (right_side, climbing_face, (aerial)): Stray plate and stepped parapet on the white wall under the east overhang. There is a free-standing white rectangular plate, a leftover spandrel or band piece, at about third-storey level on the otherwise plain wall. Its west end runs behind or into the shell's east face. Above it, where the wall meets the shell,... Likely fix: Delete the orphan plate. Make the parapet cap over the under-overhang wall continuous with the east-block parapet (same height and projection), or end it cleanly against the shell. Re-render right_side and climbing_face.

The candidate v002's own open findings are in `evidence/v002/independent-review.md`.

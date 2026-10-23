# Halifax ferry terminal (RLASM v6.1 architectural clay)

Candidate J4 of wave J of 2026-10-22, one of five catalogue additions the user asked to be chosen
(four buildings and one street); a building option from the building catalogue. State: **stopped at v004 by the stopping rule (v003 and v004 did not lower v002's count); v002 is the candidate, not keeper-approved**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `halifax_ferry_terminal / variant_0`
(catalogue variant id `halifax_ferry_terminal_v0`) from `frontend/public/archetypes/buildings/halifax-ferry-terminal/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,425,236 | `41f206425b3b7091` |
| oblique | `variant_0_angle_60.jpg` | 943,945 | `ca06c2432494805e` |
| top | `variant_0_angle_90.jpg` | 846,583 | `02dff159b26242ed` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 20 x 41 m, 10.6 m to the highest point; 2 storeys (ground-floor concourse with ticketing and a cafe, upper-floor waiting lounge).
- storey programme: ground-floor concourse with ticketing and a cafe, upper-floor waiting lounge
- plan: 20 m by 40.8 m terminal (top view) on the corner of a south street and a wide west street; a brick heritage block adjoins on the east
- facade: south front: cantilevered glass box (three tiers of clear glazing, frosted top band, aluminium cap) between concrete end frames over a lettered canopy and glazed storefronts with two pairs of glass doors; a lower glazed west bay with a canopy wrapping the corner; west front: canopy over a glazed ground floor, glazed upper bays between three full-height concrete fins carrying cantilevered white roof boxes, solid concrete north end
- roof: flat membrane in panels inside a gravel border and a coped parapet; louvred mechanical enclosure with an air-handling unit; three skylights, hatches and vents
- streetscape: concrete sidewalks, a lawn strip with a bench on the west front, street trees in pits, a tactile strip at the entrance, crossings at the corner, the harbour and piers beyond the blocks to the north
- inferred: interiors, the north and east walls and the context blocks follow the visible grammar; metric dimensions are authored teaching assumptions; the front view draws the south front wider than the top view allows, and the top view governs the plan
- levels (m): 0.15, 4.60, 9.45

## Construction and delivery (Phases C to F)

`family_ferry.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`entrance_canopy, facade_close, glass_close, architecture_close, roof_boxes, roof_mechanical, interior, brick_neighbour, lawn_bench, rear_north`.

Run:

```
python tools/clay_halifax_ferry_terminal/lock_sources.py
python tools/clay_halifax_ferry_terminal/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_halifax_ferry_terminal/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_halifax_ferry_terminal
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

Candidate: `clay-halifax-ferry-terminal-clay-v002.glb`. The v004 independent review (`evidence/v004/independent-review.md`) left these P0/P1 findings open:

- **P1** (roof_boxes, left_side, lawn_bench, architecture_close, interior): Black patch and intersecting stair at the head of the lounge stair. (a) On the lounge floor, at the south end of the west lounge row behind fin 1, there is a hard-edged near-black triangle (roof_boxes) or band (left_side). It extends beyond the end of the bench and the pedestal. (b) Directly below it, a thin... Likely fix: The upper floor slab is a single unbroken plate (z 4.3-4.6), with no cut for the stair. A separate stair-head landing block (about 1.8 x 1.4 m) sits inside the slab. Its top and bottom faces are exactly coplanar with...

The candidate v002's own open findings are in `evidence/v002/independent-review.md`.

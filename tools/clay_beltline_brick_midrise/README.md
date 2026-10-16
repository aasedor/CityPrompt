# Calgary Beltline brick mid-rise with street retail (RLASM v6.1 architectural clay)

Candidate D1 of the five-building wave of 2026-10-15, chosen to fill catalogue gaps (building types
with no clay or runtime family yet). State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `calgary_beltline_mid_rise / variant_0`
(catalogue variant id `beltline_glass_panel`) from `frontend/public/archetypes/buildings/calgary-beltline-mid-rise/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,312,366 | `23a51bd3bc20d6da` |
| oblique | `variant_0_angle_60.jpg` | 909,573 | `1199b3cc90428ba3` |
| top | `variant_0_angle_90.jpg` | 863,281 | `6773eee31ab31db0` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 30 x 34 m, 20.7 m to the highest point; 5 storeys (retail ground storey, three brick residential storeys, set-back penthouse storey).
- storey programme: retail ground storey, three brick residential storeys, set-back penthouse storey
- plan: 30 x 32 m upper floor plate on a corner (top view at 0.054 m/px); retail storey projects 1.6 m on the south; penthouse 23.8 x 25.5 m set back 3.0 to 4.3 m behind decked terraces
- facade: two brick wings either side of a 4.5 m recessed glazed slot over the lobby; floor-2 flats onto the retail roof behind a glass guard; projecting balconies on floors 3 and 4 (two on the west wing, one wide on the east wing, two stacks on the east face, two on the north)
- ground: storefronts between brick piers under dark sign bands: brewery taproom with patio (west), lobby under a dark canopy (middle), market wrapping the south-east corner
- inferred: storey height 3.1 m and interiors are teaching assumptions; the north face is not visible in any source and repeats the visible grammar; the west face is a party condition above a lower neighbour
- levels (m): 0.15, 5.00, 8.10, 11.20, 14.30

## Construction and delivery (Phases C to F)

`family_beltline.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, storefront_patio, lobby_slot, balcony_stack, penthouse_terrace, roof_bulkhead, interior, rear_lane`.

Run:

```
python tools/clay_beltline_brick_midrise/lock_sources.py
python tools/clay_beltline_brick_midrise/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_beltline_brick_midrise/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_beltline_brick_midrise
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

## Open blockers after v001 (v002 follows)

P0 black void seam at the south-east brick corner; P1 penthouse cladding cool grey instead of warm dark bronze-taupe; P1 bulkhead two boxes with a gap, not one box with an L notch; P1 floating diagonal stair slabs behind the slot glazing; P1 street tree on the lobby axis.

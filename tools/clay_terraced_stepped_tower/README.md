# Terraced stepped residential tower (RLASM v6.1 architectural clay)

Candidate E3 of the three-tower wave of 2026-10-16, chosen to add residential towers (types
with no clay or runtime family yet). State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `terraced_stepped_building / variant_0`
(catalogue variant id `terraced_ridgeline`) from `frontend/public/archetypes/buildings/terraced_stepped_building/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,100,381 | `a851d4ed4f967f01` |
| oblique | `variant_0_angle_60.jpg` | 954,134 | `223c530887e06263` |
| top | `variant_0_angle_90.jpg` | 933,191 | `e29c87cc0d4ca38b` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 36 x 42 m, 49.5 m to the highest point; 15 storeys (fifteen storeys in the dark north block; the wing steps from fourteen storeys at the block down to two at the street in seven two-storey terraces).
- storey programme: fifteen storeys in the dark north block; the wing steps from fourteen storeys at the block down to two at the street in seven two-storey terraces
- plan: north block 36 x 14 m; stepped wing 23 m wide running 28 m south from it in seven 4 m steps; birch court 13 x 28 m west of the wing (top view at 0.075 m/px)
- facade: north block: dark charcoal brick with narrow punched windows in a staggered rhythm; wing: floor-to-ceiling glazing between cedar panels, white slab edges, slim balcony rail on each upper floor, raking concrete frame along the step edges
- inferred: storey heights and interiors are teaching assumptions; the north face is not visible in any source and repeats the visible grammar
- levels (m): 0.15, 4.15, 7.25, 10.35, 13.45, 16.55, 19.65, 22.75, 25.85, 28.95, 32.05, 35.15, 38.25, 41.35, 44.45, 47.55

## Construction and delivery (Phases C to F)

`family_terraced.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, terrace_planters, raking_frame, birch_court, solar_roof, dark_block, interior, rear_north`.

Run:

```
python tools/clay_terraced_stepped_tower/lock_sources.py
python tools/clay_terraced_stepped_tower/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_terraced_stepped_tower/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_terraced_stepped_tower
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

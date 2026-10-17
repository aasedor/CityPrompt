# Sculptural white residential superblock with a twisting tower (RLASM v6.1 architectural clay)

Candidate F5 of wave F of 2026-10-17, one of five catalogue types with no clay, runtime or
seed-library model yet, chosen to replace the Beltline mid-rise slot that duplicated an existing model. State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `residential_superblock / variant_0`
(catalogue variant id `parametric_sculptural_white`) from `frontend/public/archetypes/buildings/residential-superblock/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,192,339 | `ea93201268071dd1` |
| oblique | `variant_0_angle_60.jpg` | 905,345 | `e62b153331afdcde` |
| top | `variant_0_angle_90.jpg` | 830,180 | `309316846fdf961b` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 60 x 44 m, 53.8 m to the highest point; 14 storeys (retail ground floor; apartments on eight upper floors round the court, falling to a three-storey podium at the south-east; fourteen-storey twisting tower over the podium).
- storey programme: retail ground floor; apartments on eight upper floors round the court, falling to a three-storey podium at the south-east; fourteen-storey twisting tower over the podium
- plan: 60 x 44 m rounded perimeter block (top view) round a 32 x 18 m rounded court; tower about 15 x 11 m over the south-east podium
- facade: white spandrel bands and piers (punched windows) on the straight street faces, thinning to sinuous projecting balcony bands over ribbon glazing round the corners; recessed retail glazing behind sculpted white piers
- inferred: storey counts round the ring, interiors and the north face are teaching assumptions; the tower loop is read from the oblique and top views
- levels (m): 0.15, 4.50, 29.30, 44.80

## Construction and delivery (Phases C to F)

`family_superblock.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, balcony_bands, twisting_tower, tower_loop, courtyard, roof_terraces, interior, rear_north`.

Run:

```
python tools/clay_sculptural_superblock/lock_sources.py
python tools/clay_sculptural_superblock/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_sculptural_superblock/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_sculptural_superblock
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

## Open blockers after v001 (v002 targets every P0 and P1)

1. P0: the tower does not twist (identical discs on one axis, one straight strap, a flat half-hoop).
2. P0: the east wing drops from about 8 to 3 storeys beside the tower, opening the court and showing cut slab ends; the only dip in the sources is on the south face.
3. P1: the tower is too slender and mostly glass on a 2-3 storey podium; the source rises from a broad white south-east block.
4. P1: parts pass through each other (discs through the blade, roof band into the tower, loop foot notch).
5. P1: the straight street faces read as an egg-crate grid instead of a white wall with tall punched windows.
6. P1: pier stubs above the top spandrel and stair-stepped grid ends under the roof band.
7. P1: the west face is mostly ribbon glazing; the source shows punched windows across it.
8. P1: no glass balustrades on the curved balcony bands.
9. P1: faceted bands and parapets.
10. P1: flat roof with small hatches; no raised roof bands, linear skylights or glazed penthouse.
11. P1: radial shading streaks on the roof.
12. P1: plain rectangular retail piers instead of sculpted piers with arched openings.
13. P1: court planters tilted or over the edge; terrace slabs ending in mid-air.
14. P1: the front camera cuts off the south-west corner.

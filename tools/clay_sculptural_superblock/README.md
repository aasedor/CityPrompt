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

## Open blockers after v002 (v003 targets every P0 and P1; findings surviving again stop the family)

1. P0: the tower reads as a top-heavy goblet with two giant solid shells, bare disc plates and a closed crown; the loop is a half-hoop on a solid plate, with no open ring in the top view. Survived one targeted fix.
2. P1: the south roof line drops in a sharp kinked V to about storey 5-6; the source swoops smoothly to a podium-level cleft.
3. P1: in the dip a blank sloped wedge, a windowless cut wall, slab shards in the court and terrace slabs ending in mid-air.
4. P1: rigid rounded rectangles for plan and court; the source has a fluid perimeter, a teardrop court and a serpentine roof band.
5. P1: the tower crown overhangs the south building line.
6. P1: black voids at the retail pier heads; faceted arches; plain box piers.
7. P1: pier stubs and a loose cube above the top spandrel; stair-stepped grid ends along the dip.
8. P1: intersections (glazed bay roof into piers, slab through a blade, shell cut flat on the roof disc).
9. P1: visible faceting on the tower shell, loop, band corners and arches.

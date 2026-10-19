# Timber covered footbridge (RLASM v6.1 architectural clay)

Candidate H6 of wave H (bridges) of 2026-10-19, one of the ten bridge variants the user chose from the
street and path catalogue; a street or path option, not a building. State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `urban_pedestrian_footbridge / variant_2`
(catalogue variant id `urban_pedestrian_footbridge_v2`) from `frontend/public/archetypes/streets/urban-pedestrian-footbridge/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_2.png` | 1,357,841 | `2d5045f863146575` |
| oblique | `variant_2_angle_60.jpg` | 1,022,875 | `ed7edd0326c69bc4` |
| top | `variant_2_angle_90.jpg` | 974,510 | `bd1125b71008d2e5` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(12 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 48 x 48 m, 7.5 m to the highest point; 0 storeys (street option: a covered pedestrian footbridge over a stream; the blocks are context).
- storey programme: street option: a covered pedestrian footbridge over a stream; the blocks are context
- plan: 31 m timber deck (26 m under the roof) running east-west over a 13 m stream (top view), 4 m clear walk, piers on the lower paths
- facade: glulam portal frames with knee braces and side diagonals, vertical timber louvres, glass balustrade, timber deck on glulam edge beams, standing-seam zinc roof with deep eaves and hipped ends, round concrete piers
- inferred: the stream bed below the surface, the far ends of the paths and the blocks are context
- levels (m): 0.00, 0.60, 3.40, 3.45, 6.75

## Construction and delivery (Phases C to F)

`family_covered.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, portal_end, louvre_wall, roof_eaves, deck_inside, pier_abutment, stream_under, rear_north`.

Run:

```
python tools/clay_timber_covered_footbridge/lock_sources.py
python tools/clay_timber_covered_footbridge/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_timber_covered_footbridge/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_timber_covered_footbridge
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

## Open blockers after v002 (v003 reworks it; a second failed fix stops the family)

- P1 #1: the side walls show 10 narrow bays per side, with a louvre-only bay at each end followed by an open bay carrying the long diagonal; the sources show 6 equal bays, each end bay with full-height louvres and the one long diagonal laid over them, and 4 open knee-braced interior bays (the v001 side-bracing finding, surviving one targeted fix).

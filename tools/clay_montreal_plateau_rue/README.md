# Montreal Plateau residential rue (RLASM v6.1 architectural clay)

Candidate J5 of wave J of 2026-10-22, one of five catalogue additions the user asked to be chosen
(four buildings and one street); a street or path option, not a building. State: **stopped at v003 by the stopping rule (independent review PASS_ZERO_P0_P1); v003 is the candidate, not keeper-approved**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `montreal_plateau_residential_rue / variant_0`
(catalogue variant id `montreal_plateau_residential_rue_v0`) from `frontend/public/archetypes/streets/montreal-plateau-residential-rue/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,586,791 | `895785dc3c7d193c` |
| oblique | `variant_0_angle_60.jpg` | 975,204 | `9aabefe36ee560b2` |
| top | `variant_0_angle_90.jpg` | 934,318 | `d1dcd41d3e6963fd` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(12 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 118 x 118 m, 13.6 m to the highest point; 3 storeys (street option: two residential streets meeting at a corner; the three-storey plex rows are the street walls they are read with).
- storey programme: street option: two residential streets meeting at a corner; the three-storey plex rows are the street walls they are read with
- plan: 19.2 m building line to building line on both streets (top view): 2.6 m front yards, 3.0 m sidewalks, an 8.0 m one-way roadway with parking on the far side
- facade: grey limestone and red brick three-storey plexes with coloured door and window frames, iron gallery balconies, curling black iron exterior stairs, bracketed cornices, teal mansard caps and a slate turret spire
- inferred: the rows across both streets, the block interior, the rear walls and the plex interiors are context and teaching assumptions
- levels (m): 0.00, 0.15, 0.75, 4.00, 7.15, 10.00, 11.40

## Construction and delivery (Phases C to F)

`family_plateaurue.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, iron_stair, balcony_gallery, mansard_caps, corner_building, sidewalk_trees, roof_parapets, rear_yards`.

Run:

```
python tools/clay_montreal_plateau_rue/lock_sources.py
python tools/clay_montreal_plateau_rue/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_montreal_plateau_rue/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_montreal_plateau_rue
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

## Open blockers after v003 (x)

x

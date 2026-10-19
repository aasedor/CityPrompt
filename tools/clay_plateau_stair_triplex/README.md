# Montreal Plateau triplex with an exterior iron stair (RLASM v6.1 architectural clay)

Candidate G4 of wave G of 2026-10-18, one of ten catalogue types that have quality reference images but
no in-use RLASM model (`docs/showcase/MODEL_GAP_LIST_2026-10-18.md`). State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `montreal_plateau_triplex / variant_0`
(catalogue variant id `montreal_triplex_classic_iron`) from `frontend/public/archetypes/buildings/montreal-plateau-triplex/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,503,222 | `9aacc94e700b988b` |
| oblique | `variant_0_angle_60.jpg` | 980,168 | `a7c48e6e87f9f4f6` |
| top | `variant_0_angle_90.jpg` | 899,704 | `b8ba5cedeae63a93` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 9 x 13 m, 10.0 m to the highest point; 2 storeys (two flats over a half-basement, the upper flat reached by the exterior iron stair).
- storey programme: two flats over a half-basement, the upper flat reached by the exterior iron stair
- plan: 9 x 13 m corner plex (top view), a 3.8 m front yard, an attached neighbour west
- facade: grey limestone with quoins; recessed two-storey central porch; stone balcony and iron railing; canopy on iron lattice columns; wide timber windows; bracketed cornice with raised centre
- inferred: interiors and the rear face are teaching assumptions; the rear repeats the side wall grammar
- levels (m): 1.00, 4.47, 7.80, 8.60

## Construction and delivery (Phases C to F)

`family_triplex.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, iron_stair, balcony_canopy, cornice_parapet, east_side, roof_skylights, interior, rear_north`.

Run:

```
python tools/clay_plateau_stair_triplex/lock_sources.py
python tools/clay_plateau_stair_triplex/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_plateau_stair_triplex/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_plateau_stair_triplex
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

## Open blockers after v002 (P0+P1 fell from 7 to 6; the best so far, so v002 is the candidate)

P1 cornice return still stacked slabs with black slits; open end face on the raised cornice; raised parapet set back with a loose cartouche; cube consoles hanging to the window heads; top view framed too wide; interior porch walls short of the ceiling

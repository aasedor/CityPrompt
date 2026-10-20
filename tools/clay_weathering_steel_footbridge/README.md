# Weathering-steel truss footbridge (RLASM v6.1 architectural clay)

Candidate H7 of wave H (bridges) of 2026-10-19, one of the ten bridge variants the user chose from the
street and path catalogue; a street or path option, not a building. State: **stopped at v003 by the stopping rule (independent review PASS_ZERO_P0_P1); v003 is the candidate, not keeper-approved**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `urban_pedestrian_footbridge / variant_0`
(catalogue variant id `urban_pedestrian_footbridge_v0`) from `frontend/public/archetypes/streets/urban-pedestrian-footbridge/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,431,655 | `05d426a55b9f63d2` |
| oblique | `variant_0_angle_60.jpg` | 946,369 | `d914f7e6fcafd8c8` |
| top | `variant_0_angle_90.jpg` | 927,790 | `182aba8a25be70fb` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(12 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 56 x 38 m, 14.8 m to the highest point; 0 storeys (street option: a two-span truss footbridge over a city street; the blocks are context).
- storey programme: street option: a two-span truss footbridge over a city street; the blocks are context
- plan: two straight Warren-truss spans of about 33 and 35 m meeting at a bend (a V in plan, apex north, top view); the east span crosses a 28 m street with sidewalks
- facade: rust-orange Cor-Ten Warren trusses with bold diagonals, top chords with cross ties and bracing, perforated rust-brown deck, grey cable-mesh infill and handrail, brick stair towers, steel apex columns
- inferred: the tower interiors, the far streets and the blocks are context
- levels (m): 0.00, 7.00, 10.40

## Construction and delivery (Phases C to F)

`family_corten.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, truss_node, mesh_infill, deck_walk, landing_stair, road_under, top_chord, rear_north`.

Run:

```
python tools/clay_weathering_steel_footbridge/lock_sources.py
python tools/clay_weathering_steel_footbridge/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_weathering_steel_footbridge/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_weathering_steel_footbridge
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

## Open blockers after v003 (stopped)

- No P0 or P1 findings remain. Twelve P2 refinements are listed in evidence/v003/independent-review.md.
- This is an independent RLASM review result only; it is not keeper approval, runtime integration or catalogue enrolment.

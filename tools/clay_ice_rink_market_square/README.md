# Outdoor ice rink in a market square (RLASM v6.1 architectural clay)

Candidate G10 of wave G of 2026-10-18, one of ten catalogue types that have quality reference images but
no in-use RLASM model (`docs/showcase/MODEL_GAP_LIST_2026-10-18.md`). State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `outdoor_ice_rink / variant_0`
(catalogue variant id `outdoor_ice_rink_v0`) from `frontend/public/archetypes/openspaces/outdoor-ice-rink/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,338,889 | `9e5324878de2acef` |
| oblique | `variant_0_angle_60.jpg` | 1,024,487 | `851b6b96ca92b4f9` |
| top | `variant_0_angle_90.jpg` | 950,215 | `5bf50ae904d4c38b` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 34 x 47 m, 15.5 m to the highest point; 0 storeys (open space: an ice rink with a tree island, a timber deck, twenty market chalets).
- storey programme: open space: an ice rink with a tree island, a timber deck, twenty market chalets
- plan: 22 x 34 m rounded rink (top view) on a 26 x 39 m deck, chalets four by six round it, in a cobbled square
- facade: white dasher boards with glass panels, dark timber chalets with snowy pitched roofs, garlands and counters
- inferred: the town fronts are simplified context; chalet interiors are assumptions
- levels (m): 0.00, 0.12, 0.16

## Construction and delivery (Phases C to F)

`family_rink.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, christmas_tree, market_chalets, dasher_boards, ice_surface, square_aerial, interior, rear_north`.

Run:

```
python tools/clay_ice_rink_market_square/lock_sources.py
python tools/clay_ice_rink_market_square/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_ice_rink_market_square/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_ice_rink_market_square
```

## Version history

See `VERSIONS.md` beside this file; the independent review records live in
`evidence/<version>/independent-review.md`.

## Where the artefacts are

- `candidates/`: the delivered GLB as an ordinary Git blob under 4 MiB (Git LFS uploads are
  refused from the cloud build host).
- `evidence/<version>/`: build report, source entry, prework manifest, aperture audit, reviewer
  brief, independent review record, and sub-megabyte JPEG copies of every render and phone board.

## Open-space notes

This is an open space, built with the RLASM v6.1 clay method. It was authored after reading
`docs/HIGH_QUALITY_3D_PARK_MEMORY.md`, which sets the conservatory botanical garden (`botanical_garden_v3`,
`conservatory-v013`) as the benchmark for an authored, legible plan, controlled planting and finish at
pedestrian scale. It was also authored after reading `docs/ARCHETYPE_RUNTIME_INTEGRATION.md`; the park gates
P1 to P4 there (program, terrain, remeasurement and access) are a separate runtime checkpoint and remain
NOT TESTED. The model sits on a level base. Shared terrain registration is not attempted.

## Not done, by design

Keeper approval, runtime integration (`docs/ARCHETYPE_RUNTIME_INTEGRATION.md`), zoning use
program, picker enrolment, catalogue splice and human activation.

## Open blockers after v002 (v003 reworks these four)

- P1 #1: neighbouring chalets stand eave to eave; long-row roofs overlap like shingles and each short row of four reads as one slab from above; the source shows separate huts with cobbled gaps and visible ridges.
- P1 #2: the tree is a smooth cone with sparse flat plank branches, a spiky bottle brush and a 12-spoke pinwheel from above with soil between the spokes, not a dense fir (the v001 tree finding, surviving one targeted fix).
- P1 #3: left_side, right_side, rear and rear_north crop the upper third of the tree and the star; near stall roofs fill 20-25% of each frame.
- P1 #4: the front camera stands mid-rink with the tree dead centre and about 45% empty ice; the source's right-hand foreground of boards, garlanded handrail and east chalets is missing; the skating aid is clipped.

# Tied-arch shared cycle and pedestrian bridge (RLASM v6.1 architectural clay)

Candidate H9 of wave H (bridges) of 2026-10-19, one of the ten bridge variants the user chose from the
street and path catalogue; a street or path option, not a building. State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `shared_cycle_pedestrian_bridge / variant_1`
(catalogue variant id `shared_cycle_pedestrian_bridge_v1`) from `frontend/public/archetypes/streets/shared-cycle-pedestrian-bridge/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_1.png` | 1,241,385 | `e7cb390844e8ef6a` |
| oblique | `variant_1_angle_60.jpg` | 936,813 | `562dd0b5136f4949` |
| top | `variant_1_angle_90.jpg` | 813,673 | `f9ad53e48ce5a525` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(12 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 52 x 13 m, 13.6 m to the highest point; 0 storeys (street option: a tied-arch cycle and pedestrian bridge over a canal; the quays and blocks are context).
- storey programme: street option: a tied-arch cycle and pedestrian bridge over a canal; the quays and blocks are context
- plan: 44 m span between quays across a 40 m canal (top view), 12.8 m deck: 3.6 m red cycle lane, 1.7 m raised planter, 6.5 m footway, edge ties
- facade: silver-grey box arches leaning inward with cross ties, slim hangers, edge-tie girders, red cycle lane, planter of grasses and shrubs, pale footway, picket railings, brick quays
- inferred: the deck structure, the canal width away from the bridge and the blocks are teaching assumptions; the skew in the top view is not modelled
- levels (m): 0.00, 2.60, 12.60

## Construction and delivery (Phases C to F)

`family_tiedarch.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, arch_springing, hangers, planter_divider, cycle_lane, deck_edge, quay_under, rear_north`.

Run:

```
python tools/clay_tied_arch_shared_bridge/lock_sources.py
python tools/clay_tied_arch_shared_bridge/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_tied_arch_shared_bridge/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_tied_arch_shared_bridge
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

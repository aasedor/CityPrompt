# Heritage stone arch road bridge (RLASM v6.1 architectural clay)

Candidate H2 of wave H (bridges) of 2026-10-19, one of the ten bridge variants the user chose from the
street and path catalogue; a street or path option, not a building. State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `urban_vehicular_bridge / variant_0`
(catalogue variant id `urban_vehicular_bridge_v0`) from `frontend/public/archetypes/streets/urban-vehicular-bridge/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,312,745 | `73a50019577d6099` |
| oblique | `variant_0_angle_60.jpg` | 901,141 | `5ec846317e5ee14f` |
| top | `variant_0_angle_90.jpg` | 813,607 | `21fb51dbea07f7ed` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(12 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 55 x 18 m, 18.0 m to the highest point; 0 storeys (bridge: a four-lane road with footways over a river; the quays and town blocks are context).
- storey programme: bridge: a four-lane road with footways over a river; the quays and town blocks are context
- plan: 55 x 18 m three-arch bridge (top view) between quays 55 m apart, the road continuing east and west, quay roads north-south
- facade: three semicircular 16 m cut-stone arches with voussoired rings, coursed ashlar spandrels, pointed cutwaters rising as pilasters, dentilled cornice, stone balustrades with pedestals, double-lantern lamp standards
- inferred: the river bed, foundations and the town blocks beyond the quays are context; the deck build-up is an assumption
- levels (m): 0.00, 1.20, 9.20, 11.00

## Construction and delivery (Phases C to F)

`family_stonearch.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, arch_spandrel, cutwater_pier, balustrade, lamp_standard, roadway_deck, river_underside, rear_north`.

Run:

```
python tools/clay_stone_arch_road_bridge/lock_sources.py
python tools/clay_stone_arch_road_bridge/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_stone_arch_road_bridge/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_stone_arch_road_bridge
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

## Open blockers after v002 (v003 reworks these four)

- P1 #1: both west quadrant corners are doubled: the swept quay coping cuts through the quadrant balustrade, balusters poke under and past the slab, two concentric barriers where the source has one.
- P1 #2: the lamp scroll arms and volutes are chains of box segments with black gaps at every joint.
- P1 #3: every pier panel frame has black void squares at all four corners.
- P1 #4: rear_side clips the east end: east abutment, quadrant and end lamp off the left edge, land arch at the frame edge.

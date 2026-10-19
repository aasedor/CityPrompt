# Riveted steel through-truss road bridge (RLASM v6.1 architectural clay)

Candidate H3 of wave H (bridges) of 2026-10-19, one of the ten bridge variants the user chose from the
street and path catalogue; a street or path option, not a building. State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `urban_vehicular_bridge / variant_1`
(catalogue variant id `urban_vehicular_bridge_v1`) from `frontend/public/archetypes/streets/urban-vehicular-bridge/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_1.png` | 1,315,817 | `42e7507fd4b69a75` |
| oblique | `variant_1_angle_60.jpg` | 889,183 | `247267bf4c6d098f` |
| top | `variant_1_angle_90.jpg` | 787,029 | `8d82128556f9ac84` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(12 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 19 x 35 m, 13.5 m to the highest point; 0 storeys (bridge: a two-lane street with sidewalks over a river; quays and warehouses are context).
- storey programme: bridge: a two-lane street with sidewalks over a river; quays and warehouses are context
- plan: 34 m single-span through truss (top view) over a 29 m river between concrete quays, trusses 13 m apart, sidewalks outside them
- facade: two rust-red riveted Pratt trusses of seven panels with inclined end posts, laced verticals, gusset plates, latticed top struts and X laterals, latticed portals with knee braces
- inferred: the river bed, foundations and the warehouses are context; member sizes are teaching assumptions
- levels (m): 0.00, 5.00, 12.65

## Construction and delivery (Phases C to F)

`family_trussroad.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, portal_frame, truss_panel, deck_sidewalk, abutment, roadway_inside, river_underside, rear_north`.

Run:

```
python tools/clay_steel_truss_road_bridge/lock_sources.py
python tools/clay_steel_truss_road_bridge/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_steel_truss_road_bridge/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_steel_truss_road_bridge
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

## Open blockers after v001 (v002 reworks these five)

1. P0: the front camera stands inside the portal bay; the top chord and struts are cut off and the inclined end post, portal, abutment and river are out of frame.
2. P1: only the centre panel has crossed diagonals; the sources show crossed diagonals in every interior panel except the one next to each hip vertical.
3. P1: the overhead bracing has 5 short flat X-bays between 6 struts; the top source has 3 long near-square X-bays between 4 struts.
4. P1: a raised light-grey concrete bar crosses the whole road at each end, river side of the end-post feet; the source shows only a painted stop line.
5. P1: in rear the bus hides most of the right truss and its end-post foot.

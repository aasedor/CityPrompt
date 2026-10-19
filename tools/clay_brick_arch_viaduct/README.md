# Victorian brick arch rail viaduct (RLASM v6.1 architectural clay)

Candidate H1 of wave H (bridges) of 2026-10-19, one of the ten bridge variants the user chose from the
street and path catalogue; a street or path option, not a building. State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `rail_transit_viaduct / variant_0`
(catalogue variant id `rail_transit_viaduct_v0`) from `frontend/public/archetypes/streets/rail-transit-viaduct/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,547,636 | `fcc775ae4c2424d1` |
| oblique | `variant_0_angle_60.jpg` | 1,013,551 | `9cad3a89d960bd52` |
| top | `variant_0_angle_90.jpg` | 1,036,148 | `4b0e146b6f318bf5` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(12 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 10 x 86 m, 13.8 m to the highest point; 0 storeys (street option: a rail viaduct with shop units in its arches; terraces are context).
- storey programme: street option: a rail viaduct with shop units in its arches; terraces are context
- plan: 10 m wide brick viaduct, 85.8 m modelled run of 10 arches (top view), a 5 m flagged pavement and a 7 m cobbled street on its east side
- facade: red-brown brick arches and piers with pilasters, stone impost band, string course and coping; glazed timber shopfronts with fascia signs; blind arches on the west
- inferred: the run is cut at both ends; the shop interiors and the west gardens are assumptions
- levels (m): 0.00, 4.20, 7.20, 8.40, 9.80

## Construction and delivery (Phases C to F)

`family_viaduct.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, arch_shopfront, pier_pilasters, track_ballast, parapet_coping, train_cars, cobbled_street, rear_north`.

Run:

```
python tools/clay_brick_arch_viaduct/lock_sources.py
python tools/clay_brick_arch_viaduct/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_brick_arch_viaduct/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_brick_arch_viaduct
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

## Open blockers after v001 (v002 reworks these eight)

1. P1: the cobbled street shows only transverse joints and reads as a planked deck, not setts.
2. P1: no ballast; sleepers and rails sit on a flat light-grey slab.
3. P1: the imposts are token cubes and the arch ring runs down the jambs to the pavement, reading as a round-headed architrave rather than an arch on stone imposts.
4. P1: street-tree canopies cut into the terrace facades with windows poking through.
5. P1: the train sits flush against the far end parapet with no clear deck in front of the cab.
6. P1: the viaduct is a short closed box of about 11 bays with blind end walls and dead-end tracks; the sources show only the near end cut.
7. P1: front_corner and top sit on the north lawn side, hiding the shopfront arcade the sources show; phone board 01 pairs locked top with render aerial.
8. P1: in left_side a foreground terrace hides the lower 45% of the north elevation.

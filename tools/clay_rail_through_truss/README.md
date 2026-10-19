# Elevated riveted steel arch rail viaduct (RLASM v6.1 architectural clay)

Candidate H4 of wave H (bridges) of 2026-10-19, one of the ten bridge variants the user chose from the
street and path catalogue; a street or path option, not a building. State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `rail_transit_viaduct / variant_2`
(catalogue variant id `rail_transit_viaduct_v2`) from `frontend/public/archetypes/streets/rail-transit-viaduct/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_2.png` | 1,216,789 | `05a81c56f62e11f4` |
| oblique | `variant_2_angle_60.jpg` | 979,102 | `51e2f92755b16852` |
| top | `variant_2_angle_90.jpg` | 940,258 | `16ea61c389702f0a` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(12 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 9 x 120 m, 20.1 m to the highest point; 0 storeys (street option: an elevated rail viaduct over a promenade beside a street; the blocks are context).
- storey programme: street option: an elevated rail viaduct over a promenade beside a street; the blocks are context
- plan: 9.2 m twin-track deck, 120 m modelled run (top view): a 30 m bowstring through-truss at the south end, then 6 deck-arch spans of 15 m
- facade: riveted steel deck arches with braced spandrels and plate girders on built-up columns and concrete pedestals; a bowstring through-truss; edge railings
- inferred: the run is cut at both ends; the blocks are simplified context
- levels (m): 0.00, 1.60, 8.00, 11.60, 11.80, 12.80, 13.05

## Construction and delivery (Phases C to F)

`family_railtruss.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, arch_span, column_base, lattice_detail, track_deck, train_cars, street_under, rear_north`.

Run:

```
python tools/clay_rail_through_truss/lock_sources.py
python tools/clay_rail_through_truss/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_rail_through_truss/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_rail_through_truss
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

## Open blockers after v002 (v003 reworks these two; a second failed fix of either stops the family)

- P1 #1: the spandrel lattice is reduced to one post and one diagonal at each haunch, and the rib crown runs into and laps over the deck girder; the source front shows a deep continuous lattice of posts and N/V diagonals over the whole spandrel, including over the crown at about half the rise (the v001 arch finding, surviving one targeted fix).
- P1 #2: every car end shows a full-height solid black strip where side meets end (open seam or exposed core); the silver skin does not wrap the corner (the v001 train finding, surviving one targeted fix).

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

## Open blockers after v001 (v002 reworks these five)

1. P1: each span arch is a double-chord trussed ring with the lattice inside; the source shows a solid riveted plate rib with an open post-and-N-diagonal lattice in the spandrel above.
2. P1: full-height X-bracing in every cross-frame between the paired columns down to the pedestals; the sources show none, and it blocks the open footway under the deck.
3. P1: the train has no window openings; the window band is a flat painted stripe and the doors are flat raised plates.
4. P1: solid black voids where the through-arch truss and the deck end meet the end cap beam in front_corner.
5. P1: the arch crown does not sit on the deck: a dark slit between arch top and girder, with rib segments poking into the girder.

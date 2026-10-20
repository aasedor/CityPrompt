# Prince's Island Park (RLASM v6.1 architectural clay)

Candidate I5 of wave I of 2026-10-20, one of the ten catalogue additions the user approved
(four buildings, three parks and squares, three streets); a park and open-space option, not a building. State: **stopped at v003 by the stopping rule (the close-up planting finding survived two targeted fixes); v003 is the candidate**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `calgary_princes_island / variant_0`
(catalogue variant id `calgary_princes_island_v0`) from `frontend/public/archetypes/openspaces/princes-island-park/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,505,682 | `1b888e08c7c12b1e` |
| oblique | `variant_0_angle_60.jpg` | 979,352 | `8b979668e4f59df8` |
| top | `variant_0_angle_90.jpg` | 1,002,287 | `c172c901f34540d2` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 97 x 63 m, 14.0 m to the highest point; 1 storeys (park: a one-storey pavilion (cafe or washrooms) among paths, beds and trees).
- storey programme: park: a one-storey pavilion (cafe or washrooms) among paths, beds and trees
- plan: park 52.6 x 63 m from the west edge to the waterline (top view: pavilion roof about 12.4 x 9.4 m rotated 27 degrees), the Bow 34 m wide, a footbridge at the north to a far bank
- facade: cedar board cladding, glazed south-east face with dark mullions, sedum roof with a dark fascia, timber posts; pale slab paving with sett borders, asphalt cycle paths with yellow dashes, a concrete boardwalk with mesh railings, rip-rap, kerbed planting beds, rounded deciduous trees
- inferred: the north lawn, footbridge and far bank lie beyond the top view and follow the front and oblique; the skyline is context and not modelled; the river bed below the surface is not modelled
- levels (m): ('river', 0.0), ('park_grade', 1.0), ('boardwalk_deck', 1.45), ('pavilion_floor', 1.15), ('pavilion_eave', 4.6), ('green_roof', 5.1)

## Construction and delivery (Phases C to F)

`family_princes.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`pavilion_close, glazing_close, green_roof, porch_northwest, promenade_beds, boardwalk, riprap_bank, bench_plaza, footbridge, west_path`.

Run:

```
python tools/clay_princes_island_park/lock_sources.py
python tools/clay_princes_island_park/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_princes_island_park/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_princes_island_park
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

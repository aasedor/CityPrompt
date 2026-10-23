# Prince's Island Park (RLASM v6.1 architectural clay)

Candidate I5 of wave I of 2026-10-20, one of the ten catalogue additions the user approved
(four buildings, three parks and squares, three streets); a park and open-space option, not a building. State: **stopped at v005 by the stopping rule (independent review PASS_ZERO_P0_P1 in the planting-kit second pass the user reopened); v005 is the candidate, not keeper-approved**. Nothing here is keeper-approved,
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

## Planting (v004, second pass)

From v004 the beds are planted with the shared planting kit (`tools/clay_planting_kit_showcase`, kit v003.1): the module
is assembled as `head + common + gcommon + plantkit + body`, and `build.py` keeps the kit's linked instances out of
`clay_core.deliver()`'s per-role join (`keep_instances()`, copied from the kit showcase) and writes
`evidence/planting-kit-size.json`. The kit clearance audit must be 0 or the build fails.

v005 (kit v003.2, opt-in options unused here) answers the four v004 P1s:

- **Bed margins:** a margin pass plants a low band on rings 0.44 m and 0.86 m inside every kerb (blue edging grass,
  white alyssum cushions, small salvias, in runs of 3 to 6), and where an eye-level camera is within 8 m, small
  cushions on a ring 0.27 m inside the kerb; the groundcover undulates (bump 2.8 cm) instead of lying flat.
- **Grove beds:** the bed between the pavilion and the boardwalk is planted at 1.4 m spacing with large, wide clumps
  (fountain and feather-reed grass, shrubs, astilbe, panicles) plus an edging ring, instead of 2.1 m.
- **Black holes:** crossing joint lines sit on two levels 0.8 mm apart (plaza grid, sett running joints, band ends);
  bench legs stop under the slats, the cross rail is narrower than the legs and the back post clears the slat
  faces; door leaves run 1 cm into the sill over a solid threshold that covers the sill plane the floor slab shared
  with the opening; the footbridge kerbs are lofted in one piece, 2 cm proud of the deck side face.
- **Size cap:** each grass's crown shares its blade role (one instance node per grass), the front drifts carry fewer
  pink coneflowers and more shrub and fountain-grass mass, boardwalk pickets are 200 mm apart (was 170 mm), and kit
  instance nodes are named `k1`, `k2`, ... and drop the three tags that carry the same constant on every clay object
  (`rlasm_method`, `representation_kind`, `native_geometry_only`; `short_instance_names()` in `build.py`). Each instance
  keeps its semantic and base role, module, instance flag and archetype and variant ids; authored objects and the
  build report keep the constant tags; the prototype stays named on its shared mesh.

## Open blockers after v005 (passed)

Candidate: `clay-princes-island-park-clay-v005.glb`. None: the v005 independent review returned zero P0 and zero P1. Its P2 polish items are in `evidence/v005/independent-review.md`.

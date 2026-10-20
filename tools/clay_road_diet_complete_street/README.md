# Road-diet complete street (RLASM v6.1 architectural clay)

Candidate I9 of wave I of 2026-10-20, one of the ten catalogue additions the user approved
(four buildings, three parks and squares, three streets); a street or path option, not a building. State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `road_diet_complete_street / variant_0`
(catalogue variant id `road_diet_complete_street_v0`) from `frontend/public/archetypes/streets/road-diet-complete-street/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,577,164 | `27c582cd87e4208c` |
| oblique | `variant_0_angle_60.jpg` | 980,814 | `616c0101afe6776f` |
| top | `variant_0_angle_90.jpg` | 919,159 | `bb3d67df65ec38ed` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(12 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 96 x 128 m, 14.0 m to the highest point; 2 storeys (street option: a complete-street section at an intersection; the one- and two-storey corner blocks are the street wall it is read with).
- storey programme: street option: a complete-street section at an intersection; the one- and two-storey corner blocks are the street wall it is read with
- plan: 16.2 m main street curb to curb and 11.2 m cross street curb to curb (top view), the intersection at the centre
- facade: green protected bike lanes behind raised concrete separators with white delineator posts and rubber curb stops, a centre two-way turn lane with yellow lines, continental zebra crosswalks, planted refuge islands with keep-right signs and object markers, grass verges with mature trees, black lamp standards, signal mast arms; one- and two-storey storefront and office blocks
- inferred: the blocks beyond the corners and their rear walls and interiors are context and teaching assumptions; the signal heads are generic
- levels (m): 0.00, 0.15, 4.60, 7.60, 13.40

## Construction and delivery (Phases C to F)

`family_roaddiet.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`bike_lane_separator, refuge_island, crosswalk_zebra, bike_symbol, turn_lane, storefronts, corner_signal, cross_street_lane, verge_trees, rubber_curb`.

Run:

```
python tools/clay_road_diet_complete_street/lock_sources.py
python tools/clay_road_diet_complete_street/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_road_diet_complete_street/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_road_diet_complete_street
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

## Open blockers after v001 (x)

x

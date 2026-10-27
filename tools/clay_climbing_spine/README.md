# Climbing wall building: The Spine (RLASM v6.1 architectural clay)

Candidate K3 of wave K of 2026-10-23, one of five catalogue additions the user asked for
(all four variants of the climbing wall building, and the covered passage); a building option from the building catalogue. State: **stopped at v003 by the stopping rule (v002 and v003 did not lower v001's count, and the spine-relief finding survived two targeted fixes); v001 (0 P0 / 4 P1) is the candidate, not keeper-approved**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `climbing_wall_building / variant_2`
(catalogue variant id `climbing_spine`) from `frontend/public/archetypes/buildings/climbing_wall_building/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_2.png` | 1,420,825 | `6dc35f50b0835b37` |
| oblique | `variant_2_angle_60.jpg` | 905,088 | `a5a39a8c97f8f831` |
| top | `variant_2_angle_90.jpg` | 840,417 | `9239bd487ba29a75` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 52 x 27 m, 64.0 m to the highest point; 15 storeys (double-height retail base, thirteen floors of offices and apartments, a glazed roof amenity storey).
- storey programme: double-height retail base, thirteen floors of offices and apartments, a glazed roof amenity storey
- plan: 52 m by 27 m tower (top view, fitted to all three views) with an 18.2 m wide, 3.5 m deep notch in the street front holding the 7.4 m climbing spine
- facade: dark bronze glass curtain wall: vision glass over dark spandrels, bronze fins at 1.9 m on the street and rear faces, fins at 1.0 m with sunshade bars on the side faces
- spine: light warm-grey sculpted precast climbing strip from the plaza to 5.7 m above the roof, carved into vertical flakes and ledges with holds; six rest-station balconies on its east side
- base: double-height retail base: white canopy over the west shopfronts, glazed lobby and shops east of the spine
- roof: U-shaped paved terrace with planting beds and granite boulders inside a coped parapet; a glazed amenity block with plant on its roof over the north half
- streetscape: plaza with a boulder garden at the spine foot, a second planter, street-tree pits and lamp posts; side streets west and east, a street in front
- inferred: interiors, the north face and the north half of the side faces follow the visible grammar; the catalogue text says 20-35 storeys, the pixels show fifteen; metric dimensions are authored teaching assumptions
- levels (m): 8.00, 11.80, 15.60, 19.40, 23.20, 27.00, 30.80, 34.60, 38.40, 42.20, 46.00, 49.80, 53.60, 57.40

## Construction and delivery (Phases C to F)

`family_spine.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`boulder_garden, rest_balconies, roof_terrace, retail_base, facade_close, architecture_close, glass_close, interior, rooftop_plant, east_facade`.

Run:

```
python tools/clay_climbing_spine/lock_sources.py
python tools/clay_climbing_spine/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_climbing_spine/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_climbing_spine
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

## Open blockers after v006

Candidate: `clay-climbing-spine-clay-v001.glb`. None: the v006 independent review returned zero P0 and zero P1. Its P2 polish items are in `evidence/v006/independent-review.md`.

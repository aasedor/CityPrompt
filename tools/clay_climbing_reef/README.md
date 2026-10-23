# Climbing wall building: The Reef (RLASM v6.1 architectural clay)

Candidate K4 of wave K of 2026-10-23, one of five catalogue additions the user asked for
(all four variants of the climbing wall building, and the covered passage); a building option from the building catalogue. State: **candidate under review**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `climbing_wall_building / variant_3`
(catalogue variant id `climbing_reef`) from `frontend/public/archetypes/buildings/climbing_wall_building/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_3.png` | 1,359,680 | `c510322572ffa497` |
| oblique | `variant_3_angle_60.jpg` | 817,640 | `122c06c58a3287c7` |
| top | `variant_3_angle_90.jpg` | 811,835 | `cf5e6092abfb9702` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 30 x 27 m, 8.2 m to the highest point; 1 storeys (one tall bouldering hall under the shell (climbable outside and in)).
- storey programme: one tall bouldering hall under the shell (climbable outside and in)
- plan: four-lobed starfish plan about 30 m east-west by 27 m north-south (top view, 24.4 px to the metre), lobes north, east, south and west with concave bays between
- facade: one continuous fibreglass shell: tucked dark base, near-vertical bulging walls to about 5 m, rolling over to a 6.9 m plateau; six horizontal contour bands from deep teal to pale seafoam; rounded pockets and multicoloured holds on the walls
- openings: twelve glazed skylight domes on white rims (one large central dome, eleven small); four arched glazed entrances at the foot of the bays (two visible in the front and oblique)
- landscape: sand rubber crash-pad apron inside a low rounded curb with four diagonal gaps; white crushed-shell paths to a concrete ring path; native meadow beds on mulch, small trees, lawn beyond
- inferred: the interior hall, the north-east and north-west entrances and the shell thickness follow the visible grammar; metric dimensions are authored teaching assumptions
- levels (m): 0.00, 0.06, 5.00, 6.90

## Construction and delivery (Phases C to F)

`family_reef.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, architecture_close, glass_close, interior, entrance_sw, entrance_se, curb_gap, roof_skylights, climbing_pockets, meadow_path`.

Run:

```
python tools/clay_climbing_reef/lock_sources.py
python tools/clay_climbing_reef/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_climbing_reef/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_climbing_reef
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

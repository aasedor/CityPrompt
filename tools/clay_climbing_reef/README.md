# Climbing wall building: The Reef (RLASM v6.1 architectural clay)

Candidate K4 of wave K of 2026-10-23, one of five catalogue additions the user asked for
(all four variants of the climbing wall building, and the covered passage); a building option from the building catalogue. State: **reached the v008 version cap without a pass after the user reopened the family; v002 (0 P0 / 1 P1) remains the candidate, not keeper-approved; v008 (0 P0 / 2 P1) left two pocket-shading defects (stepped concentric shade rings and a pinched apex crease in each cup)**. Nothing here is keeper-approved,
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

## Open blockers after v008 (cap reached)

Candidate: `clay-climbing-reef-clay-v002.glb`. The v008 independent review (`evidence/v008/independent-review.md`) left these P0/P1 findings open:

- **P1** (entrance_sw (cup at 300-640,0-160), entrance_se (400-620,30-200), architecture_close (pockets at 300,480 / 500,500 / 310,750 / 580,830), climbing_pockets (540,625 / 790,800), meadow_path (all four cups), facade_close (620,600), curb_gap (320,120 / 890,90)): Each cup interior shows about 8 distinct concentric bands of flat shade, like a terraced contour map, rather than a continuous darkening into the cup. The steps are plain at close range and still show at mid range (meadow_path, curb_gap). In the sources (front: pockets at 590,240 / 830,250 / 920,470; oblique:... Likely fix: Replace the stepped per-ring shade with one continuous gradient: interpolate vertex colours, or use a radial ramp sampled per vertex with at least 16 rings or a smoothstep, and cap the total darkening at the measured...
- **P1** (climbing_pockets (dark "V" at 540,625 and 790,780), meadow_path (640,465 / 1235,560 / 400,680), entrance_se (500,160), entrance_sw (475,80), architecture_close (520,525 / 600,830), top (pockets at 375,600 / 515,605 / 625,725)): Almost every cup has a sharp dark star or slit at its deepest point. It reads as a crack or puncture in the bottom of the pocket. No source pocket has this. Likely fix: Close the cup with a small flat or spherical cap ring, not a single apex vertex. Average or weld the apex normals and keep the bottom rounded (normal equal to the cup axis). Check again at climbing_pockets and...

The candidate v002's own open findings are in `evidence/v002/independent-review.md`.

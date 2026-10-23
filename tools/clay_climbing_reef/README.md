# Climbing wall building: The Reef (RLASM v6.1 architectural clay)

Candidate K4 of wave K of 2026-10-23, one of five catalogue additions the user asked for
(all four variants of the climbing wall building, and the covered passage); a building option from the building catalogue. State: **stopped at v003 by the stopping rule (the climbing-pocket finding survived two targeted fixes); v002 (0 P0 / 1 P1) is the candidate, not keeper-approved**. Nothing here is keeper-approved,
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

## Open blockers after v003 (stopped)

Candidate: `clay-climbing-reef-clay-v002.glb`. The v003 independent review (`evidence/v003/independent-review.md`) left these P0/P1 findings open:

- **P1** (front, front_corner, left_side, right_side, rear, rear_side, climbing_pockets, facade_close, top; board phone-01): Pocket rhythm, density and distribution do not match the source. Render front shows roughly 45-55 pockets on the three visible lobe faces. Source front shows about 16-18 on the same faces. The render's pockets sit in a near-regular field on every band, including the lowest dark band and the tucked base. In... Likely fix: Cut to about 30-36 pockets in total. Put about 70% of them on the upper wall band and the roll-over shoulder. Allow no more than 2-3 per lobe face on the two lowest bands, and none within 0.6 m of the base tuck. Vary...
- **P1** (front (x 560-720, y 490-560), front_corner (x 600-700, y 560-640), roof_skylights (x 180-250, y 680-740; x 560-640, y 950-1030; x 990-1040, y 950-1030; x 1230-1270, y 600-640), architecture_close (x 370-450, y 500-580; x 880-950, y 490-550), top (ring of teal spots around the plan edge)): Roll-over and shoulder pockets read as flat teal decals or translucent raised bubbles, not hollows. Their edges are soft and ghosted, with no shadowed inner wall or lip highlight. The saturated teal lining against the pale seafoam band does all the work, so they read as polka dots. In front and roof_skylights... Likely fix: On the roll-over and roof, keep the lining in the host band's hue with only a value step (10-15% darker). Deepen those caps to at least 0.45 m, or tilt them toward the wall normal so an inner wall is visible. Add a...

The candidate v002's own open findings are in `evidence/v002/independent-review.md`.

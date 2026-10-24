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

## Open blockers after v004

Candidate: `clay-climbing-spine-clay-v001.glb`. The v004 independent review (`evidence/v004/independent-review.md`) left these P0/P1 findings open:

- **P1** (front, front_corner, aerial, top, architecture_close, rest_balconies, boulder_garden, east_facade): The spine relief reads as orthogonal stepped blocks and small cubic pockets (a voxel or camouflage pattern). In top it reads as a crumpled field of small facets. The relief breaks the spine's outer arrises, so both long edges are stair-stepped and notched (front_corner right edge, boulder_garden left edge). In... Likely fix: Rebuild the relief as about 25–35 large, vertically elongated planes 2–4 m wide and 6–15 m tall, each gently inclined (5–15°) and separated by narrow sinuous V-clefts. Drop the rectangular pockets and most of the...
- **P1** (front, front_corner, aerial, top, architecture_close, boulder_garden): The spine reads as a mid khaki/buff that is darker than the plaza paving: in top, spine face L≈113 against sidewalk L≈128. It is also visibly darker than the white notch-east wall and canopy beside it, so the spine is not the lightest element of the street front. In the sources it is the palest element: top spine... Likely fix: Raise the base albedo to a light warm grey (about 0.80/0.76/0.70 linear-equivalent sRGB), cut the cleft-face darkening to about 10–15%, and tone the notch-east wall to the same family, a hair cooler. Target spine L...
- **P1** (front, front_corner, aerial, roof_terrace, top, left_side, right_side, rear, rear_side): The roof boulders are near-identical rounded, upright faceted ovoids ("eggs"/"teeth") standing shoulder to shoulder in single file along the parapet beds, in the same buff as the spine. In the sources (oblique, front, top) the boulders are angular cleft granite in a cooler light grey and vary in shape: tall... Likely fix: Author 5–6 distinct prototypes with large planar fracture faces (flat tops, sheared sides, aspect ratios from 1:2.5 slab to 2:1 block), and vary yaw and tilt (≤15°). Give them a cool light-grey granite separate from...
- **P1** (front, front_corner, aerial, roof_terrace, rooftop_plant, left_side, rear): The amenity crown reads as a deep fluted louvre screen: narrow slats at about 0.8 m pitch with dark gaps, so there are about 40+ slats across the south face. In the sources (front, oblique) it is a flush bronze-panel box: about 18–20 broad panels of roughly 2 m across the same face, thin joints, and a dark glazing... Likely fix: Replace them with flush bronze panels about 1.8–2.0 m wide, 0.05–0.08 m reveals and ≤0.1 m relief over the upper about 2/3 of the storey, with a recessed dark-glazed band below. Keep the height, setbacks and roof plant.
- **P1** (rest_balconies, architecture_close, roof_terrace, front): The rest-station balconies project south past the spine's front face. In frontal views their west ends overlap the spine's east strip: in rest_balconies the slabs start at x≈565 while the spine arris is at x≈620, and in front the slabs start at x≈740 inside a spine ending at x≈775. In roof_terrace each slab shows... Likely fix: Start each slab at the spine's east face and limit its depth so the front edge is ≤ the spine face (within 0.1 m). If any overhang remains, add a railing return and a copper edge on the west end. Keep the 6 levels...

The candidate v001's own open findings are in `evidence/v001/independent-review.md`.

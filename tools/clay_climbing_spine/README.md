# Climbing wall building: The Spine (RLASM v6.1 architectural clay)

Candidate K3 of wave K of 2026-10-23, one of five catalogue additions the user asked for
(all four variants of the climbing wall building, and the covered passage); a building option from the building catalogue. State: **candidate under review**. Nothing here is keeper-approved,
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

## Open blockers after v002

Candidate: `clay-climbing-spine-clay-v001.glb`. The v002 independent review (`evidence/v002/independent-review.md`) left these P0/P1 findings open:

- **P0** (right_side): The top frame edge (y=0) cuts through the glazed amenity storey and the spine shaft above the roof: the amenity roof, its plant and the spine cap are out of frame. Building pixels run straight into the top border from about x 385 to 940, so this whole-envelope east view does not show the full asset. Likely fix: Raise the target point or widen the FOV until the amenity parapet, roof plant and spine cap clear the top edge by at least 5% of frame height. Keep the base and east street in frame. Re-render right_side only.
- **P1** (front, front_corner, architecture_close, rest_balconies, boulder_garden, phone-01): Spine relief is almost invisible. The source has continuous, deep, sun-and-shadow carved flakes and ledges over the full face (strong dark diagonal shadow ledges every 1–2 m). The render shows a nearly flat light panel with faint low-contrast triangular facets. On the phone board the source spine reads as sculpted... Likely fix: Raise carving depth to about 0.8–1.2 m peak (still inside the 7.4 m envelope). Add stacked ledge bands with downward-facing undersides at roughly 1.2–2 m pitch and continuous vertical flake ridges across the whole...
- **P1** (front, front_corner, architecture_close, rest_balconies, roof_terrace, top): Holds dominate the spine. About 160 high-contrast charcoal box holds cover the face evenly as a dotted speckle, the most legible texture on the spine. In the source, holds are sparse and barely visible next to the carved relief. Likely fix: Cut holds to about 40–60, cluster them along two or three climbing lines, and shrink them about 30%. Shift their colour toward mid warm grey so they read only at close range (architecture_close) and disappear at...
- **P1** (front, front_corner, aerial, roof_terrace, right_side, top, phone-01): Roof boulders are under-scaled and the wrong form. In the source front and oblique views, many massive rounded tan granite boulders (about 3–4 m) crowd the front corners of both wings and rise a full storey above the coping. In render front they barely clear the parapet (about 1.5 m showing). In roof_terrace and... Likely fix: Replace them with rounded, irregular boulder meshes (smoothing at least 2, squash 0.7–0.9, no pointed tips) in warm tan-grey granite. Cluster 4–6 large boulders (3–4 m) at each front wing corner and along the...
- **P1** (boulder_garden, front, front_corner, top, phone-01): The spine foot is a small pile of separate angular shards about 4.6 m tall, and the plaza "boulders" at the foot are tall faceted crystal prisms. In the sources, the foot is a continuous, bulging, rock-textured plinth that swells wider than the shaft through roughly the full double-height base. One large rounded... Likely fix: Model the foot as one continuous flared rock mass rising to the base head (about 8–10 m). Swell it about 0.8–1.5 m past the shaft faces at grade, with carved relief matching the shaft. Swap the plaza boulders to...

The candidate v001's own open findings are in `evidence/v001/independent-review.md`.

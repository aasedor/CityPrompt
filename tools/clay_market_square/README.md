# Market square (RLASM v6.1 architectural clay)

Candidate I7 of wave I of 2026-10-20, one of the ten catalogue additions the user approved
(four buildings, three parks and squares, three streets); a park and open-space option, not a building. State: **stopped at v005 by the stopping rule (the tier-band legibility finding survived two targeted fixes); v004 is the candidate**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `market_square / variant_0`
(catalogue variant id `market_square_v0`) from `frontend/public/archetypes/openspaces/market-square/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,087,074 | `97c2c0fa7aeddc85` |
| oblique | `variant_0_angle_60.jpg` | 730,421 | `8118270b60c14165` |
| top | `variant_0_angle_90.jpg` | 853,590 | `cb66fd45a78c456b` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 72 x 64 m, 12.0 m to the highest point; 0 storeys (open space: a serviced market and event plaza with a seating bowl and a stage pavilion).
- storey programme: open space: a serviced market and event plaza with a seating bowl and a stage pavilion
- plan: 51 m wide flared plaza of square slabs with a 3 m bollard grid; a three-tier seating bowl of 38 m chord on 29 m arcs; 16 m curved stage with a 12.4 m slatted pavilion; raised stone-walled meadow beds both sides
- facade: stacked warm-grey stone risers and walls with pale concrete treads and copings; vertical timber slat cladding in three tones; dark flat roof slab; grey bollards; slender dark floodlight masts
- inferred: the backstage door, stage side steps, the far lawn and tree belt are teaching assumptions; the meadow grass is abstracted as tufts
- levels (m): 0.00, 0.06, 0.60, 1.20, 1.80, 2.17, 6.57

## Construction and delivery (Phases C to F)

`family_marketsq.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

Camera roster: the eight whole-envelope views plus the ten family detail views
`stage_pavilion, slat_wall, seating_tiers, cheek_walls, bollard_grid, paving_drain, light_mast, backstage_door, meadow_beds, rear_north`.

Run:

```
python tools/clay_market_square/lock_sources.py
python tools/clay_market_square/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_market_square/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_market_square
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

## Open blockers after v005 (stopped)

Candidate: `clay-market-square-clay-v004.glb`. The v005 independent review (`evidence/v005/independent-review.md`) left these P0/P1 findings open:

- **P1** (left_side, right_side, rear, rear_north, rear_side, meadow_beds, front, front_corner, aerial): Landform is a mesa, not raised meadow beds. - Each flank above the bowl is a flat meadow plateau at about the wing-top level, roughly 3.6 m above the plaza. - Sheer coursed-stone cliffs bound the plateaus on the outer flanks: the wall is about 210 px tall in left_side against a lawn at plaza level. - A wall runs... Likely fix: Make each side bed one meadow surface that slopes from the low plaza-edge wall (about 0.8 m with coping) up to the backs of the wings. Then: - delete the south-facing cross wall; - lower the outer flank and north...
- **P1** (aerial, front_corner, top, front): The bowl still reads as a pale six-step flight, not two stone seating bands with pale walks. - Measured on the axis in top: terrace (153,154,153), band 2 (154,151,144), walk (160,161,160), band 1 (158,155,148), plaza (157,159,158). The "warm-stone bands" differ from the walks by about 6 to 8 RGB units, so the walk... Likely fix: Keep the geometry (2.55 m band, 1.0 m walk), but separate the materials: - give the seat treads the warm-grey stone value of the risers, or narrow the pale concrete to a nosing strip of about 0.10–0.15 m; - keep the...
- **P1** (aerial, top, front_corner, left_side, right_side (vs source oblique, top, front)): Stage side steps are missing. - In the source oblique and top, a short stair flight rises northward at each pavilion end, between the slatted side wall and the cheek wall, to the meadow behind. The source front also shows step faces behind the right cheek wall. - In the render, flat pale terrace strips run up to a... Likely fix: Add one flight of about 4–5 steps in each gap between pavilion return and cheek wall, using the same stone risers and pale treads. It climbs from the upper-terrace level to the back meadow, with the cheek wall as its...
- **P1** (front_corner (both band ends), aerial (both ends), left_side, meadow_beds): The ends of the steps overrun the bed walls. - Dark raw end faces and tread-nosing stubs stick out past the diagonal bed-wall plane at every band and walk end. In front_corner there is a dark L-shaped stub at about x 120–150, y 685–700, and a dark vertical sliver about 40 px tall where the band-2 walk meets the... Likely fix: Clip every tread, riser and walk to the inner face of the bed wall, or add a stacked-stone end cheek with coping that the steps die into. Then confirm in front_corner and aerial that no end face is visible past a...

The candidate v004's own open findings are in `evidence/v004/independent-review.md`.

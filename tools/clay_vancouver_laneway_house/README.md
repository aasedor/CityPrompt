# Vancouver laneway house (RLASM v6.1 architectural clay)

Candidate J3 of wave J of 2026-10-22, one of five catalogue additions the user asked to be chosen
(four buildings and one street); a building option from the building catalogue. State: **stopped at v003 by the stopping rule (the planting finding survived two targeted fixes); v002 is the candidate, not keeper-approved**. Nothing here is keeper-approved,
runtime-integrated, enrolled in a catalogue or activated; those remain separate checkpoints that need
the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `vancouver_laneway_house / variant_0`
(catalogue variant id `vancouver_laneway_house_v0`) from `frontend/public/archetypes/buildings/vancouver-laneway-house/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,408,640 | `6bc2fb3d703006bf` |
| oblique | `variant_0_angle_60.jpg` | 978,778 | `e753b3c4369a642d` |
| top | `variant_0_angle_90.jpg` | 852,387 | `a0cc3f3e463a046f` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png is a composite hero, not a locked view.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- envelope about 7 x 8 m, 8.3 m to the highest point; 2 storeys (living and dining on the ground floor behind the glazed corner, bedrooms and a sitting room above off the front balcony).
- storey programme: living and dining on the ground floor behind the glazed corner, bedrooms and a sitting room above off the front balcony
- plan: 7.4 x 8.1 m under one hipped roof (0.38 m side and 0.30 m end overhangs); a 2.9 x 1.0 m two-storey glazed bay at the south-west corner and a 1.0 m deep porch and balcony recess east of it, closed by a full-height cedar end fin; a 5.0 x 2.6 m one-storey garage and store against the rear wall, its hipped roof ridge running east-west along the rear wall
- facade: vertical cedar boards of varied tone with fine dark joints on a concrete plinth; heavy black window frames; a deep cedar band under the front roof edge; a horizontal-board panel over the side entry; wood front and side doors
- inferred: interiors, the east and rear walls and the garage interior are teaching assumptions; the garage, which the front view shows as a low hip-roofed building with a board door behind the house, is placed on the plan of the lower roof in the top view
- levels (m): 0.48, 3.32, 5.55

## Construction and delivery (Phases C to F)

`family_laneway.py` composes the building with the repository's own `clay_core`, `geometry` and
`assemblies` modules, unchanged; the shared wave helpers (framed openings, merged boxes, strips,
domes, ribs) are copied into the module. `build.py` is the pilot runner with the light rig
parametrised per family. Every opening is cut through its carrier, carriers butt rather than
overlap, every vertex sits at or above grade, and rooms behind glazing carry low-power inspection
lights. Renders are taken from the reimported optimised GLB only.

The garden beds are planted with the shared planting kit (`plantkit.py`, concatenated after `gcommon.py`;
its text is identical to the kit chunk in `tools/clay_planting_kit_showcase/family_plantkit.py`) as linked
instances, so `build.py` carries the kit's `keep_instances()` shim and writes `evidence/planting-kit-size.json`.

Camera roster: the eight whole-envelope views plus the ten family detail views
`facade_close, glass_close, architecture_close, entry_steps, side_entry, west_wall, roof_seams, garage, interior, garden`.

Run:

```
python tools/clay_vancouver_laneway_house/lock_sources.py
python tools/clay_vancouver_laneway_house/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_vancouver_laneway_house/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_vancouver_laneway_house
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

Candidate: `clay-vancouver-laneway-house-clay-v002.glb`. The v003 independent review (`evidence/v003/independent-review.md`) left these P0/P1 findings open:

- **P1** (front_corner, front, west_wall, left_side (against source oblique and front)): The sword-fern hedge along the side-street wall is missing (a regression from v002). See the N7 detail below this table. Likely fix: The fern cap of "40-50% per front bed" and the "sparser fern pass in the bay-front bed" were applied to the whole L-shaped bed, including its west leg along the side-street wall. The ferns' slots there went to grass...
- **P1** (entry_steps, garden, front, front_corner, garage (against source front and oblique)): The enlarged sword-fern prototype reads as bare thorny canes or bramble, not as leafy sword fern. See the N8 detail below this table. Likely fix: The frond was lengthened to 1.32 m and given an upright stretch while the pinna count and size stayed the same. The pinnae are therefore spaced out and look tiny relative to the rachis.
- **P1** (**partly fixed; superseded by new P1s N7 and N8**): Fixed: the tall feather-reed and grass mass at the bay. front x 590-830; front_corner `fc_bayfront_bed.png`; entry_steps x 0-110; glass_close x 870-1000, y 850-1080. Blue fescue is present in all front views. Fern height in the east bed is now about 0.8 m (garden, entry_steps). Not fixed: the ferns' leafy mass. The...
- **P1** (**still fixed**): side_entry: both head corners are closed cedar, minimum luma 11.4 (`side_entry_head.png`). No change from v002.
- **P1** (**still fixed**): glass_close: minimum luma 8.3; nodes continuous (`glass_nodes.png`). facade_close: only the thin black frame edge at x 383-385.
- **P1** (**still fixed**): Continuous plinth at the fin base in right_side (`right_side_fin_base.png`) and aerial.
- **P1** (**still fixed** (P2 residual N2)): In front, the boarded return and the door panel with its black head are visible (`front_sideentry.png`). front_corner shows the same.
- **P1** (**still fixed**): top: north slope with north-south seams and hipped ends; rear and rear_side agree.
- **P1** (**regressed in part (N7)**): v002 had fern rosettes in both west beds. v003 has none in the west-wall strip, and the north-of-side-steps bed is about half bare soil again.
- **P1** (**still fixed**): Whole roof and front facade in frame.
- **P1** (**still fixed**): Whole garage in frame.

The candidate v002's own open findings are in `evidence/v002/independent-review.md`.

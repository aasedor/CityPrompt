# Campus shed office (RLASM v6.1 architectural clay)

Candidate 1 of the ten-building batch. State: **candidate under review**. Nothing
here is keeper-approved, runtime-integrated, enrolled in a catalogue or activated;
those remain separate checkpoints that need the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `corporate_office_campus_headquarters / variant_3`
(catalogue variant id `industrial_warehouse_campus_hq`) from
`frontend/public/archetypes/buildings/corporate-office-campus-headquarters/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_3.png` | 1,138,281 | `3ce78a7c03f7df31` |
| oblique | `variant_3_angle_60.jpg` | 855,073 | `bc245ef2958bade8` |
| top | `variant_3_angle_90.jpg` | 806,931 | `5fb4cae8ed1cf21d` |

Origin: `catalogue_reference_nomination`. Sibling variants 0 to 2 and the folder
`hero.png` are excluded. This archetype's two other modelled variants in the clay
library (`neoclassical_brick_headquarters`) are not reused; this is a new exact variant.

## Measurement contract (Phase B)

Read from the pixels and calibrated to a 42 m street length:

- Corner lot: street to the west, loading apron and lane to the south.
- Four south-glazed sawtooth monitors running east-west at a 5.4 m pitch; the
  south-most monitor is the tallest (12.0 m) and its clerestory stands above the
  terrace; the others crown at 10.4 m; eaves and terrace at 8.4 m.
- Two-storey office box along the south edge, 8.4 m deep, with a terrace roof,
  perimeter rail, packaged rooftop unit and ducts at the west end.
- Six 7 m portal bays on the south face: corner window, roll-up door, staff door,
  two dock doors and a window under a cantilevered dock canopy; raised dock with a
  ramp and stairs.
- West face: entrance bay and corner bay with a column between, corner entrance
  under a thin canopy on the west face only, shed windows under the monitors.
- Levels 0.15 / 4.30 m; the east gable end and the north wall are not visible in
  any source and repeat the visible grammar.

## Construction and delivery (Phases C to F)

`family_office.py` composes the building with the repository's own `clay_core`,
`geometry` and `assemblies` modules, unchanged. `build.py` is the pilot runner
with the light rig parametrised per family (`LIGHT_RIG`). Side carriers are
butted into the front and rear carriers; corrugation seams, portal columns,
girts and braces are proud parts; every reveal is lined; the stoop-free entrance
sits at slab level.

Run:

```
python tools/clay_campus_shed_office/lock_sources.py
python tools/clay_campus_shed_office/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_campus_shed_office/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_campus_shed_office
```

## Version history

| version | purpose | result |
|---|---|---|
| v001 (720 px, 8 spp, 8 views) | first geometry check | silhouette and sawtooth rhythm correct; 1.66 MB GLB over budget; palette too light |
| v002 (1440 px, 32 spp, 18 views) | full roster | builder pass, aperture audit PASS, 18,490 triangles, 991,228-byte GLB; independent review **VISUAL_REWORK_REQUIRED**: 2 P0 (X-braces piercing the dock canopy; north door split by a column), 3 P1 (one-bay west face, canopy wrapped onto the south face, X-braces in every bay), 6 P2; record in `evidence/v002/independent-review.md` |
| v003 (1440 px, 32 spp, 18 views) | rework from the v002 review: braces only in the corner and east-end bays with tie rods in the canopy bays, thin canopies, two west bays with a column and upper window, west-only entrance canopy, north door off the grid, duct on a mullion line, second dock stair | builder pass, aperture audit PASS, 18,872 triangles, 1,011,064-byte GLB; independent review **VISUAL_REWORK_REQUIRED**: 0 P0, 3 P1 (west face bays composed in mirror order against both elevation sources; entrance canopy spans one bay where the sources show one thin canopy across both west bays; entrance-canopy tie rods anchor into the upper window), 6 P2. All five v002 blockers verified fixed in the pixels. v003 is the last version permitted by the brief, so these three P1 stay open as recorded blockers; the candidate is not keeper-approved |
| v004 (1440 px, 32 spp, 18 views + 4 phone boards) | rework of every open v003 finding (version cap lifted by the user; iterate to a clean review) | builder pass, aperture audit PASS, 18,898 triangles, 1,012,396-byte GLB; VISUAL_REWORK_REQUIRED, 0 P0 / 5 P1 / 7 P2 |
| v005 (1440 px, 32 spp, 18 views) | rework of every v004 P1: terrace over the corner X-brace bay only with the tallest monitor rising off the box top beam over the window bay (west face five bays), transom glazing band over the shopfront and entrance under a lowered canopy, canopy hangers anchored at the upper-storey base rail, light precast lower storey in the dock bays and under the corner window, interior camera inside the box; yellow dock nosing, dock-canopy rods from the top beam, window in the north gable bay, chair pedestals; roof ribs and clerestory panes thinned to stay under 1 MiB | builder pass, aperture audit PASS, 19,632 triangles, 1,046,712-byte GLB; VISUAL_REWORK_REQUIRED, 0 P0 / 4 P1 / 8 P2 |
| v006 (1440 px, 32 spp, 18 views) | rework of every v005 P1: one portal column per line on the west face (the coincident pair z-fought black), dock ramp running out from the dock front clear of the roller door, light precast across the whole ground storey from the corner bay with the corner sill raised, north upper windows centred between the portal columns; membrane seams, roof ribs, interior columns and chair pedestals thinned to stay under 1 MiB | builder pass, aperture audit PASS, 19,462 triangles, 1,042,564-byte GLB; independent review **VISUAL_REWORK_REQUIRED**: 0 P0 / 5 P1 / 7 P2 (up from 4, the first review that did not lower the count; v007 follows). All four v005 P1 resolved in the pixels (entrance portal column, roller door clear of the ramp, precast on the corner and roller-door bays, north windows clear of the columns). New P1: ramp rotated perpendicular to the facade; terrace only 0.6 of a monitor pitch deep; no precast base on the sawtooth bays' west walls; about 8 wide clerestory panes per monitor instead of 25-30 narrow ones; desk monitors and chairs floating |
| v007 (1440 px, 32 spp, 18 views + 4 phone boards) | Rework of all five v006 P1: ramp parallel to the facade, descending westward from the dock to the corner-bay column outside a 1 m level strip in front of the roller door, with a yellow kerb and rail; terrace deepened to 1.45 monitor pitches (all monitors one height) with the unit mid-deck in the west third; light precast base to the ground-window sills on both gables; 26 narrow clerestory lights per monitor (mullions merged into one mesh, roof ribs dropped for the GLB budget); desk monitors seated on the desks and solid chair seats on the floor | builder pass, aperture audit PASS, 19,482 triangles, 1,042,776-byte GLB; independent review **VISUAL_REWORK_REQUIRED**: 0 P0 / 1 P1 / 7 P2 (down from 5, so v008, the hard-cap version, follows). All five v006 P1 resolved in the pixels (ramp parallel to the facade, terrace depth, precast base, narrow clerestory lights, seated furniture). Open P1: the office box's west face had three bays with the bay under the south monitor gable left blank; the sources show two bays, the entrance and upper window under the gable and one wide X-braced terrace bay |
| v008 (1440 px, 32 spp, 18 views + 4 phone boards) | Hard-cap version for the v007 P1: the office box's west face rebuilt as two bays, the glazed entrance doors and upper multi-light window in the bay under the south monitor gable, one X-braced terrace bay with strip glazing over a glazed lower panel (mid-terrace column removed), the entrance canopy across both bays | builder pass, aperture audit PASS, 19,552 triangles, 1,046,560-byte GLB; independent review **VISUAL_REWORK_REQUIRED**: 0 P0 / 3 P1 / 8 P2 (up from 1). The v007 west-face finding is resolved (two bays, entrance under the gable), as are all five original v002 findings. **Ended at the v008 hard cap** of the rework stopping rule. The v007 GLB, which reviewed best (0 P0 / 1 P1), stays as the candidate; v008 is preserved as evidence only |
| v009 (1440 px, 32 spp, 18 views + 4 phone boards) | Reopened after the GLB limit was lifted (rule-2 counter reset). Rework of all three v008 P1: dock ramp two bays long down westward to the corner-bay column; corner cap plates closing the plan notch at the column heads, set 2 cm proud so no faces coincide; the perpendicular canopy hangers replaced by in-plane full-bay diagonals from each column head to the next column at canopy level; roof corrugation ribs restored every 2 m now the budget allows | roster rendering |

## Where the artefacts are

- `candidates/`: the delivered GLB as an ordinary Git blob under 1 MiB (Git LFS
  uploads are refused from the cloud build host).
- `evidence/<version>/`: build report, source entry, prework manifest, aperture
  audit, reviewer brief, independent review record, and sub-megabyte JPEG copies
  of every render and phone board.
- Full-resolution PNG renders, the locked sources and the GLB were delivered to
  the user as a zip archive per version.

## Not done, by design

Keeper approval, runtime integration (`docs/ARCHETYPE_RUNTIME_INTEGRATION.md`),
zoning use program, picker enrolment, catalogue splice and human activation.

## Open blockers after v008 (hard cap reached)

Ended at v008, the hard cap of docs/showcase/REWORK_STOPPING_RULE_2026-10-11.md. The candidate GLB is v007. Open v008 P1, for a human to weigh:

1. **Dock ramp length.** It is one bay long at about 1:5; all three sources show it 2-2.5 bays long.
2. **Terrace corner.** A small see-through hole where the parapet rail beams miss the south-west corner column cap.
3. **Canopy rods.** They are perpendicular hangers; the locked front shows in-plane full-bay diagonals.

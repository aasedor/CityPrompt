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
| v004 (1440 px, 32 spp, 18 views + 4 phone boards) | rework of every open v003 finding (version cap lifted by the user; iterate to a clean review) | west face in source order (door and upper window in the north bay, shopfront under the X-brace in the corner bay meeting a corner column), one canopy across both bays with hangers on the column lines; review pending |

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

## Open blockers after v003 (no further version permitted)

- P1: rebuild the west face in source order: upper window plus entrance door in the
  north bay, X-brace plus glazed shopfront in the corner bay, so the corner braces meet
  at the corner column.
- P1: one continuous thin entrance canopy across both west bays.
- P1: canopy tie rods must land on solid cladding, not cross the upper window.

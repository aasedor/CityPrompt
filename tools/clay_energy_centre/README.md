# District energy centre (RLASM v6.1 architectural clay)

Candidate 8 of the ten-building batch. State: **candidate under review**. Nothing
here is keeper-approved, runtime-integrated, enrolled in a catalogue or activated;
those remain separate checkpoints that need the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `central_utilities_plant_energy_centre / variant_1`
(catalogue variant id `transparent_plant_showcase_urban`) from `frontend/public/archetypes/buildings/central-utilities-plant-energy-centre/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_1.png` | 1,265,310 | `dfd3da0973e43083` |
| oblique | `variant_1_angle_60.jpg` | 888,964 | `3900dbadbd2854e5` |
| top | `variant_1_angle_90.jpg` | 805,970 | `407ae3df4a3e243f` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png (LFS pointer locally; depicts variant_0, not enrolled).

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- Two abutting blocks read from the 560 x 560 px top view at 0.064 m/px: west glazed block 19 x 34 m (roof 11.6 m), east corten block 17 x 34 m (roof 14.2 m); streets west and south.
- West block: buff brick piers on a 5.6 m bay with full-height glazed bays and transoms; board-formed concrete panel over the corner bay; recessed entrance bay at the south end of the west face; louvre and roll-up door on the north.
- East block: corten panels with recessed joints, a narrow slot window on the south, a service door and louvre on the east, two rooftop units.
- West roof: two three-fan cooling banks on the west edge, duct runs, three slender flues on a base at the centre, one hourglass exhaust stack with a dark cap and guy struts.
- Plant hall interior: chillers, pipe runs, risers, switchgear line-up and a mezzanine behind the glazing.

## Construction and delivery (Phases C to F)

`family_energy.py` composes the building with the repository's own `clay_core`,
`geometry` and `assemblies` modules, unchanged. `build.py` is the pilot runner with
the light rig parametrised per family. Side carriers are butted into front and rear
carriers, every opening is cut through its carrier with lined reveals, every vertex
sits at or above grade, and rooms behind glazing carry low-power inspection lights.

Camera roster: the ten required baseline views plus `top` and the family contact
views `plant_window, stack_contact, corten_block, roof_plant, corner_entry, interior, rear_service`.

Run:

```
python tools/clay_energy_centre/lock_sources.py
python tools/clay_energy_centre/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_energy_centre/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_energy_centre
```

## Version history

See `VERSIONS.md` beside this file; the independent review records live in
`evidence/<version>/independent-review.md`.

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

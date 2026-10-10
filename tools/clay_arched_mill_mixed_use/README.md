# Converted brick mill mixed-use block (RLASM v6.1 architectural clay)

Candidate M1 of the towers and mixed-use batch. State: **candidate under review**. Nothing
here is keeper-approved, runtime-integrated, enrolled in a catalogue or activated;
those remain separate checkpoints that need the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `industrial_brick_mixed_use / variant_0`
(catalogue variant id `industrial_brick_original_mill`) from `frontend/public/archetypes/buildings/industrial_brick_mixed_use/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,277,361 | `049dffded31d819b` |
| oblique | `variant_0_angle_60.jpg` | 924,408 | `b19c286b8e77439b` |
| top | `variant_0_angle_90.jpg` | 840,178 | `8f81fee2055fb580` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(12 files listed in `sources.json`); hero.png (LFS pointer locally; composite hero, not a locked view).

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- 30 x 20 m corner block read from the top view; ridge along the long axis; streets south and west.
- Levels 0.15 / 4.6 / 8.2 / 11.8 m; cornice 15.4 m; parapet 16.0 m; ridge 19.0 m.
- South face seven bays and gable faces four bays: brick pilasters 0.9 m between recessed panels; segmental-arched shopfronts 3.3 x 3.8 m; arched windows 2.4 x 2.7 m per storey; stone sill band; dentil cornice.
- Slate roof to raked gable parapets; glazed rooftop pavilion 14 x 6.2 x 3.3 m with a terrace rail on the south slope over the western bays; four rooflights on the north slope.
- Square brick chimney 2.2 m to 26 m at the north-east corner.

## Construction and delivery (Phases C to F)

`family_mill.py` composes the building with the repository's own `clay_core`,
`geometry` and `assemblies` modules, unchanged. `build.py` is the pilot runner with
the light rig parametrised per family. Side carriers are butted into front and rear
carriers, every opening is cut through its carrier with lined reveals, every vertex
sits at or above grade, and rooms behind glazing carry low-power inspection lights.

Camera roster: the ten required baseline views plus `top` and the family contact
views `arched_windows, corner_entry, roof_pavilion, chimney_contact, shopfront, interior, rear_yard`.

Run:

```
python tools/clay_arched_mill_mixed_use/lock_sources.py
python tools/clay_arched_mill_mixed_use/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_arched_mill_mixed_use/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_arched_mill_mixed_use
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

## Open blockers after v003 (no further version permitted)

- P0: the external chimney breast on the rear eave face interpenetrates the four sill plates of bay 2 and the bay-2 windows abut it with no pier (right_side, rear_yard). Fix is to pull the shaft inside the footprint (the source rises through the roof about 0.6 bay from the gable) or to leave a pier between it and the openings and stop the sills short.
- P1: the gable faces carry the horizontal dentil cornice, coping band and kneelers; both sources run the pilasters and recessed panels straight up into the gable to the raked coping with dentils on the eave faces only.
- P1: the gable face has four equal bays where the source shows four window bays plus a narrow blank end bay with a ground-floor door at the rear corner, so the plan should be about 1.17:1 rather than square; the blank-bay motif was placed on the unseen far gable instead.
- P1: the chimney shaft stands on the rear eave about 1.3 bays from the gable with slate between it and the gable; the source shaft rises inside the footprint immediately behind the far corner.
- P1: the rooftop pavilion is a flat-lidded glazed box at about 63 percent of the eave-to-ridge run with a shallow deck; the source is a lean-to glasshouse with a vertical glass wall behind a deeper deck and a mono-pitch glazed roof rising to the slate over about 40 percent of the run, with only a short slate gap before the gable.
- P2 (recorded): rooflights all on the rear slope against two and two; arch heads reading as projecting flat-topped plates; unjustified blank bay on the far gable; shopfront camera partly blocked by a tree trunk; aerial, front_corner and rear_side framing the asset small; a street tree over the third shopfront in the front elevation.

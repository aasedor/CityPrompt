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

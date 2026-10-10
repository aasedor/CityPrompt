# Anchored L-plaza supermarket with parking court (RLASM v6.1 architectural clay)

Candidate 10 of the ten-building batch. State: **candidate under review**. Nothing
here is keeper-approved, runtime-integrated, enrolled in a catalogue or activated;
those remain separate checkpoints that need the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `commercial_strip_mall / variant_1`
(catalogue variant id `strip_anchored_l_plaza`) from `frontend/public/archetypes/buildings/commercial-strip-mall/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_1.png` | 1,275,376 | `3f3a08740e09cc79` |
| oblique | `variant_1_angle_60.jpg` | 824,868 | `edde850b2f0e0e0c` |
| top | `variant_1_angle_90.jpg` | 875,913 | `b5bb02c1baea52cf` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); no hero.png in this folder; the catalogue hero lives in contemporary-prairie-retail-strip and is a sibling, not enrolled.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- L-plan: anchor grocery 36 x 30 m (roof 8.0 m) with a 6 m cafe wing, inline run 44 x 14 m along the north edge of the court, end-cap wing 14 x 46 m along the east edge; shops roof 5.8 m; lot 108 x 74 m with the road to the south.
- Anchor: projecting entrance tower to 11.2 m with a green sign band, glazed entrance and storefronts between brick pilasters, loading dock and doors at the rear.
- Inline run: seven glazed shop fronts under a continuous canopy at 3.9 m with brackets, brick pilasters, cream sign band, dark cornice; end-cap: four shops facing the court and a drive-through lane with bollards.
- Beige EIFS with recessed joints over a 1.2 m brick base; flat membrane roofs with rooftop units; striped parking court with cars, planters, pylon sign and a shelterbelt.

## Construction and delivery (Phases C to F)

`family_plaza.py` composes the building with the repository's own `clay_core`,
`geometry` and `assemblies` modules, unchanged. `build.py` is the pilot runner with
the light rig parametrised per family. Side carriers are butted into front and rear
carriers, every opening is cut through its carrier with lined reveals, every vertex
sits at or above grade, and rooms behind glazing carry low-power inspection lights.

Camera roster: the ten required baseline views plus `top` and the family contact
views `anchor_entrance, inline_shops, endcap_corner, parking_court, roof_units, interior, rear_service`.

Run:

```
python tools/clay_anchored_plaza_supermarket/lock_sources.py
python tools/clay_anchored_plaza_supermarket/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_anchored_plaza_supermarket/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_anchored_plaza_supermarket
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

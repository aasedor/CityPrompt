# Plus 15 glass office tower (RLASM v6.1 architectural clay)

Candidate T3 of the towers and mixed-use batch. State: **candidate under review**. Nothing
here is keeper-approved, runtime-integrated, enrolled in a catalogue or activated;
those remain separate checkpoints that need the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `calgary_plus_15_connected_tower / variant_2`
(catalogue variant id `plus15_contemporary_glass`) from `frontend/public/archetypes/buildings/calgary-plus-15-connected-tower/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_2.png` | 1,238,687 | `71df1f82ca1a5080` |
| oblique | `variant_2_angle_60.jpg` | 962,177 | `c5063f2e71b7a5f0` |
| top | `variant_2_angle_90.jpg` | 810,860 | `7fabe18811a69014` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png (LFS pointer locally; composite hero, not a locked view).

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- Square 36 x 36 m plan read from the top view; the Plus 15 bridge leaves the west end of the south face and crosses the street southward.
- Double-height lobby 6.4 m on a colonnade of 1 m columns; sixteen office floors at 3.65 m; roof 64.8 m, parapet band to 66 m.
- Every floor: 1.05 m pale spandrel band and a dark vision band with mullions at 1.5 m; pale corner columns.
- Enclosed glazed bridge 4.4 m wide from 4.6 to 7.8 m, 24 m long on two piers.
- Green roof beds around an L-shaped glazed and louvred penthouse 5.2 m high with rooftop units in its yard.

## Construction and delivery (Phases C to F)

`family_plus15_tower.py` composes the building with the repository's own `clay_core`,
`geometry` and `assemblies` modules, unchanged. `build.py` is the pilot runner with
the light rig parametrised per family. Side carriers are butted into front and rear
carriers, every opening is cut through its carrier with lined reveals, every vertex
sits at or above grade, and rooms behind glazing carry low-power inspection lights.

Camera roster: the ten required baseline views plus `top` and the family contact
views `plus15_bridge, lobby_entry, curtain_grid, roof_terrace, crown_penthouse, interior, rear_service`.

Run:

```
python tools/clay_plus15_glass_office_tower/lock_sources.py
python tools/clay_plus15_glass_office_tower/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_plus15_glass_office_tower/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_plus15_glass_office_tower
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

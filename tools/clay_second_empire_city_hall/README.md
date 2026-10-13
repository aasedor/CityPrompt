# Second Empire civic hall with clock tower (RLASM v6.1 architectural clay)

Candidate C4 of the five-building wave of 2026-10-13. State: **candidate under review**. Nothing
here is keeper-approved, runtime-integrated, enrolled in a catalogue or activated;
those remain separate checkpoints that need the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `montreal_second_empire_civic / variant_0`
(catalogue variant id `montreal_civic_city_hall`) from `frontend/public/archetypes/buildings/montreal-second-empire-civic/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_0.png` | 1,240,997 | `b65649dc4ebd7c66` |
| oblique | `variant_0_angle_60.jpg` | 875,908 | `49679d3a9749ea9d` |
| top | `variant_0_angle_90.jpg` | 819,505 | `e0480ccd7131dfa3` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); hero.png (LFS pointer locally; composite hero, not a locked view).

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- 42 x 36 m grey limestone block around a 14 x 10 m inner court (top view), streets south and west; 9 m corner pavilions and a 12 m central pavilion project 0.6 m.
- Levels 0.15 / 5.2 / 10.2 m; cornice 14.4 m; slate mansard set in 1.3 m over 3.8 m with arched dormers at every bay and a zinc flat with iron cresting; corner pavilions carry 5.4 m square mansards.
- Bays at 3.0 m: round-arched ground-floor windows 1.5 x 3.2 m in rustication; piano-nobile windows 1.5 x 2.9 m with pediments and iron-railed stone balconies on the pavilions; second-storey windows 1.4 x 2.3 m with cornice hoods.
- Four-column porch 10 m wide at the piano nobile over a rusticated arcade, broad 6 m stone stair to the forecourt; 8 m square clock tower on the central pavilion: shaft to 25.2 m, clock stage to 29.4 m, convex-concave zinc cap to 34 m, lantern and finial to 37 m.
- Iron fence on a low wall with gate piers around a lawn forecourt; north and east faces repeat the grammar; court faces plain.

## Construction and delivery (Phases C to F)

`family_city_hall.py` composes the building with the repository's own `clay_core`,
`geometry` and `assemblies` modules, unchanged. `build.py` is the pilot runner with
the light rig parametrised per family. Side carriers are butted into front and rear
carriers, every opening is cut through its carrier, faces that no source shows carry
lighter window assemblies to keep the delivered GLB under the 4 MiB blob cap, every
vertex sits at or above grade, and rooms behind glazing carry low-power inspection lights.

Camera roster: the ten required baseline views plus `top` and the family contact
views `clock_tower, porch_stair, pavilion_mansard, cornice_contact, roof_court, interior, rear_court`.

Run:

```
python tools/clay_second_empire_city_hall/lock_sources.py
python tools/clay_second_empire_city_hall/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_second_empire_city_hall/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_second_empire_city_hall
```

## Version history

See `VERSIONS.md` beside this file; the independent review records live in
`evidence/<version>/independent-review.md`.

## Where the artefacts are

- `candidates/`: the delivered GLB as an ordinary Git blob under 4 MiB (Git LFS
  uploads are refused from the cloud build host; limit lifted from 1 MiB on 2026-10-12).
- `evidence/<version>/`: build report, source entry, prework manifest, aperture
  audit, reviewer brief, independent review record, and sub-megabyte JPEG copies
  of every render and phone board.
- Full-resolution PNG renders, the locked sources and the GLB were delivered to
  the user as a zip archive per version.

## Not done, by design

Keeper approval, runtime integration (`docs/ARCHETYPE_RUNTIME_INTEGRATION.md`),
zoning use program, picker enrolment, catalogue splice and human activation.

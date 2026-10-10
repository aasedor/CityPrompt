# Limited-service highway hotel (RLASM v6.1 architectural clay)

Candidate 5 of the ten-building batch. State: **candidate under review**. Nothing
here is keeper-approved, runtime-integrated, enrolled in a catalogue or activated;
those remain separate checkpoints that need the user's decision.

## Source lock (Phase A)

`lock_sources.py` locks `highway_motor_hotel / variant_2`
(catalogue variant id `hotel_limited_service`) from `frontend/public/archetypes/buildings/highway-motor-hotel/`:

| role | file | bytes | sha256 (prefix) |
|---|---|---|---|
| front | `variant_2.png` | 1,164,853 | `3ef7d1d1b1c82a45` |
| oblique | `variant_2_angle_60.jpg` | 854,242 | `443032c73db67168` |
| top | `variant_2_angle_90.jpg` | 865,338 | `21f4b2c5722cb388` |

Origin: `catalogue_reference_nomination`. Sibling variants are excluded
(9 files listed in `sources.json`); no hero.png in this folder; the catalogue hero lives in prairie-courtyard-motor-inn and is a sibling, not enrolled.

## Measurement contract (Phase B)

Read from the pixels (metric dimensions and interiors are authored teaching assumptions):

- L-plan four-storey block: south block 32 x 20 m, north wing 20.4 x 20 m (590 x 540 px top view at 0.075 m/px); one-storey wing 18.6 x 18.5 m at the south-west with a rooflight.
- Levels 0.15 / 4.0 / 7.2 / 10.4 m; roof 13.6 m, parapet 14.3 m; glazed lobby tower 7 x 7 m at the south-east corner to 15.2 m.
- Paired punched guest-room windows per 4 m bay on every floor; beige EIFS with charcoal sections; accent band under the parapet; brick-coloured base course.
- Two glass-roofed porte-cocheres on stone-clad piers projecting 10 m east and south from the lobby corner at 4.6 m.
- Parking court west and north with cars, drive loop east, pylon sign at the road, lawn verges.

## Construction and delivery (Phases C to F)

`family_hotel.py` composes the building with the repository's own `clay_core`,
`geometry` and `assemblies` modules, unchanged. `build.py` is the pilot runner with
the light rig parametrised per family. Side carriers are butted into front and rear
carriers, every opening is cut through its carrier with lined reveals, every vertex
sits at or above grade, and rooms behind glazing carry low-power inspection lights.

Camera roster: the ten required baseline views plus `top` and the family contact
views `porte_cochere, lobby_tower, wing_contact, parapet_corner, roof_plant, interior, rear_entry`.

Run:

```
python tools/clay_limited_service_hotel/lock_sources.py
python tools/clay_limited_service_hotel/build.py --version N --output <artefact dir> [--resolution 1440 --samples 32]
python tools/clay_limited_service_hotel/phone_board.py --candidate <artefact dir>
python tools/clay_evidence_preserve.py --candidate <artefact dir> --family tools/clay_limited_service_hotel
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

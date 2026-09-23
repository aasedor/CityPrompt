# Civic and employment models — bounded Astra batch

Two independent exact-source constructors share only low-level clay utilities:

- `hall`: `community_recreation_centre / rec_centre_timber_hall`, variant 1.
- `warehouse`: `modern_bigbox_warehouse / warehouse_tilt_wall_mega`, variant 1.

This is the next finite building batch after the reviewed courtyard pilot.
No parks, roads, runtime seeding or API generation occurs. Browser checks are
deferred at the user's request until the combined batch can be tested with Sol.

Use Blender 5.2 and a fresh external candidate directory. First add `--dry-run`
to validate the source triplet without writing geometry; then run without it:

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --python tools/catalogue_services_batch/build.py -- --kind hall --source-root '<hydrated-checkout>' --output '<new-external-candidate>' --version 2
python tools/catalogue_services_batch/proof.py '<new-external-candidate>'
```

Use `--kind warehouse --version 3` for the other exact constructor. A preserved candidate
can also serve as `--source-root`. Sources and construction scripts are copied
before geometry, then the texture-free GLB is reimported for all fourteen renders.
Inspect every individual view and the four proof boards, then obtain a separate
holistic review. Never relabel a failed candidate or overwrite its evidence.

`clay_core.py` is unchanged from the reviewed courtyard/duplex low-level utility.
`proof.py` uses that pilot's deterministic delivery audit and letterboxed boards,
with neutral batch labels. The two complete compositions are authored separately
in `build.py`; neither borrows house geometry or a sibling opening schedule.

The timber hall includes the low veranda roof and intersecting upper gables.
The warehouse remains a large industrial building with high freight thresholds
and a separate three-level corner office. Neither has permission to stretch,
repeat or shrink. Sol must measure complete bounds, check plot fit and terrain,
and validate human entrances independently from goods docks.

These are conceptual native dimensions and architectural-clay models, not
engineering, code-compliance, textured-keeper or runtime acceptance claims.

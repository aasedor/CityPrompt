# Brick courtyard entrance building — Astra model phase

Bounded RLASM 6.1 architectural-clay build for
`courtyard_family_housing / courtyard_family_brick_modern`.

The exact three variant-2 catalogue images show one buff-brick frontage with
three storeys, four shallow segmental arches, two outer balcony stacks, gable
ends and six rooflights. The red-brick neighbouring blocks and the space behind
are context. This asset is the entrance building, not a fabricated whole courtyard.
Its unseen rear openings and residential interior arrangement are inferred.

`clay_core.py` is copied unchanged from the prior reviewed duplex's low-level
geometry/export/reimport utility. No duplex geometry or opening schedule is
reused. `build.py` owns the exact brick variant's geometry. `proof.py` derives
labelled, letterboxed boards and verifies source hashes, GLB delivery and cameras.

Run Blender 5.2 with a fresh external output directory:

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --python tools/catalogue_courtyard_pilot/build.py -- --source-root '<hydrated-checkout>' --output '<new-external-candidate>' --version 4 --dry-run
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --python tools/catalogue_courtyard_pilot/build.py -- --source-root '<hydrated-checkout>' --output '<new-external-candidate>' --version 4
python tools/catalogue_courtyard_pilot/proof.py '<new-external-candidate>'
```

Replay may use the immutable candidate as `--source-root`. Every build preserves
sources and construction scripts, exports a texture-free GLB, reimports that
exact file, checks bounds, and renders fourteen views. Inspect all full-resolution
images and phone boards before requesting separate holistic clay review.
Never overwrite a previous candidate or edit a failed decision into a pass.

This user-requested phase creates models and model evidence only. Browser trials,
terrain, sidewalk connections, editing, persistence and exact export belong in
the subsequent Sol phase. No seeding, publication or paid provider calls occur.
The building stays at native size; a larger plot must not stretch or repeat it.

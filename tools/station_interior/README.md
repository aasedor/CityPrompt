# Victorian station interior pilot

One exact catalogue variant: `historic_grand_station / station_victorian_iron_glass`.
The model uses the library's architectural-clay palette and physical geometry.
It is a fixed 60 × 96 m assembly with a 5.1 m change between public floors.

## Build and review

Use Blender's background Python runner with `build.py`, passing `--output` to a
new directory under `C:/dev-artifacts/CityPrompt/` and an unused `--version`.
Run the same command with `--dry-run` first. The three original catalogue
references must be hydrated from Git LFS. No image-generation calls are made.

Each candidate preserves the authoring blend, constructor and helper hashes,
source references, optimized GLB, 21 renders made after importing that GLB,
walking network and exact model/network lock. Failed candidates stay external.

After the build finishes:

```powershell
node tools/station_interior/verify.mjs <candidate-directory>
python tools/neighbourhood_buildings/review_boards.py <candidate-directory>
```

The verifier requires the runtime GLB to contain the exact authored network. It
walks every declared route in both directions, compares the floor height with
the exported mesh and sweeps a 0.44 m wide body against solid construction.
This does not cover every possible input sequence or replace browser testing.

A separate reviewer must inspect all sources, renders and phone comparisons,
then write `independent-review.json` bound to the exact model hash. Registration
requires zero unresolved P0/P1 findings in the architectural-clay review.

## Local registration

```powershell
python tools/station_interior/stage.py <candidate-directory>
python tools/station_interior/stage.py <candidate-directory> --apply
```

The first command validates the package without changing repository registries.
The second installs a local trial through the existing catalogue promotion tool.
Seed only this candidate into an isolated loopback database/object store with
`tools/seed_model_library.py --rlasm-clay-only --candidate <candidate> --local-trial`.
Run its dry-run and verification modes as well. Neither command publishes a model.

## Walking contract

The GLB carries `cityprompt_walking_json` on its walking-floor mesh. Version 2
selects the floor nearest the visitor's current height, which preserves the
concourse beneath a gallery. Height-bounded obstacles cover furniture, walls,
railings and columns. Stairs share their visible top faces with navigation.

The viewer registers the network only after the detailed model and prepared
ground are ready, using its real scene transform for centering, rotation and
altitude. Unmounting or changing the saved zone invalidates the registration.
Entry clicks inside the model start at its front entrance. The entrance-return
button, Escape and Exit walk remain available. Buildings without these optional
extras use their existing walking behavior.

This pilot uses a prepared level site. The clock tower and static passenger
coaches are not enterable; the timetable is decorative. Save/reload, placement,
rotation, normal keyboard walking, grounding and screenshots require a separate
local browser trial before claiming runtime readiness.

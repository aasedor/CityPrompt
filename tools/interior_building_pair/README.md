# Art school and courtyard hotel interior pilots

Two exact catalogue identities, using RLASM v6.1 architectural clay:

- `university_academic_complex / biophilic_mass_timber_campus`: Timber Art & Design School.
- `boutique_hotel / mediterranean_resort_courtyard`: Mediterranean Courtyard Hotel.

The generator preserves all three original references, source hashes, authored
assumptions, copied constructor/helpers, native dimensions, GLB reimport renders
and the walking network. Interior arrangements are authored inferences. Hotel
roof topology follows the top reference where it conflicts with the oblique.

## Reproduce a bounded candidate

Use Blender 5.1 in background mode:

```powershell
blender -b --python tools/interior_building_pair/build.py -- --kind school --output C:/dev-artifacts/CityPrompt/new-school-candidate --version 1 --dry-run
```

Run without `--dry-run` only after the source contract is reviewed. Use `hotel`
for the second identity. Always choose a new external output directory and
version; preserve failed candidates and their evidence.

```powershell
node tools/station_interior/verify.mjs <candidate-directory>
python tools/neighbourhood_buildings/review_boards.py <candidate-directory>
```

The verifier checks every declared route in both directions against the actual
exported walking mesh and sweeps a 0.44 m body against construction. The 0.164 m
stair risers remain below the existing 0.20 m step limit. This is route coverage,
not exhaustive proof of every possible movement sequence.

Require a separate holistic reviewer to inspect every source, all 19 renders
and three phone boards. The exact model hash must have zero unresolved P0/P1
findings before registration. Registration also requires every carrier-aperture
ray check to pass, so a room partition cannot silently overlap a doorway.

```powershell
python tools/interior_building_pair/stage.py <candidate-directory>
python tools/interior_building_pair/stage.py <candidate-directory> --apply
```

These are additive local-trial commands with an exact two-variant allowlist;
they do not publish or approve the human visual gate. Seed only the selected
candidate into the isolated loopback runtime using the existing model-library
seeder's dry-run, local-trial and verification modes. Test placement, rotation,
save/reload, normal keyboard walking and entrance recovery through the UI.

The existing opt-in version 2 building walking implementation is reused.
Heavy generated output stays external. Only reviewed GLBs (Git LFS), compact
independent evidence, catalogue registrations, scripts and result docs belong
in source control.

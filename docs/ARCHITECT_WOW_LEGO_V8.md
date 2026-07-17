# Architect-Wow LEGO v8

Version 8 turns the facade-sheet pilot into an archetype-fidelity system. The central change is that a building is no longer defined only by a material style and repeated bay. Every pilot archetype now carries a small, explicit architectural signature: the spatial and material moves that must remain recognizable after modularization.

## Quality target

The target is a City Prompt asset that reads as its archetype at three distances:

1. At block scale, the massing, roofline, base-middle-crown hierarchy, and main pavilion must be recognizable.
2. At building scale, shadow-casting signature elements—porticos, loggias, continuous balconies, buttresses, screens, oriels, turrets, and deep eaves—must distinguish one family from another.
3. At facade scale, the Gemini elevation supplies window joinery, reveals, masonry or timber variation, storefront detail, and believable material joints.

The result remains a modular real-time GLB family. It is not survey-grade photogrammetry and it does not attempt to model every fastener.

## What changed from v7

### Facade-sheet schema 3

Each cached Gemini elevation is now processed into four bands:

- `podium`: entrance, storefront, arcade, or stone base;
- `floor`: the main repeatable floor;
- `floor_alt`: an adjacent floor, used by the B module to reduce mechanical repetition;
- `crown`: the upper floor and parapet zone.

The generator prompt treats the catalogue image as a hard design reference. It names the profile's non-negotiable identity cues and material zoning, and explicitly tells the image model not to regularize away signature bays or asymmetry.

### Architectural signature profiles

[`architectural_signature_profiles.json`](../tools/archetype_compiler/architectural_signature_profiles.json) defines all twenty profiles. A profile contains:

- one concise identity description;
- the intended material hierarchy;
- optional material corrections where sparse catalogue data would otherwise produce a generic roof or accent;
- four or more reusable geometry kits.

The profile is injected into `grammar.json`, so it is visible to the facade generator, Blender generator, manifest pipeline, tests, and future renderers without changing the versioned core grammar schema.

### Reusable signature geometry

The geometry remains kit-based. Examples include:

- Nordic: stone base, warm timber picture frames, recessed balcony columns, fine roof guard;
- classical civic: ceremonial steps, giant portico, pediment, civic cornice;
- Gothic: central tower, buttresses, pointed portal, crenellated crown;
- brownstone: individual stoops, oriels, party-wall divisions, bracketed cornice;
- industrial reuse: steel bays, bracing, loading canopy, roof monitor;
- Mediterranean: ground arcade, upper loggias, quoining, tile eaves;
- modernist: pilotis, cantilever canopy, brise-soleil, concrete frame;
- châteauesque: porte-cochère, central pavilion, corner turrets, mansard dormers, chimney skyline.

These parts cast real shadows and alter silhouette. Fine joints, glass reflections, window assemblies, and weathering stay in the facade sheet.

## Generate the twenty families

```powershell
python tools/archetype_compiler/generate_worldclass_library.py `
  --registry tools/archetype_compiler/worldclass_v8_library.json `
  --output build/worldclass-v8/families `
  --force-facades
```

`--force-facades` requests new Gemini elevations using the v8 prompt. Omit it to reuse cached raw elevations. `--skip-facades` requires existing v3 sheet manifests and rebuilds only the GLBs.

To recut a cached elevation without an API request:

```powershell
python tools/archetype_compiler/generate_facade_sheets.py `
  --family build/worldclass-v8/families/nordic-timber-midrise `
  --out tools/archetype_compiler/facade_sheets_v8/nordic-timber-midrise `
  --reprocess
```

## Review and compare

```powershell
python tools/archetype_compiler/create_architect_wow_v8_gallery.py
```

The review board places the catalogue archetype, v7 baseline, and v8 signature model side by side. The checked pilot produced:

- 20 complete families;
- 20 passing validation reports;
- 6 reusable modules per family;
- assembled City Prompt-ready GLBs and preview renders;
- facade-sheet v3 manifests with four material bands.

The generated board is `build/worldclass-v8/gallery/architect-wow-v8-archetype-v7-v8.png`.

## Adding another archetype

1. Add the archetype to a library registry.
2. Add a profile in `architectural_signature_profiles.json`. Reuse existing kits first; add a new kit only for an architectural move not already represented.
3. Generate or reprocess its facade sheet.
4. Build the family and inspect the archetype comparison at thumbnail, building, and facade scales.
5. Accept only after `validate_outputs.py` passes and the signature remains legible without relying on the texture alone.

## Known next frontier

V8 materially improves identity, but true landmark reconstruction still benefits from a dedicated massing graph: separate wings, corner towers, courtyards, and non-rectangular footprints. The signature-profile contract is deliberately renderer-agnostic so a future massing-graph generator can consume the same identity cues instead of replacing this work.

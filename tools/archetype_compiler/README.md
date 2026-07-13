# Archetype Compiler

This experiment converts the existing Urban Intelligence DNA / `generation_style_input` payload into a deterministic building grammar, then runs Blender headlessly to create reusable GLB modules.

## Pipeline

```text
Urban Intelligence DNA JSON
  -> compiler.py
  -> BuildingGrammar JSON
  -> blender_generate.py
  -> podium / floor / setback / roof GLBs + manifest
  -> LEGO assembly model-library metadata
```

The compiler preserves the existing archetype ID and `downstreamHints.reuseKeys`; these are the matching keys used by the LEGO assembly API. It also reads existing footprint ranges, floor ranges, style profile, palette and facade detail when available.

## Run locally

```bash
cd tools/archetype_compiler
python compiler.py examples/nordic_mixed_use.json build/nordic_mixed_use_grammar.json
blender --background --python blender_generate.py -- build/nordic_mixed_use_grammar.json build/nordic_mixed_use
```

Outputs:

```text
build/nordic_mixed_use/
  nordic-mixed-use_podium.glb
  nordic-mixed-use_floor.glb
  nordic-mixed-use_setback.glb
  nordic-mixed-use_roof.glb
  nordic-mixed-use_manifest.json
```

## Important status

This is a first-pass procedural generator intended to prove scale, origins, stacking, archetype matching and browser export. The generated architecture is intentionally clean and simple. Production families will need richer facade grammar, texture atlases, horizontal bay composition, LOD generation, mesh optimization and visual review in the Google Tiles scene.

## Coordinate contract

- metres
- Z up in Blender source
- origin at bottom centre of every module
- front facade at negative Y in Blender
- identical footprint for podium, standard floor and roof unless the setback role is used
- transforms applied during GLB export

# Modernist Civic Block massing-graph pilot

This pilot replaces the assembled V8 floor stack for `modernist_civic_block` with an opt-in semantic massing graph. The six conventional V8 modules are still generated as a reversible fallback; only the assembled landmark GLB uses the graph.

## Why it is different

The previous model repeated a 50 × 30 metre floor plate and used signature kits as facade decoration. The pilot builds the archetype's large architectural moves first:

- a recessed public lobby and open pilotis forecourt;
- three offset floating concrete rooms;
- a rear service core and entrance cleft;
- real ribbon-window reveals and framed clerestories;
- a continuous cantilevered roof, dark soffit and parapet;
- construction-scale bevels, form-tie relief, steps and curtain-wall framing.

The recipe is stored in `architectural_signature_profiles.json` as `massing-graph@1`. `signature_profiles.py` promotes the recipe to the grammar root so renderers can consume it without treating it as an image-generation prompt.

## Generate the pilot

```powershell
python tools/archetype_compiler/generate_family.py `
  --archetype-id modernist_civic_block `
  --output build/modernist-civic-massing-pilot `
  --facade-sheets tools/archetype_compiler/facade_sheets_v8/modernist-civic-block `
  --facade-sheet-detail hero `
  --no-ao `
  --presentation-engine eevee `
  --presentation-view-set all `
  --keep-blend
```

The output includes the City Prompt-ready assembled GLB, Blender source, legacy modules, manifest, validation report, and five review renders. The manifest records the graph schema, profile, node count, assembly count and declared void count.

Create the comparison board with:

```powershell
python tools/archetype_compiler/create_modernist_massing_pilot_gallery.py
```

## Current boundary

This is the first massing pilot, not a general automatic image-to-3D solver. The graph is intentionally explicit and reviewable. The next generalization should extract the same contract from an archetype image, provide authoring overlays, and add graph recipes for courtyard, tower/setback, rowhouse and pavilion families.

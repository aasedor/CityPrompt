# Gemini Skin Realism Pilot

This pilot tests the facade-sheet method on three materially different City Prompt archetypes:

- Nordic Timber Mid-Rise
- Industrial Brick Mixed Use
- Modern Glass Office / Institutional

The objective is not to turn a building photograph into a flat box. It is to split the visual job at the correct scale:

- a rectified Gemini elevation carries timber grain, brick coursing, curtain-wall assemblies, curtains, interiors, joints, restrained weathering, and other sub-decimetre detail;
- a semantic massing graph carries the actual volume, bottom-centre placement, corners, roof silhouette, canopies, steps, frames, slabs, chimney, roof monitor, terrace, and pavilion;
- thin shadow-casting frame grids sit slightly proud of the photographic elevation so the facade responds to the runtime sun;
- the finished asset remains one lightweight assembled GLB suitable for City Prompt.

## New renderer capabilities

`blender_generate.py` now understands three optional massing-graph assemblies:

- `facade_skin`: applies one coherent rectified elevation to a specified facade plane;
- `facade_skin_stack`: composes podium, alternating floor, and crown strips at real floor heights;
- `frame_grid`: builds a separate shallow structural grid in front of a skin.

Each skin gets exact post-join 0..1 UV coordinates. The graph mesh is also normalized after beveling so its exported bottom is exactly the City Prompt origin datum.

The architectural-signature registry defines the three pilot graphs. Families without a `massing_graph` continue to use the existing modular compiler path.

## Reproduce a family

```powershell
python tools/archetype_compiler/generate_family.py `
  --archetype-id industrial_brick_mixed_use `
  --output build/gemini-skin-v9/industrial-brick-mixed-use `
  --facade-sheets tools/archetype_compiler/facade_sheets_v8/industrial-brick-mixed-use `
  --facade-sheet-detail hero `
  --no-ao `
  --presentation-engine cycles `
  --presentation-samples 32 `
  --presentation-view-set all `
  --keep-blend
```

The other archetype ids are `nordic_timber_midrise` and `modern_glass_office_institutional`.

## Outputs

Each family directory under `build/gemini-skin-v9/` contains:

- the normal reusable podium, floor, setback, crown, and roof modules;
- the assembled Gemini-skin GLB;
- a manifest accepted by the existing LEGO Assembly import endpoint;
- a validation report;
- path-traced front, street, aerial, context, and preview renders;
- the source Blender file for inspection.

Run `tools/archetype_compiler/create_gemini_skin_realism_gallery.py` to rebuild the comparison boards.

## Pilot findings

The method materially improves perceived realism without a triangle-count explosion. The assembled results are approximately 6,900 to 9,500 triangles. The most important quality rule is restraint: photographic detail and modeled detail must not duplicate one another. Oversized generic grids made the first pass look like scaffolding; thinner material-specific frames allow the generated facade to remain dominant while still creating real parallax and shadows.

The next quality step is a paired front/side Gemini generation with one shared design brief. The current pilot reuses the front elevation on the visible side, which is adequate for evaluation but not the final landmark standard. A semantic glass/masonry/window mask would also allow per-zone roughness, transmission, and normal response instead of treating the complete elevation as one photo-baked material.

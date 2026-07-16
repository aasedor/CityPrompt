# LEGO Photoreal v4

## Outcome

The builder now produces authored architectural GLBs intended to sit inside the
same scene class as the supplied quality reference: a real photogrammetric city
context with a higher-quality proposed building replacing one scanned footprint.

The reference is not just a “better material” example. It is a complete
photogrammetry / 3D Tiles scene. The production composition is therefore:

1. retain Google Photorealistic 3D Tiles for terrain, trees, roads and surrounding buildings;
2. clip the original scanned building only after its replacement GLB or LEGO stack mounts;
3. seat the authored PBR building on the measured terrain anchor;
4. preserve the clip during normal display and clean render captures.

## Building-quality changes

- Four-sided elevation authorship: construction grids, panel joints, window sills and datum lines wrap to exposed side and rear elevations.
- Real front opening depth: wall returns, sill/head surfaces and a shallow modeled interior zone replace pasted-on glazing.
- Improved PBR response: catalogue colour steers albedo textures; normal, roughness and baked AO remain attached; coated glass uses stronger image-based lighting in the globe.
- Archetype-specific rhythm: the timber family uses sparse staggered planted bays and selected variants no longer inherit an unsupported setback from generic parent copy.
- Entry detail: layered door glass, transom and hardware augment the portal / recessed / arched / colonnade systems.
- Roof authorship: coping, service pads, air-handling units, fan cowls, louvers, access penthouse, vents, drain-scale details, planted roof and PV field.
- Persistent tile replacement: stencil volumes moved outside the hideable planning-overlay group and are gated by the set of successfully mounted models.
- Cached GLTF material isolation: every placed scene receives cloned and tuned materials, texture anisotropy and architectural glass treatment without mutating shared loader state.

## Generated pilot

Four variant families were generated with six reusable modules each plus an
assembled GLB and four review cameras:

- Mass Timber Biophilic Infill — 8 floors
- European White Render Boutique — 6 floors
- Contextual Dark Brick Classical — 7 floors
- Limestone Panel Contemporary Infill — 5 floors

All module bounds, coordinate contracts, manifests and assembled files pass the
existing validator. The generated review assets are in `docs/lego_photoreal_v4/`.

## Performance boundary

This pass deliberately favors the requested close/aerial quality. The assembled
pilots range from roughly 70k to 115k triangles and some exceed the advisory
8 MB texture budget. That is acceptable for the pilot and current placement cap,
but production expansion should add generated distance LODs and texture KTX2
compression. It should not flatten the close-view geometry that created the
quality improvement.

## Verification

- Archetype compiler tests: 33 passed.
- Frontend tests: 179 passed, including 20 targeted stencil/material/LEGO placement tests.
- Frontend TypeScript type-check: passed.
- Four complete Blender families: validation passed.
- Visual QA: front/oblique, street, aerial and wider urban context reviewed for each family.

## Primary visual review files

- `docs/lego_photoreal_v4/quality_bar_translation.png`
- `docs/lego_photoreal_v4/v4_showcase.png`
- `docs/lego_photoreal_v4/mass-timber_v4_review.png`
- `docs/lego_photoreal_v4/white-render_v4_review.png`
- `docs/lego_photoreal_v4/dark-brick_v4_review.png`
- `docs/lego_photoreal_v4/limestone_v4_review.png`

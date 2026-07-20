# Archetype-matched massing and physical glazing pipeline

This pilot combines reference-guided Gemini facade sheets with softened semantic massing and a two-range glazing system. It is designed for the City Prompt workflow: draw a footprint, assemble the LEGO model, orbit in Google Tiles, then make a styled render.

## What changed in v11

- The facade generator now uses the exact `generation_archetype_id` card (for example `variant_0.png`) instead of the broader family hero whenever that card exists.
- Prompts preserve curved and arched openings and coordinated variation instead of forcing an identical repeating floor.
- Landmark massing supports real beveled gable roofs. Industrial Brick now has a shallow gable, softened eaves, a chimney and a glazed monitor instead of a flat box.
- Nordic Timber has a shadow-casting glulam post-and-beam grid, recessed loggias and a roof pavilion.
- Modern Glass Office uses its complete registered elevation on the assembled landmark, avoiding artificial strip repetition. UV crop metadata removes neutral image margins without moving the semantic glass mask or room cards.
- Structural boxes use small multi-segment construction bevels. These radii are deliberately subtle: they create edge highlights and soften the silhouette without turning masonry into rounded plastic.
- Every occupied room card uses one of seven lit atlas cells. The previous dark-blue/off cell is excluded.

## Runtime glazing LOD

- **Near, below 180 m:** the opaque facade, recessed physical panes and shallow lit room cards are shown.
- **Far, above 230 m:** the complete baked Gemini facade is shown.
- **180-230 m:** hysteresis retains the current mode to prevent orbit flicker.
- A city image-based reflection environment is enabled in the LEGO builder and standalone model viewer; the globe supplies the equivalent environment.

Every semantic material exports a `glazing_lod` glTF extra: `far`, `near`, `physical`, or `interior`. City Prompt switches visibility on the loaded model rather than fetching a second asset.

## Hybrid glass, not a decal

Four construction profiles live in `tools/archetype_compiler/glass_profiles.py`:

| Profile | Use | Optical character |
|---|---|---|
| `low_iron_clear` | lobbies and retail | neutral, high transmission |
| `reflective_curtain_wall` | office and institutional | restrained low-E reflectance |
| `industrial_sash` | factories and lofts | slightly dirty historic glazing |
| `residential_low_e` | apartments | warm-neutral residential glass |

The near material retains Principled transmission, IOR, roughness, specular and clearcoat. Registered Gemini pane colour is mixed into the physical base and contributes a small pane-specific emission, preserving reflected buildings and varied interiors without making every window a uniform lightbox.

The physical section is assembled in the correct order:

1. opaque facade at the wall face;
2. physical glass recessed behind the face;
3. warm room card behind the glass but in front of the smaller shadow core;
4. authored frame detail at the face.

`frame_mode: mask_only` is used when the Gemini sheet already contains registered arches, rails or mullions. This avoids the coarse rectangular cages that made earlier pilots look computer generated.

## Semantic mask generation

`generate_facade_sheets.py` asks the selected image provider for a pixel-registered binary selection:

- white: vision glass, glazed doors and curtain-wall vision panels;
- black: frames, mullions, rails, masonry, cladding, spandrels and shadows.

The response is resized, binarized, despeckled and sliced with the facade bands. `manifest.json` uses `facade-sheet@4` and records provider, model, mask source, coverage and grouped openings. Gemini remains the default; GPT Image 2 is selected with `--provider openai`. A deterministic fallback remains available when either image service is unavailable.

```powershell
python tools/archetype_compiler/generate_facade_sheets.py `
  --family build/gemini-skin-v9/modern-glass-office-institutional `
  --out tools/archetype_compiler/facade_sheets_v8/modern-glass-office-institutional `
  --force-mask
```

## Delivery format

Blender exports embedded alpha textures as high-quality WebP using `EXT_texture_webp`. Three.js r170's `GLTFLoader` supports this directly. It avoids the large lossless RGBA PNGs created when photographic colour and a semantic alpha mask are packed together.

| Family | Profile | Glass coverage | Assembled triangles | GLB size | Validation |
|---|---|---:|---:|---:|---|
| Modern Glass Office | `reflective_curtain_wall` | 33.6% | 4,888 | 0.94 MB | pass |
| Industrial Brick Loft | `industrial_sash` | 23.5% | 9,648 | 4.79 MB | pass |
| Nordic Timber Residential | `residential_low_e` | 23.4% | 17,708 | 4.18 MB | pass |

All are below the 8 MB assembled-asset budget. The comparison board and generated models are under `build/glass-lod-v11/`.

## Remaining production work

1. Add automated visual scoring for silhouette, storey count, opening rhythm and material zones before approving a Gemini elevation.
2. Reject or regenerate sheets that ignore an explicit storey count; do not fix that error by vertically warping a multi-floor crown crop.
3. Consolidate repeated module materials to reduce draw calls even though file size and triangle budgets now pass.
4. Roll the exact-card + semantic-massing recipe through the remaining archetype library, retaining family-specific roof and corner grammar rather than one universal box.

## v15 PBR and semantic assembly pilot

The Parisian/Haussmann pilot upgrades the sheet contract to `facade-sheet@5` and makes the close/city split explicit:

- each elevation band has registered albedo, normal, roughness, AO, 16-bit depth and emissive maps;
- albedo is de-lit in linear colour space, so City Prompt's environment and sun remain the lighting authority;
- one 2K close atlas and one 1K city atlas are generated for each semantic band;
- podium/entrance, corner returns, crown and mansard roof are fixed assemblies;
- `typical_a`, `typical_b`, and `typical_c` repeat only in the middle stack;
- front, rear, left and right skins use the same real-metre repeat span;
- heritage windows use cut-out opaque skins, recessed physical glazing, room cards and stone returns;
- audited storey crops prevent a single LEGO module from accidentally containing two or three compressed floors.

Generate the registered PBR source package:

```powershell
python tools/archetype_compiler/upgrade_facade_pbr.py `
  --source tools/archetype_compiler/facade_sheets_v8/parisian-midrise-block `
  --output tools/archetype_compiler/facade_sheets_pbr_v15/parisian-midrise-block `
  --near-width 2048 `
  --far-width 1024
```

Build a resizable City Prompt family:

```powershell
python tools/archetype_compiler/generate_family.py `
  --archetype-id parisian_midrise_block `
  --family-id codex-lego-pbr-parisian-v15 `
  --output build/codex-lego-pbr-parisian-v15b `
  --floors 6 --width 30 --depth 20 `
  --facade-sheets tools/archetype_compiler/facade_sheets_pbr_v15/parisian-midrise-block `
  --facade-sheet-detail city --no-ao
```

Package only the deployable LEGO modules as resumable UASTC KTX2 assets:

```powershell
python tools/archetype_compiler/package_ktx2.py `
  build/codex-lego-pbr-parisian-v15b `
  --output build/codex-lego-pbr-parisian-v15b-ktx2 `
  --ktx-bin build/tools/ktx/installed/bin/ktx.exe `
  --level 4 --jobs 8 --resume --skip-assembled
```

The City Prompt LEGO globe layer, composer and standalone model viewer now register `KTX2Loader`. Set `VITE_KTX2_TRANSCODER_PATH` to a self-hosted Basis transcoder directory in production; without it, the loader uses the matching official Three.js r170 CDN files.

## v17 Kinnaird-quality reference-guided pilot

The Parisian pilot can now start from a deliberately rectified, shadow-neutral elevation instead of accepting the first provider output. Pass the audited image with `--elevation`; the upgrader records its filename and role in the `facade-sheet@5` manifest, then derives one registered 4K near PBR set and a 1K city set.

```powershell
python tools/archetype_compiler/upgrade_facade_pbr.py `
  --source tools/archetype_compiler/facade_sheets/parisian-midrise-block `
  --elevation tools/archetype_compiler/facade_sources_openai_v16/parisian-midrise-block/elevation-gpt-shadow-neutral-v1.png `
  --output tools/archetype_compiler/facade_sheets_pbr_v16/parisian-midrise-block `
  --near-width 4096 --far-width 1024
```

The close model and city LOD intentionally have different construction budgets:

- **Hero:** registered 4K albedo/normal/roughness/AO/depth/emissive, physical recessed panes, warm room cards, stone returns, bevelled cornices and forged balcony scrollwork on all elevations.
- **City:** registered 1K baked facades on all elevations, coarse silhouette-critical rails and no per-pane physical overlays.
- **Fixed assemblies:** entrance/podium, corner returns, crown, mansard roof, dormers and the Haussmann roof deck/lightwell never enter the repeat loop.
- **Repeatable assemblies:** only `typical_a`, `typical_b`, and `typical_c` are stacked, preventing the entrance and crown from being stretched when a City Prompt polygon changes size.
- **Delivery:** deployable module GLBs are repackaged as UASTC KTX2 and declare `KHR_texture_basisu`; the editable PNG PBR source remains outside the runtime asset.

Large Haussmann footprints now receive a real central roof court rather than a featureless dark cap. Rear and side dormers receive the same occupied-room treatment as the street elevation, so aerial views read as a complete building rather than a decorated front box.

## v18 geographic footprint assembly

City Prompt no longer has to reduce every drawn building polygon to one rectangle. For archetypes that opt into `footprintCompatibility`, the LEGO Builder measures the real polygon in local metres, aligns it to its longest edge and classifies its re-entrant corners as one of four profiles:

- `rectangle`: one streetwall segment;
- `l_shape`: two joined streetwall segments;
- `u_shape`: a front bar and two return wings;
- `courtyard`: four bars enclosing a usable central court.

Each segment reuses the same podium, interchangeable middle bays, crown and roof modules. The saved assembly recipe carries segment position, Z rotation and local X/Y scale, so the browser renderer and exported GLB reconstruct the same geographic form. Architectural materials, dormers and occupied-window treatment therefore continue around every wing instead of appearing only on a decorated front plane.

The archetype catalogue is the design authority for fit. `footprintCompatibility` records global limits plus per-profile width, depth, floor, wing-depth and minimum-courtyard ranges. The Parisian pilot currently recommends:

| Profile | Overall width | Overall depth | Floors | Wing depth |
| --- | ---: | ---: | ---: | ---: |
| Rectangle | 24-42 m | 16-24 m | 5-7 | n/a |
| L shape | 32-40 m | 24-30 m | 5-7 | 8-12 m |
| U shape | 36-42 m | 26-32 m | 5-7 | 9-13 m |
| Courtyard | 36-42 m | 32-38 m | 5-7 | 9-12 m |

These are architectural recommendations, not arbitrary API clamps. City Prompt shows when a user's polygon sits outside the preferred envelope, while still allowing the planner to produce a model when the module scale remains safe. Widths near the 3 m authored facade-bay multiple retain the best Haussmann window rhythm.

## v19 Parisian detail correction

The first geographic-footprint render exposed four close-range defects that are now corrected in the reusable Parisian kit:

- dormers use the same standing-seam zinc as the mansard, with slim two-part dark sashes and occupied-room cards instead of white stone boxes and dense grids;
- the podium uses recessed bronze-framed shopfront bays, textured dark-oak double doors, transoms, kickplates and PBR limestone piers;
- unsupported `shopfront_canopies` no longer generate floating black slabs—the archetype's shallow sign fascia and framed storefront construction provide the depth;
- every LOD carries textured, bevelled 45-degree corner pavilions with their own glazing and wrapping datum bands, rather than thin applied quoin strips at a perfect box corner.

These elements are parameterized by module width and height. They therefore remain fixed architectural end conditions while middle facade bays repeat across compact, wide, L, U and courtyard assemblies.

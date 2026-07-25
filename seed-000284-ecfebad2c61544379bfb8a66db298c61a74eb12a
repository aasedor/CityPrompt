# Facade Sheet Pipeline

> Production memory: use this pipeline together with
> [`HIGH_QUALITY_3D_BUILDING_MEMORY.md`](HIGH_QUALITY_3D_BUILDING_MEMORY.md).
> Its versioned assessor separates structurally invalid families from valid
> outputs that merely need visual review, allowing catalogue-scale batches to
> continue safely.

The facade-sheet pipeline is the v7 high-fidelity path for LEGO building families. It follows the construction pattern observed in the Chicago and Kinnaird reference assets: keep massing and silhouette in geometry, but place windows, reveals, shopfronts, masonry variation, panel joints, and restrained weathering in a rectified photographic facade atlas.

The result is more detailed than a fully procedural facade at City Prompt viewing distances, while remaining modular and far lighter than modelling every joint and window assembly as bespoke geometry.

## What is integrated

The pipeline is now an optional, end-to-end input to the existing archetype compiler:

1. `generate_family.py` exports the real City Prompt catalogue archetype and compiles its deterministic Building Grammar.
2. `generate_facade_sheets.py` sends the archetype card and construction brief to a selectable image provider as a texture-map request, not a whole-building rendering request. Gemini remains the default; `--provider openai` uses `gpt-image-2`.
3. The generated orthographic elevation is cached as `elevation_raw.jpg`.
4. Row-variance autocorrelation detects the actual repeated floor pitch. This is important because image models do not always obey the requested floor count exactly.
5. The tool cuts one repeatable upper-floor band and one podium band, flattens illumination, moves distinctive accent bays away from the tile seam, and blends only the horizontal edges.
6. It derives conservative roughness and warm-window emissive masks.
7. `blender_generate.py --facade-sheets <directory>` builds a hybrid module: thin photographic skins over a normal PBR core, plus real roof, cornice, canopy, balcony, terrace, and setback geometry where those elements change the silhouette or cast useful shadows.
8. The normal validation and manifest-import path makes the family available to the LEGO planner and City Prompt globe.

The source elevation is first reduced to modular floor and podium bands instead of wrapping one complete building photograph. The `hero` profile keeps generated PBR side/rear walls and a full geometric window system. The lighter `city` profile repeats the rectified bands on side/rear skins, matching the atlas strategy of the Chicago reference: it produces detailed orbit views with far fewer draw calls and triangles. Roofs, projections, terraces, cornices, and shadows remain geometry in both profiles.

## Generate one family

First create the grammar and baseline family directory:

```powershell
python tools/archetype_compiler/generate_family.py `
  --archetype-id london_heritage_mansion_block `
  --output build/archetypes/london-heritage-mansion-block `
  --skip-thumbnail
```

Generate the facade sheet:

```powershell
backend/.venv/Scripts/python.exe tools/archetype_compiler/generate_facade_sheets.py `
  --family build/archetypes/london-heritage-mansion-block
```

Regenerate the modular family with the facade sheet attached:

```powershell
python tools/archetype_compiler/generate_family.py `
  --archetype-id london_heritage_mansion_block `
  --output build/archetypes/london-heritage-mansion-block `
  --facade-sheets tools/archetype_compiler/facade_sheets/london-heritage-mansion-block `
  --facade-sheet-detail city `
  --textures tools/archetype_compiler/textures_worldclass_v7 `
  --no-ao
```

The Gemini key is read from `GEMINI_API_KEY`, `--api-key`, or `backend/.env`. Re-running without `--force` reuses the cached raw elevation. Use `--reprocess` to re-cut the bands without any API call.

### GPT Image comparison pilot

GPT Image uses the same exact archetype card, rectified-elevation brief, band processor and GLB compiler, so the comparison changes only the image provider. Its cache defaults to `facade_sheets_openai/<family>` and cannot overwrite the Gemini baseline.

```powershell
$env:OPENAI_API_KEY = "<local key>"
backend/.venv/Scripts/python.exe tools/archetype_compiler/generate_facade_sheets.py `
  --provider openai `
  --family build/archetypes/london-heritage-mansion-block `
  --force
```

`OPENAI_API_KEY` can also live in the ignored root `.env` or `backend/.env`. The key is never written to the façade manifest. The manifest records `provider`, `model`, and independent semantic-glass provenance. `--mask-provider deterministic` is useful for a cheaper first-pass sheet; the default `same` uses GPT Image for both elevation and mask when `--provider openai` is selected.

## Generate the twenty-family pilot

The library definition is `tools/archetype_compiler/worldclass_v7_library.json`. The batch is resume-safe and records an index after every attempted family:

```powershell
backend/.venv/Scripts/python.exe tools/archetype_compiler/generate_worldclass_library.py
```

Useful controls:

```powershell
# One family only
backend/.venv/Scripts/python.exe tools/archetype_compiler/generate_worldclass_library.py `
  --only parisian_midrise_block

# Rebuild models from cached sheets without image API calls
backend/.venv/Scripts/python.exe tools/archetype_compiler/generate_worldclass_library.py `
  --skip-facades

# Hero-quality side and rear elevations plus all review views
backend/.venv/Scripts/python.exe tools/archetype_compiler/generate_worldclass_library.py `
  --facade-sheet-detail hero `
  --presentation-view-set all
```

Outputs are written under `build/worldclass-v7/families/`. The consolidated index is `build/worldclass-v7/worldclass-library-index.json`.

## Import into City Prompt

With the backend running and a normal SiteForge token/login configured:

```powershell
python tools/archetype_compiler/import_worldclass_library.py
```

The importer includes only families whose validation report is `pass`. It calls the existing `/api/v1/lego-assembly/import-manifest` endpoint, so no second model registry or placement system is introduced.

## Runtime material calibration

Facade sheets contain photographic shading. Applying the globe's full analytic environment response on top creates pale, plastic-looking walls. Materials named `MAT_Sheet_*` therefore use a dedicated `photo_baked_v1` profile in both the LEGO composer and globe layer:

- ambient-occlusion maps are removed to avoid double-darkening and mismatched AO UV artifacts;
- environment intensity is reduced;
- roughness is forced high and metalness to zero so the strong city sun does not add a second synthetic sheen;
- base-colour textures are explicitly treated as sRGB.

All non-sheet materials retain the normal architectural PBR treatment.

## Quality rules learned from the pilot

- Ask for an architectural **texture map**, not an image of a building. The latter invites sky, pavement, perspective, and invented massing.
- Detect the generated floor pitch instead of trusting the requested number of storeys.
- Derive strip span from the image aspect ratio. Forcing the requested bay width can visibly squeeze windows.
- Move a distinctive accent bay away from the horizontal seam before blending.
- Keep photo detail on the hero elevation, but keep silhouette-changing elements in geometry.
- Never bake normal module AO on top of a photographic sheet.
- Validate bottom-centre origins, dimensions, triangle counts, and file sizes before importing.

## Current limits and next work

- One generated elevation currently supplies the modular atlas on every city-profile side. This is coherent for repetitive blocks, but landmark corners will benefit from paired front/side generations with a shared material brief.
- Emissive masks are heuristic warm-window masks. A model-generated semantic window/glass mask would separate gloss and emission more accurately.
- The sheet is repeated per module, which is intentional for LEGO assembly but can repeat recognizable interiors over very tall stacks. A future atlas can carry two or three typical-floor variants.
- Photographic materials must be rechecked if the globe exposure or light rig changes.

These are incremental extensions to the same manifest and module contracts; no replacement of the City Prompt planner is required.

# Building Archetype Image Library

This repository now uses a generated archetype image system for **building style selection**.

## Source of Truth

- Config: `frontend/src/data/buildingArchetypes.json`
- Generated assets: `frontend/public/archetypes/buildings/`
- Generated manifest: `frontend/public/archetypes/buildings/manifest.json`

## Archetype Model

Each archetype in the config defines:

- `id`
- `title`
- `aestheticCategory`
- `buildingSubcategory`
- `developmentTypes`
- `generationTags`
- `styleProfile`
- `prompt.subject`
- `prompt.details`
- `prompt.negative`
- `palette`

The visual system block defines shared card rules:

- front-facing camera requirement
- consistent framing/crop
- output size/aspect ratio
- shared rendering style rules
- shared negative guidance
- variant definitions (front day / golden hour / overcast / rain reflection)

## Regenerating Archetype Images

Run:

```bash
node scripts/generate-building-archetype-images.mjs
```

This script:

1. reads `frontend/src/data/buildingArchetypes.json`
2. generates consistent archetype card SVGs for each variant
3. writes a manifest with prompt metadata and image paths

## Downstream Generation

The selected archetype image and style metadata are stored into zone properties and propagated through `generation_style_input` so future 3D generation can use:

- development type
- building subcategory
- aesthetic category
- selected archetype image id/path
- generation tags
- style profile
- canonical style prompt


## Community Archetype Expansion

The archetype system now spans all core community systems:

- Buildings: `frontend/src/data/buildingArchetypes.json`
- Streets and Pathways: `frontend/src/data/streetPathArchetypes.json`
- Parks and Plazas: `frontend/src/data/openSpaceArchetypes.json`
- Shared visual rules and prompt templates: `frontend/src/data/archetypeVisualSystem.json`

### Seed and Image Generation

To regenerate the full catalog from structured seed/config data:

```bash
node scripts/seed-community-archetypes.mjs
node scripts/generate-community-archetype-images.mjs
```

The seed script now generates a larger, scalable archetype taxonomy across all domains with structured metadata fields used by downstream generation.

### Reusable 3D Asset Library

Generated models are indexed in the reusable model library with signature metadata (archetype/category/subtype/tags/dimensions/style profile).

- Matching helpers: `backend/app/services/reusable_model_library.py`
- Generation-time reuse lookup: `backend/app/tasks/processing.py`
- API endpoint for suggestions: `GET /api/v1/model-library/buildings/{building_id}/recommendations`

The reuse flow now supports:

1. exact signature-key match reuse (prevents near-identical regeneration)
2. scored similarity matching for close archetype/style candidates
3. automatic registration of newly generated assets for future reuse


## Premium Photoreal Render Pipeline (All Domains)

For production-quality archetype cards (buildings, streets/pathways, parks/plazas), use the OpenAI render pipeline:

```bash
# Dry run: writes prompt manifests only
node scripts/render-community-archetype-images-openai.mjs --dry-run

# Generate premium card images (PNG + SVG wrappers) for all domains
OPENAI_API_KEY=your_key_here node scripts/render-community-archetype-images-openai.mjs --overwrite

# Example: buildings only, first 20 archetypes
OPENAI_API_KEY=your_key_here node scripts/render-community-archetype-images-openai.mjs --domains=buildings --limit=20 --overwrite
```

Environment options:

- `ARCHETYPE_IMAGE_MODEL` (default `gpt-image-1`)
- `ARCHETYPE_IMAGE_QUALITY` (default `high`)
- `ARCHETYPE_IMAGE_SIZE` (default `1536x1024`)
- `ARCHETYPE_IMAGE_DELAY_MS` (default `900`)
- `ARCHETYPE_ONLY` (optional archetype id filter)

This pipeline enforces shared benchmark rules (front-facing/centered composition, photoreal material quality, consistent framing/mood) and writes per-variant prompt manifests under:

- `frontend/public/archetypes/<domain>/prompts/<archetype>/<variant>.json`

Generated assets are stored as:

- `<variant>.png` (raster image)
- `<variant>.svg` (wrapper used by existing UI pathing)

so the UI can keep referencing stable `.svg` paths while rendering premium generated imagery.

### Image Metadata for 3D Conversion

The OpenAI render pipeline now writes structured conversion metadata for every archetype image variant:

- Prompt payload: `frontend/public/archetypes/<domain>/prompts/<archetype>/<variant>.json`
- Conversion metadata: `frontend/public/archetypes/<domain>/metadata/<archetype>/<variant>.json`
- Manifest references: `frontend/public/archetypes/<domain>/manifest.json`

Each metadata payload includes:

- `generationStyleInput` aligned to platform zone properties (`generation_style_input` / `generation_style_inputs`)
- `modelConversionHints` for geometry strategy, parametric inputs, material slots, scene elements, and reuse signature keys
- `imageRefs` with stable SVG/PNG/prompt/metadata paths

SVG wrappers also embed a compact `<metadata>` JSON block with references to prompt and metadata files for portable downstream tooling.

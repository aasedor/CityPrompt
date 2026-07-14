# LEGO Assembly Experiment

Branch: `experiment/lego-assembly`

This experiment replaces one-off AI building generation with reusable,
archetype-aware GLB modules. It intentionally builds on the existing Urban
Intelligence DNA and aesthetic catalogue rather than introducing a competing
style taxonomy.

## Current scope

The first slice supports vertical composition:

1. podium
2. repeatable upper floor
3. optional setback floor for taller buildings
4. roof

The backend returns a renderer-neutral assembly recipe. The frontend preview
loads each GLB module and stacks it using the returned transforms.

## Reusing Urban Intelligence DNA

The frontend passes the existing values from `generation_style_input`:

- `archetypeId`
- `downstreamHints.reuseKeys`

The planner uses these values alongside footprint dimensions and floor count to
rank compatible module families. Existing archetype IDs and reuse keys remain
the canonical identity for architectural style.

## Configuring library items as modules

No migration is required for the experiment. Existing `ModelLibraryEntry`
records use their `metadata` JSON field.

Example metadata:

```json
{
  "lego": {
    "enabled": true,
    "role": "floor",
    "family": "nordic-midrise",
    "width_m": 24,
    "depth_m": 18,
    "height_m": 3.2,
    "repeatable_z": true,
    "archetype_ids": ["nordic-midrise"],
    "reuse_keys": ["nordic", "mixed-use"],
    "min_floors": 3,
    "max_floors": 12
  }
}
```

The API can add this metadata to an existing model-library item:

```http
PUT /api/v1/lego-assembly/modules/{model_library_item_id}
```

Request:

```json
{
  "role": "floor",
  "family": "nordic-midrise",
  "width_m": 24,
  "depth_m": 18,
  "height_m": 3.2,
  "repeatable_z": true,
  "archetype_ids": ["nordic-midrise"],
  "reuse_keys": ["nordic", "mixed-use"],
  "min_floors": 3,
  "max_floors": 12
}
```

A usable family currently requires:

- one `podium`
- one repeatable `floor` for buildings taller than one storey
- one `roof`

A `setback` is optional and is selected for buildings of five or more floors.

## Planning an assembly

```http
POST /api/v1/lego-assembly/plan
```

```json
{
  "target_width_m": 24,
  "target_depth_m": 18,
  "target_floors": 6,
  "archetype_id": "nordic-midrise",
  "reuse_keys": ["nordic-midrise", "contemporary", "mixed-use"]
}
```

The response contains the selected family, fit information and ordered module
instances with model URLs, positions and scales.

## Guardrails

The experimental planner rejects a family when fitting the podium would require
more than 20% scaling in either footprint dimension. This avoids the stretched
windows and doors that make generated assets look clunky.

## The Archetype Compiler (local module generation)

Modules no longer need to be authored by hand. One command generates a full
family from a real catalogue archetype, headlessly, in Blender:

```powershell
.\scripts\generate-archetype-family.ps1 -ArchetypeId "nordic_timber_midrise"
```

and one command registers it in the model library with all `metadata.lego`
fields filled in:

```powershell
python tools\archetype_compiler\import_manifest.py build\archetypes\nordic_timber_midrise --email ... --password ...
```

See `tools/archetype_compiler/README.md` (pipeline internals, coordinate
contract, catalogue→grammar mapping) and
`docs/GENERATE_YOUR_FIRST_ARCHETYPE_FAMILY.md` (step-by-step user guide).

## Persisted assembly recipes

Accepted assemblies are stored on the building without touching the
Meshy/Tripo `model_url` workflow, namespaced inside `Building.specifications`:

```json
{ "legoAssembly": { "schemaVersion": 1, "moduleFamily": "...", "instances": [], "target": {} } }
```

Endpoints: `POST/GET/DELETE /api/v1/lego-assembly/recipes/{building_id}`.
Clearing a recipe leaves every other specification field intact.

## Status (2026-07-13)

Done: compiler pipeline (export → grammar → Blender → validation), one-command
scripts, manifest import into the model library, composer reachable from the
zone panel, recipe persistence, tests (compiler unit + smoke, backend API,
frontend build/typecheck).

## Next steps

1. Geospatial placement of assembled recipes in the main Google Tiles scene.
2. Horizontal left/centre/right façade modules (corner conditions).
3. A worker that bakes accepted recipes into one optimized GLB and creates LODs.
4. Texture atlases / richer materials for the generated modules.
5. A small admin editor for module metadata and GLB dimensions.

## Asset authoring conventions

All modules should use metres, Y-up or Z-up consistently after normalization,
a documented front direction, a ground/base origin, and common floor heights
within a family. Revit-authored assets should pass through Blender for cleanup,
material consolidation, origin normalization and GLB export.

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

## Next steps

1. Wire `LegoAssemblyPreview` to `ZonePropertiesPanel.onOpenBlockEditor`.
2. Add a small admin editor for module metadata and GLB dimensions.
3. Add geospatial placement in the main Google Tiles scene.
4. Persist selected recipes against a building.
5. Add horizontal left/centre/right façade modules.
6. Add a worker that bakes accepted recipes into one optimized GLB and creates LODs.

## Asset authoring conventions

All modules should use metres, Y-up or Z-up consistently after normalization,
a documented front direction, a ground/base origin, and common floor heights
within a family. Revit-authored assets should pass through Blender for cleanup,
material consolidation, origin normalization and GLB export.

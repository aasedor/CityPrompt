# Park Meshy object pilot v1

This bounded pilot tests whether Meshy adds useful realism to an irregular
park object while the City Prompt LEGO grammar retains site composition,
metric scale and placement authority.

## Pilot object

- Family: `park_nature_play_v0`
- Archetype: `nature_play_area`
- Variant: `nature_play_area_v0` / Forest Adventure
- Object: `climbing-log-meshy-v1.glb`
- Catalogue references:
  - `frontend/public/archetypes/openspaces/nature-play-area/variant_0.png`
  - `frontend/public/archetypes/openspaces/nature-play-area/hero.png`
- People in the references informed scale only; no people or buildings are in
  the generated views or GLB.

## Result

Meshy successfully isolated one natural climbing log and generated three
consistent views with visible bark relief, end grain, moss, dirt and irregular
silhouette. The result is materially more convincing than a procedural
cylinder at close and middle park-view distances.

The paid two-stage run used 39 Meshy credits. Raw output was 11.1 MB with
24,914 faces and four 2K PBR images. Blender normalization produced:

- 4.20 m long by approximately 0.90 m diameter;
- ground-contact origin at Z=0;
- 12,000-face runtime topology;
- four 512 px PBR images;
- 1.42 MB runtime GLB;
- explicit `nature_play_climbing_log` placement role;
- no people and no large buildings.

The reviewed runtime GLB is intentionally added alongside the existing
metric `balance-log.glb`. The Meshy prop replaces one focal instance in the
Forest Adventure assembly; the remaining balance beams stay procedural and
dimension-controlled.

## Pipeline

1. Use one to five catalogue references only as visual guidance.
2. Ask Meshy Image-to-Image for three mutually consistent isolated views.
3. Feed that task directly to Multi-Image-to-3D with PBR and remeshing.
4. Keep raw and master assets outside Git.
5. Normalize dimensions, orientation, ground contact, topology and textures
   in Blender.
6. Promote only the mobile/runtime LOD into the archetype-owned kit.
7. Test one park at a time in City Prompt.

Reusable scripts:

- `tools/park_skin_compiler/generate_meshy_park_object_pilot.py`
- `tools/park_skin_compiler/normalize_and_render_meshy_park_asset.py`

## Validation

- GLB imported and re-exported successfully in Blender 5.1.2.
- Final dimensions: 4.2001 x 0.9003 x 0.9001 m.
- Final faces: 12,000.
- Focused frontend tests: 507 passed.
- TypeScript type-check: passed.
- Browser login was unavailable during the pilot, so a signed-in City Prompt
  screenshot remains the sole unfinished visual check before scaling beyond
  this one object.

See `comparison-sheet.png` for the catalogue, Meshy multiview and cleaned
runtime comparison.

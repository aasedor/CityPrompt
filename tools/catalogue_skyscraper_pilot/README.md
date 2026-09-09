# Source-locked tower batch

Three finite RLASM 6.1 architectural-clay candidates. These scripts create
external review packages, not live catalogue entries. They do not call paid
generation APIs, seed a database, grant approval, or push Git.

| Script | Exact parent / variant | Occupied levels | Nominal height |
| --- | --- | ---: | ---: |
| `build.py` | `glass_tower_podium_modern` / `glass_tower_blue_reflective` | 25 | 99 m |
| `vancouver.py` | `vancouverism_tower_podium` / `vancouverism_classic` | 16 | 58.8 m |
| `twisted.py` | `glass_tower_podium_modern` / `glass_tower_twisted` | 40 | 147.7 m |

Dimensions and floor counts are conceptual estimates from the locked images,
not surveys. The Vancouver option is a residential high-rise, shorter than the
two skyline towers. Unseen interiors and engineering are explicitly inferred.

## Build one candidate

Use Blender 5.1 in a separate background process for each script. They reuse
the established clay core's low-level construction/export routines and disable
per-component bevels locally; do not combine scripts in one persistent process.
Run the source/camera preflight before the corresponding build:

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe' -b `
  --python tools/catalogue_skyscraper_pilot/build.py -- `
  --source-root C:/Users/andre/OneDrive/Documents/CityPrompt `
  --output C:/dev-artifacts/CityPrompt/my-new-tower-version `
  --version 4 --resolution 1200 --dry-run
```

Remove `--dry-run` to build. Always use a new external output directory and
version. `vancouver.py` and `twisted.py` accept the same arguments. Source root
must contain the exact front, oblique and top files under the authoritative
`frontend/public/archetypes/buildings` folder; do not substitute sibling images.

The pipeline exports and reimports the exact texture-free GLB before rendering
every mandatory camera. It preserves source hashes, authoring scene, scripts,
opening audit, native bounds, mesh metrics and complete proof images.

```powershell
python tools/catalogue_foursquare_pilot/proof.py C:/dev-artifacts/CityPrompt/my-new-tower-version
```

This creates phone boards and deterministic verification once. A pass is not
independent visual approval. Review all full-resolution views and both phone
boards, then obtain the separate holistic review required by the RLASM method.

## Catalogue handoff

The 2026-09-08 evidence batch is external at
`C:/dev-artifacts/CityPrompt/skyscraper-trio-2026-09-08`. Its three staging
packages are `blue-promotion.json`, `vancouver-promotion.json` and
`twisted-promotion.json`. They retain empty human-approval and app-trial fields
until those actions actually occur. Follow `docs/BUILDING_CATALOGUE_WORKFLOW.md`
for local trial, exact-byte promotion and selective seeding.

Use `fixed_native` placement for all three: reshape the plot around the intact
building. Do not stretch the exported mesh or repeat floors. The existing
authored reference images remain the catalogue thumbnails; these clay QA
previews must not replace them.

The planned Art Deco alternative was deferred before geometry: its front and
oblique references depict incompatible shaft/crown proportions. The replacement
twisting tower has its own source lock and asymmetric five-sided plan.

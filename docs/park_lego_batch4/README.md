# Archetype-Owned Park LEGO — Batch 4

Batch 4 promotes ten catalog archetypes to deterministic Public Realm LEGO v0 programs. Generate to 3D uses the procedural surface and depth kits; it does not make an image-generation API call. People in the references are scale/use evidence only and are not generated. Large buildings remain the responsibility of building families.

| Archetype / exact variant | Spatial contract | Depth kit |
|---|---|---|
| Community Park / English Pastoral v0 | One whole 100 × 64 m recreation field, pond, serpentine loop, picnic/pavilion edge | Existing community modules; no field stretching |
| Pond / Lake / Naturalistic Pond v0 | One coherent basin, planted shelf, continuous dry loop, one dock | Timber viewing dock |
| Wetland / Rain Garden / Native Restoration v0 | Three connected treatment cells and exact looping boardwalk network | Boardwalk and overlooks |
| Japanese Garden / v0 | Koi pond, stroll loop, raked gravel and exact bridge alignment | Arched lacquer bridge |
| Botanical Garden / v0 | Connected interpretive loop, distinct collection beds and reserved conservatory pad | Compact glass conservatory |
| Urban Forest / Native Restoration v0 | 75–85% varied woodland canopy, one loop and two clearings | Layered canopy/understory; no cloned rows |
| Reservoir / Watershed Park / Concrete-Edge v0 | Rectangular impoundment, continuous shoreline path and short dam edge | Dam/spillway, fence and service/viewing edge |
| Amphitheater Lawn / Terraced Performance v0 | Four lawn terraces focused on one 18 × 8 m stage and upper rim path | Raised lawn-tier edges and timber stage |
| Riparian Buffer / Native Restoration v0 | Continuous creek, vegetated banks, parallel dry trail and one crossing | Small timber bridge |
| Adventure Playground / Rustic Timber v0 | Separate gravel/wood-fibre tower and swing safety rooms plus clear perimeter route | Rough timber towers, rope climbing, swings, split-rail fence and boulders |

## Skin method

`park_archetype_batch4_skin_sources.json` records the exact reference source and normalized crop for six material roles per archetype. The compiler samples reference color statistics, then synthesizes stationary repeatable paver, lawn, asphalt, planting, safety and timber structure. Source pixels are never projected onto site geometry. Each role produces base color, normal, roughness, ambient-occlusion and height maps plus a manifest. The complete batch makes zero paid API calls.

## Adaptation rules

- Whole metric facilities rotate or disappear; they never stretch, crop or overlap.
- Ecological water and planting forms adapt to irregular parcel residuals while preserving flow and access topology.
- Social infrastructure stays on the path, field or activity edge.
- Variant identity is exact. Community Park v1–v3 remain non-executable until individually reviewed rather than borrowing the v0 program.
- Preview remains a simple colored, labeled polygon. The detailed program appears only after Generate to 3D.

## Reproduction

```powershell
python tools/park_skin_compiler/generate_park_archetype_batch4_skins.py --dry-run
python tools/park_skin_compiler/generate_park_archetype_batch4_skins.py
python tools/park_skin_compiler/render_park_archetype_batch4_sheet.py
```

The review sheet is [park_lego_batch4_reference_skin_sheet.jpg](park_lego_batch4_reference_skin_sheet.jpg).

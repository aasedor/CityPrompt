# Meadow vegetation component kit — 2026-09-22

Follow-up: the [Currie site trial](MEADOW_VEGETATION_SITE_TRIAL_2026-09-22.md)
integrates this kit into exact meadow variant v2 and records two paid close-ups.
The component-only status below describes the earlier checkpoint.

Six reusable planting prototypes to accompany the timber-and-charcoal furniture.
Source base: `4f08f605e`, branch `codex/public-realm-visual-pilot`; the delivery
revision is the commit containing this report. Scope is component creation and
visual review, not a changed park archetype or global tree replacement.

## Components and measured default seed

| Kind | Height | Triangles | Reserved horizontal radius |
| --- | --- | --- | --- |
| Spreading shade tree | 7.20 m | 11,205 | 3.8 m |
| Pale-bark grove tree | 8.05 m | 11,277 | 2.2 m |
| Multi-stem ornamental | 4.75 m | 12,825 | 2.9 m |
| Silver-green shrub | 1.07 m | 3,204 | 0.85 m |
| Meadow grass | 1.19 m | 585 | 0.65 m |
| Flowering perennial | 0.70 m | 1,404 | 0.65 m |

Values measured from seed 17, geometry before uniform instance scaling. Maximum
heights and triangle budgets for the three tested seeds are declared in
`MEADOW_VEGETATION_SPECS`. These are visual types, not exact botanical specimens.

`createMeadowVegetation` builds visible tapered limbs, attached leafy sprays and
small folded leaves. No opaque crown shells, spherical canopy blobs, textures or
provider calls. The pale-bark tree has restrained bark markings; the lower kit
uses silvery foliage, seed heads and muted purple/cream flowers. The shade-tree
branches rise into a rounded crown instead of repeating horizontal tiers.

`GlobeMeadowVegetation` instances the bark/stem and foliage geometries separately
(two draws per type/seed), with stable seeded prototypes, uniform scale, yaw and
caller-supplied ground Z. Resources use the shared StrictMode-safe deferred
disposal helper; matrices update at layout time rather than per animation frame.
No district-scale FPS or memory benchmark has been performed.

## Verification and evidence

- Seven new vegetation tests pass: finite geometry, matching colour counts,
  envelope/height/triangle bounds for seeds 1, 17 and 91, and deterministic seed
  replay with different branching for another seed. Seven existing furniture
  geometry tests also passed; the final grass-only change reran all seven
  vegetation tests. TypeScript check passed.
- Initial tree meshes exceeded the 14,000-triangle limit; twig repetition was
  reduced and retested. The limit was not raised to accommodate the first build.
- Initial grass used a triangle spanning its bend, which produced an overly
  broad spear shape. It now uses a narrow segmented ribbon following the blade.
- Browser review at localhost:5176, 1264 × 625; no captured page errors in the
  component viewer. Actual generator output was inspected under neutral lighting,
  with the existing bench next to the trees at the same metre scale.
- Final external evidence:
  `C:/dev-artifacts/CityPrompt/sol-empty-lot-trial-2026-09-22/browser/81-meadow-trees.png`
  and `83-meadow-plants.png`. Earlier 80/82 images are intermediate checks.
- Review generators remain in ignored `artifacts/meadow-tree-review.html` and
  `artifacts/meadow-plant-review.html`. Temporary frontend review pages were
  removed after inspection. Images are local evidence, not committed assets or
  a durable shared evidence package.

## Integration status and next bounded step

Component dimensions and isolated appearance: agent-reviewed PASS. Independent
human visual approval remains open. No park picker entries, saved IDs, current
trees, scatter recipes or terrain policy changed in this batch. These components
are not yet student-placeable items.

For each future consuming park, complete the exact-variant runtime template:
reserve the declared complete canopy envelope, choose count/seed/yaw deliberately,
use current shared ground, preserve access/paving clearances, and verify Currie
close/aerial views plus edit/Undo/reload/capture. Do not use a narrow trunk disc
as proof that the crown clears a building or that foliage will not obscure an
entrance. Natural terrain, site integration, export and novice use are NOT TESTED
for this set. Existing-site download verification remains a separate open item
from the previous furniture checkpoint.

Next: review this set, then place a bounded selection in one disposable Currie
park using its authoritative terrain/clearance system, before wider substitution.

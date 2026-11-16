# Local prairie foliage, second batch: 40 more plants and seasonal forms

> **Update, same day.** A [third batch](LOCAL_DETAILS_BATCH3_2026-11-16.md) added 15 more
> seasonal forms, including winter and autumn shrubs, taking the kit to 85 plants.
> The 70 models described here are byte-identical.

## Scope

Extend the first 30 Calgary and Alberta plants in **Add details**
([first batch](LOCAL_FOLIAGE_DETAILS_2026-11-14.md)) with 40 more from the same
Blender-free generator and kit folder (`prairie-foliage-v1`, IDs prefixed
`detail-prairie-`):

- **8 trees** still missing from Calgary streets, yards and river valleys;
- **4 seasonal colour forms**: autumn aspen and larch, snow-laden spruces;
- **17 bare winter trees**, one for every deciduous tree in the kit;
- **11 native wildflowers and grasses**, each a small drift about a metre across.

Trees join **Trees** (`kind: tree`); the rest join **Planting** (`kind: object`).
The kit now holds 70 plants: 44 trees and 26 planting items. Species are visual
types for site visualization, not botanical specimens or planting advice, and
nothing here changes shared landscape stands, park scatter or archetype trees.

## New choices

| Item | W × D × H (m) | Triangles | Bytes |
|---|---:|---:|---:|
| Plains cottonwood | 12.4 × 12.3 × 20.4 | 12,606 | 1,439,136 |
| Brandon elm | 10.9 × 8.9 × 13.4 | 12,558 | 1,433,648 |
| Littleleaf linden | 7.1 × 7.1 × 11.8 | 11,808 | 1,348,176 |
| Flowering crabapple | 5.0 × 5.0 × 6.0 | 13,048 | 1,489,536 |
| Japanese tree lilac | 5.1 × 5.3 × 8.4 | 12,396 | 1,415,204 |
| Scots pine | 8.1 × 8.2 × 12.2 | 10,776 | 1,230,468 |
| Douglas fir | 7.1 × 6.7 × 18.2 | 11,946 | 1,363,856 |
| Limber pine | 5.0 × 5.4 × 6.8 | 9,992 | 1,141,108 |
| Trembling aspen · autumn | 4.8 × 4.8 × 11.6 | 11,236 | 1,282,980 |
| Siberian larch · autumn | 4.5 × 4.6 × 13.2 | 10,832 | 1,236,908 |
| White spruce · snow | 5.4 × 5.0 × 14.2 | 13,296 | 1,517,788 |
| Colorado blue spruce · snow | 5.0 × 4.8 × 10.7 | 11,946 | 1,363,920 |
| Bearberry | 1.2 × 1.2 × 0.1 | 4,862 | 556,288 |
| Prairie crocus | 0.9 × 0.9 × 0.2 | 840 | 97,788 |
| Blanketflower | 1.1 × 1.2 × 0.7 | 1,773 | 204,144 |
| Wild bergamot | 1.0 × 1.2 × 1.0 | 1,336 | 154,324 |
| Fireweed | 1.0 × 1.2 × 1.6 | 1,488 | 171,628 |
| Canada goldenrod | 1.1 × 1.3 × 1.1 | 1,920 | 220,884 |
| Prairie smoke | 1.0 × 0.9 × 0.4 | 1,582 | 182,380 |
| Wild blue flax | 1.1 × 1.2 × 0.7 | 3,264 | 374,132 |
| Pasture sage | 0.9 × 0.8 × 0.4 | 2,985 | 342,320 |
| Blue grama | 1.2 × 1.0 × 0.5 | 1,386 | 160,004 |
| June grass | 1.1 × 1.0 × 0.6 | 2,583 | 296,468 |

**Winter forms** (label suffix `· winter`, 6,191 to 9,973 triangles, 16.0 MB
together): trembling aspen, Swedish columnar aspen, balsam poplar, paper birch,
green ash, bur oak, Manitoba maple, laurel leaf willow, Schubert chokecherry,
showy mountain ash, Amur cherry, plains cottonwood, Brandon elm, littleleaf
linden, flowering crabapple, Japanese tree lilac and Siberian larch.

Searching the panel for `winter`, `autumn` or `snow` lists the seasonal forms.

## Method

Seasonal forms are not separate trees. Each shares its base species' seed and
random sequence, so the trunk and every limb are identical and a student can
swap a summer aspen for its winter form without the tree changing shape:

- **Autumn** swaps the leaf or needle palette only.
- **Snow** replaces about half the needle tufts with tilted white slabs.
- **Winter** drops each leaf to one fine twiglet sliver and each needle tuft to
  a short spur, drawn in a dark twig colour. Fruit that really persists stays:
  mountain ash berries, crabapples and lilac seed heads.

Seasonal choices draw from a second random stream, which is why the summer
models are untouched. The generator also gained a limber pine builder
(twisting multi-stem trunks, limbs swept leeward), a two-tone Scots pine trunk,
bark furrows and lenticels, blossom accents, a trailing mat builder, a
flowering-drift builder with eight head types (crocus cup, daisy, pom, spire,
plume, nodding smoke, flax, sage) and eyelash and spike grass heads.

**The first 30 models are byte-identical.** The tools test now pins their 30
SHA-256 values, so no later change to shared code can alter a shipped model
unnoticed.

**Placement anchor corrected for all 70.** The first batch followed the older
kit habit of re-centring each model on its bounding box, which put a trunk up
to 0.44 m from the clicked point (balsam poplar). Registry offsets now only
ground the model, so the trunk or clump centre lands exactly where the student
clicks, which matters in a 1.5 m tree well or boulevard strip. Only the 30
registry offset values changed; no model file did. Nothing had been merged or
placed, so no saved project moves.

The 40 new GLBs total 35,071,428 bytes and 307,029 triangles; the whole kit is
62,342,176 bytes. Budgets are unchanged (trees under 14,000 triangles, planting
under 6,000, two meshes, no textures). Models still load only on placement.

## Picker card images

With 53 choices under Trees, drawing each card from its model would download
about a megabyte per tile. Every plant in the kit, including the first 30, now
has a static 480 × 315 WebP card (`<slug>.webp` beside the GLB, about 7 KB each,
784 KB for both local kits together). The registry records it as `thumbnailUrl`,
which the panel already prefers over a live render.
`render_detail_thumbnails.cjs` draws the cards with the same lighting and
orthographic framing as `detailThumbnail.ts`, so they look like the live preview
they replace. Pixels depend on the renderer, so the cards are reviewed outputs
locked by hash; tests verify the committed bytes and never re-render. The
hashes live in `tools/detail_catalogue/detail_card_images.lock.json`, not in the
registry rows, because every row ships inside the JavaScript bundle and the
running app never reads an image hash.

## Bundle budget

Catalogue rows are compressed into the production bundle, and CI holds total
JavaScript to 8,448 KB. The branch base had under 5 KB to spare, so the 108 new
rows put the first build 21.5 KB over. This was caught by running the production
build and `check-budget` locally; it would have failed CI.

The budget was not raised and no catalogue field was dropped. Following the
repository's existing practice, seven catalogues moved from base64 to the
denser Z85 transport the packing plugin already supports for the three largest:
`detailCatalogueExtras`, `recoveredDetails`, `streetPathArchetypes`,
`nativeParks`, `cataloguePlanningHistory`, `catalogueTeaching` and
`archetypeReferenceAvailability`. Z85 is lossless; the plugin tests decode each
one after minification and require it to equal the source exactly, including
signed-zero offsets. Together with keeping card hashes out of the rows, total
JavaScript is 8,441.7 KB, which leaves slightly more headroom than before.

## Reproduction

```text
python tools/detail_catalogue/build_local_foliage.py --dry-run
python tools/detail_catalogue/build_local_foliage.py --output <fresh-directory> [--id fireweed ...]
node tools/detail_catalogue/render_detail_thumbnails.cjs <directory>
python tools/detail_catalogue/build_local_foliage.py --output <directory> --attach-thumbnails
python tools/detail_catalogue/build_local_foliage.py --output <directory> --register
python -m pytest tools/detail_catalogue/test_local_foliage.py -q
```

The thumbnail step needs the repository root served on port 8765 and frontend
dependencies installed, like the review page.

`--register` is still a text-level splice before the closing bracket of
`detailCatalogueExtras.json` and refuses IDs already present; backups are now
written as `.bak-detail-register`. For this batch the 30 earlier rows were first
removed, with the remaining 155 rows verified byte-for-byte against
`origin/deployment-version`, and all 70 were registered in catalogue order.

## Verification

- Dry run: 70 species, zero paid calls, no Blender.
- Review passes at eye level, oblique and catalogue-card framing. Tuned after the
  first pass: Brandon elm (now a clear-trunked vase), crabapple and tree lilac
  bloom, Scots pine limb colour and density, limber pine fullness, snow that
  reads from the side, a filled bearberry mat and a less chalky pasture sage.
  Final sheets: [trees and seasonal forms](prairie-foliage-v1/second-batch-trees.jpg),
  [wildflowers and grasses](prairie-foliage-v1/second-batch-plants.jpg),
  [catalogue cards](prairie-foliage-v1/second-batch-cards.jpg). Agent review
  passed; independent human visual acceptance is open.
- Tools pytest: 10 tests. It rebuilds all 70 and requires byte-identical
  registry rows, the 30 pinned first-batch hashes, identical skeletons for every
  seasonal form, origin-anchored offsets, trunks standing on the anchor and a
  hash-locked card image for every row.
- `npx vitest run src/features/parks` plus the people catalogue test: 42 files,
  237 tests passed with archive-backed assets materialized as CI does.
  TypeScript and ESLint on the changed test pass.
- Backend `tests/test_project_details.py`: 83 passed, including the mirror and
  round-trip of all 225 extras; the one failure is the pre-existing traffic-safety
  hash test that needs hydrated LFS models.
- Runtime asset manifest regenerated and checked: 5,579 required files (+40)
  at the model commit, then 5,725 once both local kits gained card images.
- Production build and `check-budget` pass at 8,441.7 KB of 8,448 KB total
  JavaScript. The 128 catalogue delivery guard tests pass, including eight new
  ones for the denser transport.

Not done here: a browser trial placing these plants in a project, Undo/reload,
deterministic capture, low-end device performance and classroom novice use.

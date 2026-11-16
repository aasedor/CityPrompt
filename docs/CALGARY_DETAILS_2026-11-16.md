# Calgary site details for Add details: 38 local objects and two new categories

> **Update, same day.** The kit grew to 76 objects in a
> [second batch of everyday street, lane and yard items](CALGARY_EVERYDAY_DETAILS_2026-11-16.md).
> The 38 models below are byte-identical and pinned by digest in the tools test.
> Winter city now has 12 items. That write-up also records a release-tooling
> defect in how picker card hashes were read, present on this branch until then,
> and the current bundle-budget position.

## Scope

Add 38 fixed-size objects that make a scene read as Calgary: a winter city set,
back-lane and yard items, foothills stone and ranch pieces, pathway and transit
furniture, and four local animals. They come from a new Blender-free builder in
the same kit convention as the [prairie foliage](LOCAL_FOLIAGE_SEASONS_2026-11-16.md).
Catalogue IDs use the `detail-yyc-` prefix and the kit folder is
`frontend/public/park-kits/calgary-details-v1/`. The plainer `detail-calgary-`
prefix already belongs to the traffic-safety concept family, and IDs are saved
in student projects, so the two families are kept distinct by prefix.

Two categories are new and have their own tiles in the panel: **Winter city**
(9 items) and **Wildlife** (4). The other 25 items join existing categories.
All are `kind: object`, saved in project `props`.

These are generic concept models for site visualization. They carry **no City
of Calgary or Calgary Transit branding**, no wording, and reproduce no specific
landmark or artwork. They are not construction, electrical, traffic-control,
play-safety or rink designs. Indigenous cultural items were deliberately left
out; those should come from consultation with Treaty 7 nations.

## New choices

| Item | Category | W × D × H (m) | Triangles |
|---|---|---:|---:|
| Community outdoor rink | Winter city | 31.6 × 18.5 × 1.3 | 2,900 |
| Rink board section | Winter city | 4.1 × 0.8 × 1.1 | 102 |
| Hockey net | Winter city | 1.9 × 1.2 × 1.2 | 454 |
| Skaters' warming hut | Winter city | 5.1 × 4.8 × 3.8 | 2,796 |
| Fire pit circle | Winter city | 5.4 × 5.4 × 0.7 | 1,593 |
| Snow fence | Winter city | 4.8 × 0.1 × 1.5 | 300 |
| Snow windrow | Winter city | 6.5 × 2.7 × 1.1 | 648 |
| Sanding grit box | Winter city | 1.3 × 0.9 × 1.0 | 116 |
| Parking plug-in posts | Winter city | 5.6 × 1.2 × 1.2 | 368 |
| Black garbage cart | Street furniture | 0.7 × 0.9 × 1.1 | 432 |
| Blue recycling cart | Street furniture | 0.7 × 0.9 × 1.1 | 432 |
| Green compost cart | Street furniture | 0.7 × 0.9 × 1.1 | 432 |
| Three-cart set | Street furniture | 2.1 × 0.9 × 1.1 | 1,296 |
| Wooden utility pole | Street furniture | 0.6 × 3.6 × 10.4 | 934 |
| Utility pole with lines | Street furniture | 30.0 × 3.6 × 10.4 | 1,366 |
| Wood privacy fence | Edges & gates | 2.6 × 0.1 × 2.0 | 288 |
| Chain-link fence | Edges & gates | 3.1 × 0.1 × 1.3 | 396 |
| Garden shed | Garden & growing | 3.4 × 3.3 × 3.0 | 504 |
| Backyard trampoline | Play | 4.5 × 4.7 × 2.8 | 2,588 |
| Little free library | Street furniture | 0.6 × 0.5 × 1.9 | 518 |
| Driveway hockey net | Play | 2.6 × 2.0 × 1.1 | 596 |
| Sandstone block group | Landscape | 3.0 × 2.2 × 0.9 | 210 |
| Sandstone seat wall | Seating | 3.6 × 0.6 × 0.5 | 300 |
| Rundle rock wall | Edges & gates | 3.0 × 0.6 × 0.9 | 1,104 |
| Glacial erratic | Landscape | 5.1 × 3.9 × 2.3 | 384 |
| Round hay bale | Landscape | 1.2 × 1.5 × 1.5 | 528 |
| Ranch rail fence | Edges & gates | 5.0 × 0.2 × 1.4 | 288 |
| Ranch entry gate | Edges & gates | 6.5 × 1.5 × 4.7 | 732 |
| River pathway marker | Street furniture | 0.4 × 0.4 × 1.4 | 206 |
| River safety ring station | Street furniture | 0.6 × 0.4 × 2.1 | 840 |
| Light-rail platform shelter | Shelters & markets | 10.0 × 4.2 × 3.4 | 1,052 |
| Light-rail catenary pole | Street furniture | 40.0 × 3.1 × 7.8 | 720 |
| Heated bus shelter | Shelters & markets | 7.1 × 2.6 × 2.7 | 620 |
| E-scooter parking corral | Street furniture | 4.0 × 1.7 × 2.3 | 1,410 |
| White-tailed jackrabbit | Wildlife | 0.3 × 0.6 × 0.6 | 642 |
| Black-billed magpies (pair) | Wildlife | 0.8 × 0.6 × 0.2 | 640 |
| Canada geese (pair) | Wildlife | 1.4 × 1.1 × 0.9 | 648 |
| Mule deer | Wildlife | 0.4 × 1.6 × 1.6 | 1,032 |

**Repeatable sections** (fences, boards, walls) are sized to butt end to end.
**Line carriers** are centred on their pole so they chain: place a utility pole
with lines every 30 m and a catenary pole every 40 m, and the wires meet at
mid-span. The plain utility pole ends a run.

## Method and assets

`tools/detail_catalogue/calgary_kit.py` holds the primitives: boxes, tapered
cylinders, prisms, lofts, tori, domes, flat ribbons, netting, chain-link
diagonals, hanging wires and an angular rock made by clipping a box with random
planes. `tools/detail_catalogue/build_calgary_details.py` holds one small
function per object and reuses the foliage GLB writer, so the files share the
kit format: linear vertex colours, flat normals, no textures, extensions or node
transforms. Each object is one matte mesh, and seven also carry a second
smoother mesh for glass and ice, which stays opaque like the existing shelters.

The animals are static low-poly forms lofted along a spine with colour by
region. They were piloted before the set was kept: the hare, magpies, geese and
doe all read clearly in catalogue-card and eye-level views. They do not move.

The 38 GLBs total 3,518,596 bytes and 30,415 triangles; the largest is the rink
at 2,900 triangles and 332,656 bytes. Models load on placement only. The
authored ground origin is the placement anchor, as with the plants.

## Picker card images

Every item ships a static 480 × 315 WebP card beside its GLB, recorded as
`thumbnailUrl` and hash-locked in `tools/detail_catalogue/detail_card_images.lock.json`,
so browsing the panel never downloads a model. The cards use the same lighting and framing as the live
preview. The two 30 m and 40 m line carriers would otherwise shrink to a hairline
in a card, so their images frame the pole and the nearest few metres of wire.
See the [foliage write-up](LOCAL_FOLIAGE_SEASONS_2026-11-16.md) for the method
and for how the 108 new rows were fitted inside the JavaScript bundle budget.

## Reproduction

```text
python tools/detail_catalogue/build_calgary_details.py --dry-run
python tools/detail_catalogue/build_calgary_details.py --output <fresh-directory> [--id outdoor-rink ...]
node tools/detail_catalogue/render_detail_thumbnails.cjs <directory> utility-pole-lines:3.2,lrt-catenary-pole:4.2
python tools/detail_catalogue/build_calgary_details.py --output <directory> --attach-thumbnails
python tools/detail_catalogue/build_calgary_details.py --output <directory> --register
python -m pytest tools/detail_catalogue/test_calgary_details.py -q
```

Review with the shared page: serve the repository root, then
`node tools/detail_catalogue/review_local_foliage.cjs "dir=<output>&mode=mix" <png>`.
Add `zoom=3` to bring the camera in on the two long wire items.

## Verification

- Dry run: 38 items, zero paid calls, no Blender.
- Every item was rendered at eye level, oblique and catalogue-card framing and
  reviewed. Fixed after review: fire pit gravel tone, hay bale banding, fence
  board contrast, hockey stick placement, and a scooter lean that rotated about
  the wrong axis and sank the wheels, which the ground-datum test caught. Final
  sheets: [eye level](calgary-details-v1/eye-level.jpg),
  [oblique](calgary-details-v1/oblique.jpg),
  [catalogue cards](calgary-details-v1/catalogue-cards.jpg). Agent review passed;
  independent human visual acceptance is open.
- Tools pytest for this kit: 7 tests rebuild all 38 and require byte-identical
  registry rows, budgets, the kit material convention, ground-datum and anchor
  rules, chaining spans, backend allowlist, category tiles, unbranded wording
  and a hash-locked card image for every row.
- `npx vitest run src/features/parks` plus the people catalogue test: 42 files,
  239 tests passed with archive-backed assets materialized as CI does. The
  panel test walks every category tile, including the two new ones. TypeScript,
  ESLint on changed files, `check:catalogue-json` and the 120 catalogue delivery
  guard tests pass.
- Backend `tests/test_project_details.py`: 83 passed, including the mirror and
  round-trip of all 263 extras; the one failure is the pre-existing
  traffic-safety hash test that needs hydrated LFS models.
- Runtime asset manifest regenerated and checked: 5,617 required files (+38)
  at the model commit, then 5,725 once both local kits gained card images.
- Production build and `check-budget` pass at 8,441.7 KB of 8,448 KB.

### App code path, without the globe

The full app could not be started in the build sandbox, which has no map key or
database. Instead a temporary page served by the project's own Vite config
imported the real `detailCatalogue.ts`, `detailThumbnail.ts` and
`detailInstances.ts` and ran all 108 local models (both kits) through them in
headless Chromium:

- every model resolves by ID and by label search inside its category;
- `detailThumbnail` returns the static card without loading a model, and each
  card decodes at 480 × 315;
- every GLB loads with the app's three.js loader and `buildDetailInstances`
  yields the registered mesh count, vertex-coloured double-sided materials with
  no textures or transparency, and one instance per placement;
- after `detailPlacementMatrix`, every model's base sits on the 0.084 m detail
  datum within 0.001 mm, its size matches the registry within 0.5 mm, the
  anchor lies inside the footprint, and a quarter turn pivots on the anchor.

108 of 108 passed with no page or console errors. Three composed scenes went
through the same instancing path:
[winter lane at eye level](calgary-details-v1/scene-winter-lane.jpg),
[winter aerial](calgary-details-v1/scene-winter-aerial.jpg) and
[summer aerial](calgary-details-v1/scene-summer-aerial.jpg). The utility lines
join across three poles placed 30 m apart. The harness was not committed.

### The real project page, with a mocked backend

The project's own browser tests start the real app against mocked APIs, so the
same setup was used for a temporary trial of **Add details** in a real project
page (the 13 existing browser tests also pass in this sandbox):

- the category screen shows the new **Winter city** and **Wildlife** tiles with
  their item counts ([screenshot](calgary-details-v1/app-category-tiles.jpg));
- every card in [Winter city](calgary-details-v1/app-winter-city.jpg) (9) and
  [Wildlife](calgary-details-v1/app-wildlife.jpg) (4), and all 26 local cards in
  Planting and 44 in Trees, loads from its static image at 480 × 315;
- browsing those four categories requested **zero** local model files;
- searching `winter` finds 17 items inside Trees and 27 across all categories;
- choosing the community rink [arms placement](calgary-details-v1/app-placing.jpg).

The map area itself shows "Missing VITE_GOOGLE_MAPS_API_KEY" in this setup, so
clicking the map to place, saving, Undo/reload and capture were not exercised.
The one logged browser error was an older item's model that is not hydrated in
the sandbox. The trial spec was not committed.

After seeing the cards at true size, the rink ice and the snow windrow were
re-toned slightly bluer so they read against the pale card.

Not done here: placing these objects on the live map with a real map key,
Undo/reload, deterministic capture and AI render with them, low-end device
performance and classroom novice use.

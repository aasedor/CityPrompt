# Local prairie foliage for Add details: 30 Calgary and Alberta plants

> **Update 2026-11-16.** The kit grew to 70 plants in a
> [second batch](LOCAL_FOLIAGE_SEASONS_2026-11-16.md). The 30 models below are
> byte-identical and their hashes are now pinned in the tools test. Two details
> on this page changed: registry offsets no longer re-centre a model on its
> bounding box, so the trunk lands on the clicked point, and `--register` writes
> its backups as `.bak-detail-register`.

## Scope

Add 30 fixed-size plants to the **Add details** catalogue so students can place
the trees, shrubs, hedges and grasses they actually see in Calgary instead of
the generic oak, shade tree and cherry models. Fifteen trees join the **Trees**
category (`kind: tree`, saved in project `trees`); fifteen shrubs, hedges,
ground covers and grasses join **Planting** (`kind: object`, saved in `props`).
Catalogue IDs use the `detail-prairie-` prefix and the kit folder is
`frontend/public/park-kits/prairie-foliage-v1/`.

Species are visual types at hardiness zone 3-4 for site visualization. They are
not botanical specimens, growth models, planting advice or a replacement for
the shared landscape tree stand, park scatter recipes or archetype-owned trees.
No embedded archetype objects, building families or existing details change.

## New choices

| Item | Kind | W × D × H (m) | Triangles | Bytes |
|---|---|---:|---:|---:|
| Trembling aspen | Tree | 4.8 × 4.8 × 11.6 | 11,236 | 1,282,952 |
| Swedish columnar aspen | Tree | 2.4 × 2.4 × 10.7 | 9,740 | 1,112,440 |
| Balsam poplar | Tree | 9.4 × 8.0 × 17.4 | 13,248 | 1,512,312 |
| Paper birch | Tree | 4.5 × 4.7 × 10.5 | 13,788 | 1,573,868 |
| Green ash | Tree | 7.7 × 8.8 × 12.7 | 13,248 | 1,512,296 |
| Bur oak | Tree | 9.3 × 9.4 × 11.1 | 12,462 | 1,422,688 |
| Manitoba maple | Tree | 7.8 × 7.7 × 10.8 | 13,920 | 1,588,928 |
| Laurel leaf willow | Tree | 10.3 × 10.4 × 12.9 | 13,248 | 1,512,332 |
| Schubert chokecherry | Tree | 4.4 × 4.0 × 6.6 | 10,398 | 1,187,440 |
| Showy mountain ash | Tree | 4.1 × 4.1 × 7.3 | 12,218 | 1,394,916 |
| Amur cherry | Tree | 3.8 × 3.9 × 7.0 | 13,194 | 1,506,152 |
| White spruce | Tree | 5.3 × 5.0 × 14.2 | 13,296 | 1,517,768 |
| Colorado blue spruce | Tree | 5.0 × 4.8 × 10.7 | 11,946 | 1,363,900 |
| Lodgepole pine | Tree | 5.5 × 5.5 × 15.2 | 11,582 | 1,322,360 |
| Siberian larch | Tree | 4.5 × 4.6 × 13.2 | 10,832 | 1,236,880 |
| Saskatoon berry | Planting | 2.3 × 2.2 × 2.6 | 3,288 | 376,844 |
| Wolf willow | Planting | 1.8 × 1.7 × 2.1 | 3,690 | 422,680 |
| Common lilac | Planting | 3.1 × 2.7 × 3.3 | 5,544 | 634,048 |
| Caragana hedge (2 m section) | Planting | 3.0 × 1.2 × 2.0 | 4,836 | 553,340 |
| Cotoneaster hedge (2 m clipped section) | Planting | 2.2 × 0.9 × 1.2 | 2,945 | 337,768 |
| Prickly wild rose | Planting | 1.6 × 1.5 × 1.0 | 3,740 | 428,400 |
| Common snowberry | Planting | 1.6 × 1.6 × 1.0 | 4,500 | 515,016 |
| Shrubby cinquefoil | Planting | 1.4 × 1.2 × 0.8 | 5,188 | 593,488 |
| Canada buffaloberry | Planting | 2.1 × 1.9 × 1.8 | 4,076 | 466,692 |
| Highbush cranberry | Planting | 2.8 × 2.6 × 2.8 | 3,936 | 450,752 |
| Diabolo ninebark | Planting | 2.3 × 2.3 × 1.9 | 3,920 | 448,924 |
| Mugo pine | Planting | 2.4 × 2.4 × 1.3 | 2,992 | 343,096 |
| Creeping juniper | Planting | 2.1 × 2.1 × 0.4 | 3,168 | 363,196 |
| Feather reed grass | Planting | 1.0 × 1.0 × 1.4 | 1,530 | 176,444 |
| Rough fescue drift | Planting | 1.5 × 1.5 × 0.7 | 972 | 112,828 |

Descriptions carry the Latin name and searchable words (Alberta, Calgary,
native, hedge, evergreen, berries) so the panel's search box finds them. The
red-osier dogwood, water sedge and American elm from the recovered batch remain
as they were; the held white spruce and balsam fir exports are not reused.

## Method and assets

`tools/detail_catalogue/build_local_foliage.py` is a Blender-free, deterministic
Python generator (numpy only). It follows the accepted meadow-kit recipe rather
than the rejected rounded photographic crowns: tapered trunks and limbs, attached
leafy sprays, small folded leaf tufts with gaps through the crown, branch tiers
with needle tufts for conifers, and vertex-colour accents for flowers, berries,
panicles, plumes, birch lenticels and aspen knots. Every GLB uses the kit
convention already served from `street-kits/pilots` and `standalone-details-v2`:
POSITION/NORMAL/COLOR_0 linear vertex colours, one double-sided roughness-0.9
material, flat normals, no textures, extensions or node transforms, and two
meshes (wood and foliage) so the shared instanced-copy renderer draws at most
two batches per species. Geometry is authored Z-up and written Y-up; the trunk
or clump centre sits at the origin on the ground, and registry offsets are
measured from actual bounds like earlier batches.

The 30 GLBs total 27,270,748 bytes and 238,681 triangles. Trees stay under
14,000 triangles and shrubs under 6,000, matching the meadow kit budgets; the
largest file is 1,588,928 bytes. Models load on placement only; the catalogue
renders cards from the GLB on demand like the standalone batch, so no thumbnail
images are shipped. Files are intentional Git LFS deliverables and the runtime
asset manifest records all 30. The backend allowlist mirrors every ID by kind.
No provider calls, Blender, textures or animations were used.

## Reproduction

```text
python tools/detail_catalogue/build_local_foliage.py --dry-run
python tools/detail_catalogue/build_local_foliage.py --output <fresh-directory> [--id white-spruce ...]
python tools/detail_catalogue/build_local_foliage.py --output <directory> --register
python -m pytest tools/detail_catalogue/test_local_foliage.py -q
```

The builder refuses an existing output directory and `--register` refuses IDs
already present. Registration is a text-level splice before the closing bracket
of `detailCatalogueExtras.json` after writing `.bak-prairie-foliage` backups; the
backend allowlist is appended in place. The pytest rebuilds all 30 species in
memory and requires byte-identical SHA-256, size, dimension, offset, triangle
and mesh values against the committed registry, so a tuning change that is not
re-registered fails CI-free locally in under two seconds.

For visual review serve the repository root
(`python -m http.server 8765 --bind 127.0.0.1`, with frontend dependencies
installed) and run `node tools/detail_catalogue/review_local_foliage.cjs
"dir=<output-directory>&mode=eye" <png>`; modes `oblique` and `card` give the
45° view and the app's catalogue-card framing.

## Verification

- Dry run: exactly 30 species, zero paid calls, no Blender.
- Two review passes before the final build: the first pass read too sparse and
  the mugo pine read as broad leaves; density, spray count, tuft size and
  needle shape were tuned, then every species was re-rendered at eye level,
  oblique and card framing. Final sheets:
  [eye level](prairie-foliage-v1/eye-level.jpg),
  [oblique](prairie-foliage-v1/oblique.jpg) and
  [catalogue cards](prairie-foliage-v1/catalogue-cards.jpg). Agent review of
  the generated models passed; independent human visual acceptance is open.
- Served GLB bytes under `frontend/public/park-kits/prairie-foliage-v1` match
  the registry hashes; the tools pytest (6 tests, 60 subtests) passes.
- `npx vitest run src/features/parks` and the people catalogue test pass except
  the pre-existing sandy-beach LFS hydration tests, which fail identically
  without this change in an unhydrated checkout. TypeScript, ESLint on the
  changed test, `check:catalogue-json` and the 120 catalogue delivery guard
  tests pass.
- Backend `tests/test_project_details.py`: 83 passed, including the frontend
  mirror and round-trip checks for all 185 extras; the one failure is the
  pre-existing traffic-safety hash test that needs hydrated LFS models.
- `node scripts/generate-runtime-asset-manifest.mjs --check` passes after
  regeneration (5,539 required runtime files, +30).

Not done here: a browser trial placing these items in a project, Undo/reload of
placed foliage, deterministic capture with the new models, low-end device
performance and classroom novice use. These remain the usual per-batch runtime
checks before classroom activation. Generated review PNGs, intermediate batches
and the local review server stay outside Git under `artifacts/`.

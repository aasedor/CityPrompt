# Local details, third batch: 44 more objects, animals and seasonal plants

## Scope

Add 44 fixed-size items to **Add details** in six sets, all from the two
existing Blender-free builders and kit folders:

- **Buses and trains** (4): city bus, light-rail car, school bus, snow plow truck.
- **Construction site kit** (6): roll-off bin, site office trailer, excavator,
  skid-steer loader, lumber and sheet goods, concrete barrier.
- **River and city edge** (6): inflatable raft, canoe, drift boat, pumpjack,
  grain bins, wind turbine.
- **Street and yard basics** (6): roadway street light, lamp post with flower
  baskets, flagpole, lane garage, carport, ground solar array.
- **Wildlife and ranch animals** (7): Richardson's ground squirrels, coyote,
  mallards, American white pelicans, osprey nesting platform, horses, cattle.
- **Seasonal plants** (15): six more autumn trees, winter forms for six shrubs
  and hedges, two autumn shrubs and a red-stemmed winter dogwood.

The 29 objects and animals extend `calgary-details-v1` (now 105, IDs prefixed
`detail-yyc-`). The 15 plants extend `prairie-foliage-v1` (now 85, IDs prefixed
`detail-prairie-`). No category is new. Earlier write-ups:
[first Calgary batch](CALGARY_DETAILS_2026-11-16.md),
[everyday batch](CALGARY_EVERYDAY_DETAILS_2026-11-16.md),
[plants and seasons](LOCAL_FOLIAGE_SEASONS_2026-11-16.md).

The same limits apply. Everything is a generic concept model with no agency,
utility, retail or postal branding and no wording. Vehicle liveries are
invented. The flag is plain with no emblem. Animals are static. None of this is
a traffic, construction, electrical or structural design.

## Duplicate scan before building

The proposal was checked against every existing asset first, not only the Add
details list:

- 3,350 catalogue-like rows across 31 data files, which covers Add details,
  the recovered details, vehicles, people, safety items and the building,
  street and park archetype catalogues;
- 1,033 tracked model files under `frontend/public`, listed kit by kit.

Each planned item was searched by several words. Most hits were archetype
names, such as a bus corridor street or a boathouse park, rather than something
a student can place. What changed as a result:

- **Dropped: blank notice board.** A community noticeboard already exists.
- **Dropped: red barn.** Farm and barn buildings belong in the building
  catalogue, which has its own construction method, and it already holds
  farmstead and barn types.
- **Kept, with a narrower form: red-osier dogwood.** A summer dogwood already
  exists among the recovered details, so only the winter form was added.
- **Kept: light-rail car.** A metro train exists inside the elevated-rail
  street, but nothing rail can be placed on its own.
- **Kept: street light.** Pedestrian lamps and lanterns exist; a tall roadway
  davit light does not.
- **Kept: lane garage and carport.** They are props like the garden shed, not
  building families, and the building catalogue's laneway suite and garden
  studio are dwellings.
- **Kept: snow plow truck.** A small municipal tipper exists, without a plow.

Nothing else overlapped: there was no bus, construction equipment, boat, farm
or energy structure, solar array, flagpole or animal other than the first four
and a guide dog in the people set.

## New objects and animals

| Item | Category | W × D × H (m) | Triangles |
|---|---|---:|---:|
| City bus | Vehicles | 3.1 × 12.6 × 3.3 | 1,156 |
| Light-rail car | Vehicles | 2.7 × 25.5 × 5.5 | 1,400 |
| School bus | Vehicles | 2.7 × 11.4 × 3.1 | 1,304 |
| Snow plow truck | Vehicles | 3.4 × 11.8 × 3.3 | 1,476 |
| Roll-off construction bin | Traffic & safety | 6.8 × 2.8 × 2.0 | 714 |
| Site office trailer | Traffic & safety | 8.8 × 4.2 × 3.7 | 814 |
| Excavator | Traffic & safety | 5.4 × 8.9 × 4.9 | 776 |
| Skid-steer loader | Traffic & safety | 1.8 × 3.6 × 2.1 | 616 |
| Lumber and sheet goods | Traffic & safety | 2.9 × 5.6 × 1.3 | 2,292 |
| Concrete barrier | Traffic & safety | 3.0 × 0.6 × 0.8 | 80 |
| Inflatable raft | Landscape | 1.9 × 4.2 × 0.7 | 1,122 |
| Canoe | Landscape | 0.9 × 4.9 × 0.5 | 406 |
| Drift boat | Landscape | 4.3 × 4.7 × 1.1 | 318 |
| Pumpjack | Landscape | 1.8 × 9.5 × 5.3 | 620 |
| Grain bins | Landscape | 11.6 × 6.1 × 7.4 | 1,856 |
| Wind turbine | Landscape | 42.4 × 11.3 × 84.5 | 600 |
| Roadway street light | Lighting | 0.6 × 3.0 × 9.1 | 196 |
| Lamp post with flower baskets | Lighting | 2.1 × 0.6 × 4.4 | 1,488 |
| Flagpole | Street furniture | 2.3 × 0.9 × 9.1 | 180 |
| Lane garage | Garden & growing | 7.5 × 8.8 × 4.5 | 576 |
| Carport | Shelters & markets | 6.4 × 6.2 × 3.0 | 422 |
| Ground solar array | Street furniture | 8.6 × 3.1 × 2.6 | 676 |
| Richardson's ground squirrels | Wildlife | 1.0 × 0.9 × 0.3 | 974 |
| Coyote | Wildlife | 0.3 × 1.3 × 1.1 | 976 |
| Mallards | Wildlife | 0.7 × 0.6 × 0.4 | 634 |
| American white pelicans | Wildlife | 1.4 × 1.1 × 1.1 | 686 |
| Osprey nesting platform | Wildlife | 1.4 × 1.6 × 12.2 | 846 |
| Horses | Landscape | 2.6 × 2.8 × 2.2 | 1,936 |
| Cattle | Landscape | 2.9 × 2.7 × 1.5 | 1,744 |

Vehicles are modelled like the existing ones, with the long axis along the
depth. The light-rail car is low-floor to suit the ground-level platform shelter, and its
pantograph reaches 5.5 m, the contact-wire height of the catenary pole. The
concrete barrier is sized to butt end to end. Horses and cattle sit in
Landscape beside the hay bale rather than under Wildlife, and are found by
searching `horse`, `cattle` or `ranch`. The wind turbine is the one very large
item: an 84 m tip height suits city-edge scenes, not a street.

## New seasonal plants

| Item | Kind | W × D × H (m) | Triangles | Bytes |
|---|---|---:|---:|---:|
| Green ash · autumn | Tree | 7.7 × 8.8 × 12.7 | 13,248 | 1,512,324 |
| Manitoba maple · autumn | Tree | 7.8 × 7.7 × 10.8 | 13,920 | 1,588,956 |
| Paper birch · autumn | Tree | 4.5 × 4.7 × 10.5 | 13,788 | 1,573,896 |
| Plains cottonwood · autumn | Tree | 12.4 × 12.3 × 20.4 | 12,606 | 1,439,164 |
| Showy mountain ash · autumn | Tree | 4.1 × 4.1 × 7.3 | 12,218 | 1,394,944 |
| Bur oak · autumn | Tree | 9.3 × 9.4 × 11.1 | 12,462 | 1,422,716 |
| Common lilac · winter | Planting | 3.1 × 2.7 × 3.3 | 2,754 | 315,168 |
| Caragana hedge · winter | Planting | 3.0 × 1.3 × 2.0 | 3,219 | 368,184 |
| Cotoneaster hedge · winter | Planting | 2.3 × 0.9 × 1.3 | 824 | 95,988 |
| Saskatoon berry · winter | Planting | 2.4 × 2.2 × 2.6 | 1,992 | 228,292 |
| Highbush cranberry · winter | Planting | 2.8 × 2.6 × 2.8 | 2,820 | 323,552 |
| Prickly wild rose · winter | Planting | 1.6 × 1.5 × 1.0 | 2,466 | 283,184 |
| Cotoneaster hedge · autumn | Planting | 2.2 × 0.9 × 1.2 | 2,945 | 337,796 |
| Saskatoon berry · autumn | Planting | 2.3 × 2.2 × 2.6 | 3,288 | 376,872 |
| Red-osier dogwood · winter | Planting | 2.3 × 2.6 × 2.1 | 3,600 | 411,628 |

Until now a winter scene showed bare trees over summer-green shrubs, and only
two trees had an autumn form. Each seasonal form shares its base plant's seed
and random sequence, so a student can swap seasons without the plant changing
shape. The winter cranberry keeps its red berries and the winter rose its hips,
by giving the existing accent a colour that persists rather than a new accent,
which would have changed the random draws and so the skeleton. The dogwood is
the one exception with no base here, for the reason given above.

## Method

`tools/detail_catalogue/build_calgary_details.py` gained one function per
object and a few shared helpers: a rounded body lofted along its length for
vehicles and cabins, window bands, a road-wheel axle, a box beam between two
points for booms and arms, and an open-hull loft that builds a boat from closed
thin-shell sections so the loft never roofs it over. The animals use the same
spine-loft method as the first four, with a shared four-leg helper.

`tools/detail_catalogue/build_local_foliage.py` gained three autumn palettes,
the seasonal variants, and a twig-colour parameter for shrubs, which the
dogwood uses for red stems.

**Every earlier model is byte-identical.** The 76 earlier objects and 70
earlier plants rebuild to the same hashes; both tools tests pin them. New
entries were appended, so earlier items keep their catalogue order.

The 29 new objects total 3,108,040 bytes and 26,884 triangles; the largest is
the lumber at 2,292 triangles. The 15 plants total 11,672,664 bytes, nearly all
of it the six autumn trees at about 1.5 MB each. The kits are now 9.6 MB and
74.0 MB. Models load on placement only.

## Picker card images

Each new item has a static 480 × 315 WebP card, 235 KB for the 44 together,
hash-locked in `tools/detail_catalogue/detail_card_images.lock.json`, which now
holds 190 entries. Re-rendering the 146 earlier cards reproduced every one byte
for byte, and the committed files were kept. The light-rail car and wind
turbine were toned slightly off white so they read against the pale card.

## Bundle budget

The everyday batch left 5.3 KB of the 8,448 KB JavaScript budget and used up
the route of moving catalogues to the denser transport. This batch therefore
started with a change to the packing plugin, in its own commit:

- Each of the sixteen Z85 catalogues carried an inline copy of the decoder.
  They now import the build codec itself, which has no Node dependency, so the
  bundle holds one copy.
- The decoder is assigned to the chunk that already holds the inflater every
  packed catalogue depends on. The build manifest has the same 155 import
  edges as with Rollup's own placement, so no route gains a chunk dependency.
- Total JavaScript fell from 8,442.7 KB to 8,432.8 KB.

With the 44 new rows the total is 8,439.7 KB, leaving 8.3 KB. That is more
headroom than before either of the last two batches.

A further step is now available but was not taken: with a shared decoder the
denser transport saves about 6% at any size, so the catalogues still shipped as
base64 could move too. That is worth doing before the next large batch.

## Reproduction

```text
python tools/detail_catalogue/build_calgary_details.py --dry-run
python tools/detail_catalogue/build_calgary_details.py --output <fresh-directory> [--id city-bus ...]
python tools/detail_catalogue/build_local_foliage.py --output <fresh-directory> [--id bur-oak-autumn ...]
node tools/detail_catalogue/render_detail_thumbnails.cjs <directory> [utility-pole-lines:3.2,lrt-catenary-pole:4.2]
python tools/detail_catalogue/build_<kit>.py --output <directory> --attach-thumbnails
python tools/detail_catalogue/build_<kit>.py --output <directory> --register
python -m pytest tools/detail_catalogue -q
```

As before, the 146 earlier local rows were removed first, the remaining 155
rows were verified byte for byte against `origin/deployment-version`, and both
kits were registered again in catalogue order. The 301 rows that existed before
this batch are unchanged.

## Verification

- Dry runs: 105 objects and 85 plants, zero paid calls, no Blender.
- Every new item was rendered at eye level, oblique and catalogue-card framing
  and reviewed. Fixed after review: an excavator bucket that hung a metre and a
  half above the ground, wheels and hooves that did not sit on the datum, a
  horse neck that read too long, a buckskin horse given pale instead of dark
  points, a russet oak and winter hedge that were too dark, and winter berries
  too small to see. Final sheets:
  [objects at eye level](calgary-details-v1/batch3-eye-level.jpg),
  [objects oblique](calgary-details-v1/batch3-oblique.jpg),
  [object cards](calgary-details-v1/batch3-cards.jpg),
  [plants at eye level](prairie-foliage-v1/third-batch-eye-level.jpg),
  [plant cards](prairie-foliage-v1/third-batch-cards.jpg). Agent review passed;
  independent human visual acceptance is open.
- Tools pytest for both kits: 23 passed. It rebuilds all 190 models and requires
  byte-identical registry rows, the pinned earlier hashes, budgets, the kit
  material convention, ground and anchor rules, identical skeletons for every
  seasonal form, the backend allowlist, unbranded wording and a hash-locked
  card for every row.
- The whole CI list was run locally:
  - frontend lint with zero warnings, dead-code check and type check pass;
  - `npx vitest run`: 512 files and 4,542 tests passed, 45 skipped;
  - the 134 catalogue delivery guard tests pass with the shared decoder;
  - `check:archetype-assets`, `check:catalogue-json`,
    `check:catalogue-delivery -- --metadata-only`, `check:sticker-pilot-assets`
    and `check:runtime-assets` pass;
  - the runtime asset manifest was regenerated after materializing assets as
    CI does: 5,889 required files (+88);
  - production build with the CI build settings, then `check-budget`:
    8,439.7 KB of 8,448 KB;
  - hosted-asset and Git LFS tests: 22 passed, now covering all 190 local rows;
  - the other CI script tests, the catalogue promotion check and the
    repository blob policy pass;
  - backend `tests/test_project_details.py`: 84 passed, including the mirror
    and round-trip of all 345 extras. The full backend suite needs a database
    and was not run here;
  - browser tests with the sandbox Chromium: 13 passed, and the startup test
    passed.

### App code path, without the globe

The temporary harness was run over all 190 local models with the app's real
`detailCatalogue.ts`, `detailThumbnail.ts` and `detailInstances.ts`. 190 of 190
passed: found by ID and by label, static card at 480 × 315, model loaded,
registered mesh count, base on the 0.084 m detail datum within 0.001 mm, size
within 0.5 mm and rotation pivoting on the anchor. Eighty placements went
through the same instancing path as one scene:
[street, transit and a construction site](calgary-details-v1/scene-batch3-street-and-site.jpg)
and [river bank and ranch edge](calgary-details-v1/scene-batch3-river-and-ranch.jpg).
In that scene the light-rail car stands under the wire of two catenary poles
40 m apart, and its pantograph is built to the same 5.5 m height. The harness
was not committed.

### The real project page, with a mocked backend

A temporary browser trial of **Add details** in a real project page, not
committed:

- [Wildlife](calgary-details-v1/app-batch3-wildlife.jpg) shows 9 cards, all
  from static images;
- each of the 44 new items is found by typing its name, and its card loads
  from its static image at 480 × 315;
- browsing and searching requested **zero** local model files;
- searching [`bus` in Vehicles](calgary-details-v1/app-batch3-search-bus.jpg)
  lists the city bus and the school bus;
- all seven winter shrubs and hedges are listed under Planting;
- choosing the excavator arms placement.

Not done here: placing these items on the live map, which needs a real map
key, Undo/reload, deterministic capture and AI render with them, low-end device
performance and classroom novice use.

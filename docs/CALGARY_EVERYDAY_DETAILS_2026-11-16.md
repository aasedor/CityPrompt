# Everyday Calgary details for Add details: 38 street, lane and yard objects

> **Update, same day.** A [third batch](LOCAL_DETAILS_BATCH3_2026-11-16.md) took the kit to 105
> objects. The 76 models described up to here are byte-identical. The bundle-budget
> note below was acted on there: the catalogues now share one decoder.

## Scope

Add 38 humble, fixed-size objects that make a Calgary street, lane or yard read
as lived in, in the spirit of the black, blue and green waste carts from the
[first Calgary batch](CALGARY_DETAILS_2026-11-16.md): a lane dumpster, the green
utility box on the boulevard, a red letter box, newspaper boxes, bikes dropped
on a lawn, a snowman. They extend the same kit and builder, so IDs keep the
`detail-yyc-` prefix and files live in
`frontend/public/park-kits/calgary-details-v1/`, which now holds 76 objects.

No category is new. The items join Street furniture (17), Garden & growing (7),
Vehicles (3), Play (3), Winter city (3), Seating (2), Traffic & safety (2) and
Sport & exercise (1). All are `kind: object`, saved in project `props`.

The same limits apply as before. These are generic concept models with **no
City of Calgary, Calgary Transit, postal, retail or utility branding** and no
wording. Signs, placards and poster panels are blank shapes. They are not
electrical, traffic-control, construction-site or play-safety designs.

## New choices

| Item | Category | W × D × H (m) | Triangles |
|---|---|---:|---:|
| Lane dumpster | Street furniture | 2.1 × 1.8 × 1.5 | 252 |
| Deep-collection bins | Street furniture | 2.9 × 1.4 × 1.4 | 912 |
| Wildlife-proof park bin | Street furniture | 1.6 × 0.9 × 1.2 | 196 |
| Yard waste paper bags | Street furniture | 1.4 × 0.5 × 1.1 | 471 |
| Donation drop box | Street furniture | 1.3 × 1.3 × 2.2 | 134 |
| Green utility box | Street furniture | 1.4 × 1.3 × 1.0 | 190 |
| Signal control cabinet | Street furniture | 0.9 × 0.7 × 1.6 | 240 |
| Street letter box | Street furniture | 0.6 × 0.6 × 1.3 | 180 |
| Newspaper boxes | Street furniture | 1.6 × 0.4 × 1.3 | 252 |
| Parking pay station | Street furniture | 0.5 × 0.4 × 2.2 | 308 |
| Bus stop bench | Seating | 1.9 × 0.6 × 1.0 | 144 |
| Sandwich board sign | Street furniture | 0.6 × 0.5 × 0.9 | 228 |
| Shopping cart | Street furniture | 0.6 × 1.1 × 1.1 | 830 |
| Portable toilet | Street furniture | 1.2 × 1.3 × 2.6 | 336 |
| Patio heater | Street furniture | 0.9 × 0.9 × 2.2 | 808 |
| Park charcoal grill | Street furniture | 1.0 × 1.0 × 1.1 | 204 |
| Backyard barbecue | Garden & growing | 1.4 × 0.6 × 1.2 | 628 |
| Adirondack chairs | Seating | 2.3 × 1.1 × 1.0 | 616 |
| Rotary clothesline | Garden & growing | 1.9 × 1.9 × 2.1 | 260 |
| Wheelbarrow | Garden & growing | 0.7 × 1.9 × 1.3 | 342 |
| Half-barrel planter | Garden & growing | 0.8 × 0.8 × 0.7 | 1,131 |
| Parked bicycle | Vehicles | 0.6 × 1.7 × 1.0 | 1,388 |
| Kids' bikes on the lawn | Play | 1.7 × 1.5 × 0.4 | 2,826 |
| Driveway basketball hoop | Play | 1.1 × 1.7 × 3.6 | 824 |
| Backyard sandbox | Play | 1.8 × 1.8 × 0.5 | 644 |
| Camping trailer | Vehicles | 2.5 × 5.6 × 2.8 | 1,256 |
| Disc golf basket | Sport & exercise | 0.7 × 0.7 × 1.6 | 804 |
| Construction barrel | Traffic & safety | 0.7 × 0.7 × 1.0 | 276 |
| Construction fence panel | Traffic & safety | 3.1 × 0.7 × 1.9 | 226 |
| Snowman | Winter city | 1.6 × 0.9 × 1.9 | 1,184 |
| Toboggan and saucer | Winter city | 1.4 × 1.8 × 0.5 | 486 |
| Bicycle with child trailer | Vehicles | 0.9 × 3.4 × 1.7 | 2,419 |
| Bird feeder with chickadees | Garden & growing | 0.7 × 0.4 × 2.1 | 738 |
| Telecom pedestals | Street furniture | 0.8 × 0.4 × 0.9 | 240 |
| Firewood stack | Garden & growing | 3.2 × 1.1 × 1.2 | 1,696 |
| Snow shovel in a snowbank | Winter city | 1.8 × 1.3 × 1.5 | 430 |
| Lawn mower | Garden & growing | 0.6 × 1.3 × 1.0 | 548 |
| Propane exchange cage | Street furniture | 1.5 × 0.7 × 2.1 | 1,220 |

The construction fence panel is sized to butt end to end. The camping trailer
is anchored at the middle of its body, with the hitch pointing along its depth.

Before building, the list was checked against the items already in the panel. A community mailbox, a dog-waste bag dispenser, rain barrels and
compost bins already exist, so those were left out.

## Method

`tools/detail_catalogue/build_calgary_details.py` gained one function per
object plus a few shared helpers: a solid wheel, a spoked bicycle wheel, a
barrel-top prism, a side-profile extrusion, and `rest_on_ground`, which settles
a tilted sub-assembly so its lowest point touches the ground. The bicycle is
one function reused four times: parked on its kickstand, towing the child
trailer, and twice at child size dropped on the lawn. Its kickstand length is
set so that at the parked lean the foot and both tyres touch down together.

The files share the kit format: linear vertex colours, flat normals, no
textures, extensions or node transforms, one matte mesh and, for seven of the
38, a second smoother mesh for glass and screens.

The 38 new GLBs total 3,000,144 bytes and 25,867 triangles; the largest is the
kids' bikes at 2,826 triangles and 323,344 bytes. The whole kit of 76 is
6,518,740 bytes. Models load on placement only.

**The first 38 models are byte-identical.** The builder was extended, not
re-tuned, and the tools test now pins a digest over their 38 hashes so a later
change to shared code cannot alter a shipped model unnoticed.

## Picker card images

Each new item has a static 480 × 315 WebP card beside its GLB, 167 KB for the
38 together, hash-locked in `tools/detail_catalogue/detail_card_images.lock.json`.
Re-rendering the earlier 38 cards on the way reproduced all of them byte for
byte, and the committed files were kept. The snowbank and the propane cage were
re-toned after the first card pass so they read against the pale card.

## A release-tooling defect found and fixed

Running the CI asset step for this batch showed that the branch had been
failing a check since its first commit, which earlier runs of the narrower
detail tests did not exercise:

- `scripts/tests/test_hosted_assets.py` pins the number of Add details files in
  the hosted-asset closure, and the count had not been updated for the local kits.
- `scripts/hosted_assets.py` read a picker card's hash from its catalogue row.
  The earlier change that moved those hashes into the sidecar lock, to keep
  them out of the JavaScript bundle, left it with nothing to read, so
  `scripts/materialize_frontend_assets.py` stopped with a `KeyError`.

`detail_requirements` now takes a capture's hash from its row or, by row ID,
from the tracked lock file. One of the two must give an exact SHA-256 and they
may not disagree. The lock is registered as a release input, so a prepared
asset packet goes stale when a card changes. The test now covers all 146 local
rows, checks the committed card bytes against the lock, and refuses a card with
no lock or with two conflicting ones.

## Bundle budget

Catalogue rows ship compressed inside the production bundle, and CI holds total
JavaScript to 8,448 KB with its own build settings. The 38 new rows took the
total from 8,441.7 KB to 8,448.2 KB, which is 0.2 KB over.

Following the same practice as the [foliage batch](LOCAL_FOLIAGE_SEASONS_2026-11-16.md),
six more catalogues moved to the lossless Z85 transport: `nativeBridgeRelease`,
`localPlanIndex`, `legoFamilySignatures`, `nativeBridgePilots`,
`validationCatalogue` and `classroomExpansion`. Each is above the roughly 20 KiB
packed size where the inline decoder pays for itself, and each is covered by a
test that decodes it after minification and requires it to equal the source.
Total JavaScript is now 8,442.7 KB, leaving 5.3 KB.

**This route is now used up.** The remaining catalogues are too small to gain
from it. At about 170 bytes a row, the next batch of roughly 30 items will need
either a shared decoder in the packing plugin, which by estimate would recover
several KB by replacing sixteen inline copies with one, or a decision on the
budget itself.

## Reproduction

```text
python tools/detail_catalogue/build_calgary_details.py --dry-run
python tools/detail_catalogue/build_calgary_details.py --output <fresh-directory> [--id dumpster ...]
node tools/detail_catalogue/render_detail_thumbnails.cjs <directory> utility-pole-lines:3.2,lrt-catenary-pole:4.2
python tools/detail_catalogue/build_calgary_details.py --output <directory> --attach-thumbnails
python tools/detail_catalogue/build_calgary_details.py --output <directory> --register
python -m pytest tools/detail_catalogue/test_calgary_details.py -q
```

`--register` refuses IDs already present, so for this batch the 108 earlier
local rows were first removed, with the remaining 155 rows verified byte for
byte against `origin/deployment-version`, and both kits were registered again in
catalogue order. The 263 rows that existed before this batch are unchanged.

## Verification

- Dry run: 76 items, zero paid calls, no Blender.
- Every new item was rendered at eye level, oblique and catalogue-card framing
  and reviewed. Fixed after review: barbecue legs that stopped short of the
  ground, chair legs and a bicycle mudguard that dipped below it, a kickstand
  too long for the lean, loose logs that read as legs on the chopping block,
  and a snowbank and propane cage too pale for the card. Final sheets:
  [eye level](calgary-details-v1/everyday-eye-level.jpg),
  [oblique](calgary-details-v1/everyday-oblique.jpg),
  [catalogue cards](calgary-details-v1/everyday-cards.jpg). Agent review passed;
  independent human visual acceptance is open.
- Tools pytest for both local kits: 23 passed. It rebuilds all 146 models and
  requires byte-identical registry rows, the pinned first-batch digest, budgets,
  the kit material convention, ground and anchor rules, the backend allowlist,
  unbranded wording and a hash-locked card for every row.
- This time the whole CI list was run locally, not only the detail tests:
  - frontend lint with zero warnings, dead-code check and type check pass;
  - `npx vitest run`: 512 files and 4,542 tests passed, 45 skipped;
  - the 134 catalogue delivery guard tests pass, six of them new;
  - `check:archetype-assets`, `check:catalogue-json`,
    `check:catalogue-delivery -- --metadata-only`, `check:sticker-pilot-assets`
    and `check:runtime-assets` pass;
  - the runtime asset manifest was regenerated after materializing assets as CI
    does: 5,801 required files (+76);
  - production build with the CI build settings, then `check-budget`:
    8,442.7 KB of 8,448 KB;
  - hosted-asset and Git LFS tests: 22 passed. Five of them failed on the
    branch as previously pushed;
  - the other CI script tests, the catalogue promotion check and the
    repository blob policy pass;
  - backend `tests/test_project_details.py`: 84 passed, including the mirror
    and round-trip of all 301 extras. The full backend suite needs a database
    and was not run here;
  - browser tests with the sandbox Chromium: 12 passed and 1 passed on retry
    (project creation, unrelated to this change), and the startup test passed.
- Seven other tests under `scripts/tests` fail in this sandbox because their
  models are unhydrated Git LFS pointers. They fail identically on a clean
  checkout of `origin/deployment-version` and are not in the CI list.

### App code path, without the globe

The temporary harness from the first Calgary batch was run again over all 146
local models with the app's real `detailCatalogue.ts`, `detailThumbnail.ts` and
`detailInstances.ts`. 146 of 146 passed: found by ID and by label, static card
at 480 × 315, model loaded, registered mesh count, base on the 0.084 m detail
datum within 0.001 mm, size within 0.5 mm and rotation pivoting on the anchor.
A composed lane went through the same instancing path:
[shops side of the lane](calgary-details-v1/scene-everyday-main-street.jpg) and
[backyards](calgary-details-v1/scene-everyday-yards.jpg). The harness was not
committed.

### The real project page, with a mocked backend

A temporary browser trial of **Add details** in a real project page, again not
committed:

- [Winter city](calgary-details-v1/app-everyday-winter-city.jpg) shows 12 cards,
  all from static images;
- each of the 38 new items is found by typing its name, and its card loads from
  its static image at 480 × 315;
- browsing and searching requested **zero** local model files;
- searching [`cart` in Street furniture](calgary-details-v1/app-everyday-search-cart.jpg)
  lists the four waste carts and the shopping cart;
- choosing the lane dumpster arms placement.

Not done here: placing these objects on the live map, which needs a real map
key, Undo/reload, deterministic capture and AI render with them, low-end device
performance and classroom novice use.

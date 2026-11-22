# Native park batch

Builds native parks (`native_park_v2`) as one self-contained assembly GLB each, in
pure Python with numpy, shapely and earcut. No Blender and no paid calls.

| Park | `--park` | Variant id | Site |
|---|---|---|---:|
| Prairie Bowl Skate Park | `skate` | `student_prairie_bowl_skate_park_v1` | 64 x 52 m |
| Parkour & Calisthenics Yard | `fitness` | `student_parkour_calisthenics_yard_v1` | 44 x 36 m |
| Walled Memorial Garden | `memorial` | `student_walled_memorial_garden_v1` | 36 x 50 m |
| Community Ball Diamond | `baseball` | `student_community_ball_diamond_v1` | 88 x 88 m |
| Community Track & Field | `track` | `student_community_track_field_v1` | 200 x 112 m |
| Village Green Cricket Ground | `cricket` | `student_village_green_cricket_v1` | 120 x 120 m |
| Prairie Wind Plaza | `plaza` | `student_calgary_prairie_plaza_v1` | 64 x 52 m |
| Clover Neighbourhood Park | `neighbourhood` | `student_clover_neighbourhood_park_v1` | 84 x 68 m |
| Prairie Sports Complex | `complex` | `student_prairie_sports_complex_v1` | 216 x 168 m |
| Creekside Mini Golf | `minigolf` | `student_creekside_mini_golf_v1` | 48 x 40 m |
| Boulder Block Park | `bouldering` | `student_boulder_block_park_v1` | 40 x 32 m |
| Prairie Pollinator Meadow | `meadow` | `student_prairie_pollinator_meadow_v1` | 48 x 36 m |

They are local pilots: registered, not runtime-tested, not published.
`docs/PARK_BATCH_1_2026-11-21.md` to `docs/PARK_BATCH_4_2026-11-22.md` describe the parks and the checks.

## Files

| File | Purpose |
|---|---|
| `parkkit.py` | Shared kit: runtime material names and surface colours, polygon fills, heightfields, extrusions, instanced plants, furniture, layout helpers and the GLB writer |
| `sportskit.py` | Sports pieces for batch 2: chain-link and picket fences, bleachers, dugouts, field lights, scoreboards, goals, a shelter, hurdles, chalk markings and mowing stripes |
| `playkit.py` | Plaza and play pieces for batch 3: shade sails, market stalls, a wind screen, boulders, paver bands, tree grates, play towers, a slide, swings, a split-rail fence, picnic tables and a fieldhouse |
| `leisurekit.py` | Batch 4 pieces: mini golf cups, flags and edging, footbridges and ramps, a sod-roof hut, angular bouldering blocks, bee hotels, lecterns and a cheap bloom field for massed meadow flowers |
| `skate_park.py`, `fitness_circuit.py`, `memorial_garden.py`, `baseball_diamond.py`, `running_track.py`, `cricket_ground.py`, `prairie_plaza.py`, `neighbourhood_park.py`, `sports_complex.py`, `mini_golf.py`, `bouldering_park.py`, `pollinator_meadow.py` | One park each: site, entrance, plan, programme, routes, planting and park-specific checks |
| `build.py` | Builds one park into a new directory: `assembly-preview.glb` and `recipe.json`. The recipe's generator hash covers the park file, `parkkit.py` and any files the park lists in `KIT_SOURCES` |
| `verify.py` | Offline geometry checks on the delivered GLB; writes `geometry-verification.json` |
| `cameras.json`, `review.html`, `render.cjs` | Review renders of the GLB in headless Chromium |
| `runtime_review.py` | Fills `docs/ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md` for a seed package; every applicable gate stays NOT TESTED |
| `test_native_park_batch.py` | Rebuilds the twelve registered parks byte for byte and re-runs the checks |

## The runtime contract the kit follows

- Walkable ground is a face whose material is in the park's
  `walk_surface_materials`, facing up, between -0.4 and 0.45 m. Bowls go deeper,
  so walkers never step into them.
- `water` is a hazard.
- Steep faces that are not foliage are barriers.
- The assembly owns its ground and is never stretched. Plants are instances, and
  their origins stay clear of every route.

## Reproduce

```bash
python3 tools/native_park_batch/build.py --park skate --dry-run
python3 tools/native_park_batch/build.py --park skate --output <dir>
python3 tools/native_park_batch/verify.py skate <dir>
python3 -m http.server 8765 --bind 127.0.0.1 &          # from the repository root
node tools/native_park_batch/render.cjs skate <dir>/assembly-preview.glb <dir>/renders
python3 scripts/register_park_batch1.py --package <dir>   # or register_park_batch2.py to 4; card image: <dir>/renders/aerial.png
python3 tools/native_park_batch/runtime_review.py skate seed/classroom-parks/prairie-bowl-skate-v006
python3 -m pytest tools/native_park_batch
```

`build.py` refuses an existing directory. The registrar refuses a model whose
hash differs from the reviewed one in `scripts/register_park_batch1.py`.
Review builds live under the ignored `artifacts/park-batch/<park>/`.

## Budgets

Keep a park under about 850,000 rendered triangles and 12 MB. Each unique tree
species adds about 1 MB of mesh data, and a shrub costs 2,000 to 4,500
triangles. Large grounds should use a few tree species for mass and keep shrub
beds small.

## Frozen kits

A registered park's recipe records the source hash of its park file, `parkkit.py`
and every file in its `KIT_SOURCES`. Once a park is registered, those files are
frozen: changing one changes the hash and fails the rebuild test. New pieces go
into a new kit file (`sportskit.py` for batch 2, `playkit.py` for batch 3, `leisurekit.py` for batch 4). Lint
fixes in a registered park file wait until that park is re-registered under a
new revision.

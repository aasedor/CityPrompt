# Native park batch

Builds native parks (`native_park_v2`) as one self-contained assembly GLB each, in
pure Python with numpy, shapely and earcut. No Blender and no paid calls.

| Park | `--park` | Variant id | Site |
|---|---|---|---:|
| Prairie Bowl Skate Park | `skate` | `student_prairie_bowl_skate_park_v1` | 64 x 52 m |
| Parkour & Calisthenics Yard | `fitness` | `student_parkour_calisthenics_yard_v1` | 44 x 36 m |
| Walled Memorial Garden | `memorial` | `student_walled_memorial_garden_v1` | 36 x 50 m |

They are local pilots: registered, not runtime-tested, not published.
`docs/PARK_BATCH_1_2026-11-21.md` describes the parks and the checks.

## Files

| File | Purpose |
|---|---|
| `parkkit.py` | Shared kit: runtime material names and surface colours, polygon fills, heightfields, extrusions, instanced plants, furniture, layout helpers and the GLB writer |
| `skate_park.py`, `fitness_circuit.py`, `memorial_garden.py` | One park each: site, entrance, plan, programme, routes, planting and park-specific checks |
| `build.py` | Builds one park into a new directory: `assembly-preview.glb` and `recipe.json` |
| `verify.py` | Offline geometry checks on the delivered GLB; writes `geometry-verification.json` |
| `cameras.json`, `review.html`, `render.cjs` | Review renders of the GLB in headless Chromium |
| `runtime_review.py` | Fills `docs/ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md` for a seed package; every applicable gate stays NOT TESTED |
| `test_native_park_batch.py` | Rebuilds the three registered parks byte for byte and re-runs the checks |

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
python3 scripts/register_park_batch1.py --package <dir>   # card image: <dir>/renders/aerial.png
python3 tools/native_park_batch/runtime_review.py skate seed/classroom-parks/prairie-bowl-skate-v006
python3 -m pytest tools/native_park_batch
```

`build.py` refuses an existing directory. The registrar refuses a model whose
hash differs from the reviewed one in `scripts/register_park_batch1.py`.
Review builds live under the ignored `artifacts/park-batch/<park>/`.

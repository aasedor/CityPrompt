# Stormwater pond park builder

Builds `student_stormwater_pond_v1`, the **Stormwater Pond & Pathway Loop**
native park: an 86 by 68 m wet pond with cattail shallows, a 3 m asphalt loop,
a timber viewing dock, an inlet headwall and an outlet control structure. See
[the build notes](../../docs/STORMWATER_POND_PARK_2026-11-19.md).

Everything is drawn in Python with no paid calls and no Blender. The plants come
from the shared foliage generator in `tools/detail_catalogue`.

## Steps

```bash
# 1. Build a new candidate. An existing directory is never overwritten.
python3 tools/stormwater_pond_park/build.py --output <candidate dir>

# 2. Check the delivered GLB and write geometry-verification.json beside it.
python3 tools/stormwater_pond_park/verify.py <candidate dir>

# 3. Render review views (serve the repository root at 127.0.0.1:8765 first).
node tools/stormwater_pond_park/render.cjs <candidate dir>/assembly-preview.glb <candidate dir>/renders

# 4. Register an inspected candidate as a pilot. The hash in SPECS must match.
python3 scripts/register_stormwater_pond.py --package <candidate dir>
```

Registration needs `renders/aerial.png` in the package; it becomes the card
thumbnail and the seeded `preview.png`.

## Files

- `build.py`: the generator. Its constants set the site, pond outline, water
  level, path widths and lookout positions.
- `verify.py`: offline checks on the exact GLB bytes. It covers hashes, footprint,
  the water plane, walkable route rays and planting clear of the routes.
- `review.html`, `render.cjs`, `cameras.json`: the headless review renderer and
  its eight views.
- `test_stormwater_pond.py`: rebuilds the seeded package byte for byte and
  re-runs the checks on it.

The reviewed package is `seed/classroom-parks/stormwater-pond-v002/`.

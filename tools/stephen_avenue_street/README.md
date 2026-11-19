# Stephen Avenue street builder

Builds `student_stephen_avenue_mall_v1`, the **Stephen Avenue Pedestrian Mall**
as a street students draw, like the other native streets. The street only: no
buildings, storefronts or +15 skywalks. See
[the build notes](../../docs/STEPHEN_AVENUE_MALL_2026-11-19.md).

Pure Python: no Blender and no paid calls. The linden comes from the shared
foliage generator in `tools/detail_catalogue`, and the furniture from its clay kit.

## Steps

```bash
# 1. Build a candidate: five module GLBs, a 40 m preview, the recipe and the registry row.
python3 tools/stephen_avenue_street/build.py --output <new directory>

# 2. Review renders of the preview (serve the repository root at 127.0.0.1:8765 first).
node tools/stephen_avenue_street/render.cjs <new directory>/assembly-preview.glb <new directory>/renders

# 3. Register it as a local pilot. Dry run first; --install writes, with backups.
python3 tools/stephen_avenue_street/install.py --package <new directory> --backups <directory>
python3 tools/stephen_avenue_street/install.py --package <new directory> --backups <directory> --install
```

The installer only adds. It splices each registry file as text, so existing
records keep their exact bytes, and it refuses to replace a different revision.
It writes:

- the row in both copies of `nativeStreetPilots.json`;
- the release in both copies of `classroomStarter.json`;
- the module bounds in `nativeStreetModuleBounds.json`;
- the card in `classroomExpansion.json`;
- the presentation text and the hero photo;
- the five modules under `frontend/public/street-kits/pilots/`;
- the new public-realm catalogue fingerprint in the backend history.

Then regenerate the runtime asset manifest. Module GLBs are force-added to Git
LFS, as the other pilots' are.

## Files

- `build.py`: the section, the five modules, one 40 m placement cycle and the
  surface programme. Every dimension is a named constant.
- `install.py`: the additive registration.
- `review.html`, `render.cjs`, `cameras.json`: headless review renders.
- `test_stephen_avenue.py`: the generator still writes the registered row, module
  bytes and bounds. The roster, card and hero bind the same revision. The
  sections tile the 20 m width, and the clear routes stay clear. Every item fits
  its cycle and zone, and there are no motor lanes.

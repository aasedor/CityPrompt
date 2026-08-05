# Neighborhood park LEGO + authored-depth pilot

This bounded pilot starts from `b5ad07d6` on
`codex/neighborhood-park-skins-pilot-v1`. It replaces the former drape handoff
with a semantic LEGO surface and seats the existing archetype-authored
basketball kit on that surface at metric scale.

## Reviewed result

[Mobile comparison sheet](lego-depth-pilot-comparison-mobile.png)

[Archetype-matched v2 comparison](basketball-archetype-matched-v2-mobile.png)

The v2 acceptance pass moves beyond the first tabletop proof. It renders the
same metric kit in a reference-matched urban scene with a dark asphalt court,
complete linework, galvanized enclosure, brick street walls, benches, people,
street trees, cars, and base/60-degree/90-degree cameras paired to the
catalogue views. These elements are generated as 3D geometry and PBR materials;
the archetype photographs are used only as visual targets in the comparison.

The pilot works. The split is clean:

- the LEGO park grammar owns the parcel, paths, lawn, planting, pavilion pad,
  exact `32 x 19 m` basketball envelope, acrylic surface, and markings;
- the GLB kit owns only vertical/depth features: two hoops, reusable `4 m`
  fence panels, two `3 m` gates, and four floodlights;
- every depth asset remains at `metricScale: 1.0` and preserves its authored
  ground-contact origin;
- the GLBs contain no duplicate court plane, so surface updates cannot create
  z-fighting or a second conflicting park;
- the source basketball base, 60-degree, and 90-degree catalogue renders remain
  the reference for equipment language, silhouette, and count;
- the pilot makes zero image or model API calls.

The A/B render shows that the LEGO surface supplies adaptable ground and
materials, while the authored kit supplies the identity-bearing silhouette,
shadows, and enclosure. The top view verifies registration against the exact
court envelope.

## Important catalogue rule

Do not scale a complete park GLB to a small program pad. The existing
`50 x 40 m` inclusive-playground kit, for example, is a whole archetype and
would become toy-sized if forced onto the neighborhood park's compact play
pad. It must first be split into module-level assets such as tower-and-slide,
accessible ramp, swing bay, spinner, sensory panel, and shade canopy. Each
module then needs a footprint, clearance, anchor, and allowed rotation before
the LEGO grammar can place it.

Basketball is the ideal first proof because the metric envelope and repeated
asset anchors are unambiguous. The next gate should be one rotated or irregular
parcel, followed by one decomposed playground module.

## Reproduce

```powershell
python tools/park_skin_compiler/generate_adaptive_urban_materials.py
python tools/park_skin_compiler/generate_lego_depth_asset_pilot.py --dry-run
python tools/park_skin_compiler/generate_lego_depth_asset_pilot.py
& 'C:\Program Files\Blender Foundation\Blender 5.1\blender.exe' `
  --background --factory-startup `
  --python tools/park_skin_compiler/render_lego_depth_asset_pilot.py -- `
  --repo-root . `
  --output artifacts/neighborhood-park-lego-depth-pilot/renders
python tools/park_skin_compiler/compose_lego_depth_asset_pilot.py `
  --output artifacts/neighborhood-park-lego-depth-pilot/lego-depth-pilot-comparison-mobile.png
```

The checked-in contract is
[`tools/park_skin_compiler/lego_depth_asset_pilot.json`](../../tools/park_skin_compiler/lego_depth_asset_pilot.json).
Heavy render intermediates remain ignored under `artifacts/`; only the reviewed
comparison sheet is promoted.

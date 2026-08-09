# Fixed GLB Meshy/Blender pilot

This pilot compares two non-modular, fixed-dimension assets for the same brief:

- adaptive-reuse brick warehouse loft;
- 40 m frontage x 20 m depth;
- two main storeys with a pitched standing-seam roof;
- one complete GLB per pipeline, with no runtime bay or floor assembly.

Generated files and renders live outside the repository under
`C:/dev-artifacts/3D-Maps/fixed-glb-meshy-blender-pilot/`.

## Commands

Run the free Meshy preflight before starting the one-call pilot:

```powershell
python tools/fixed_glb_pilot/run_meshy_warehouse.py `
  --repo-root . `
  --env-file C:/path/to/repository/.env `
  --reference frontend/public/archetypes/buildings/adaptive_reuse_warehouse_lofts/variant_0.png `
  --output C:/dev-artifacts/3D-Maps/fixed-glb-meshy-blender-pilot `
  --dry-run
```

The Blender builder and Meshy normalizer are headless scripts:

```powershell
blender --background --python tools/fixed_glb_pilot/build_blender_warehouse.py -- `
  --repo-root . `
  --output C:/dev-artifacts/3D-Maps/fixed-glb-meshy-blender-pilot

blender --background --python tools/fixed_glb_pilot/normalize_render_meshy.py -- `
  --input C:/dev-artifacts/3D-Maps/fixed-glb-meshy-blender-pilot/adaptive_warehouse_meshy_raw.glb `
  --output C:/dev-artifacts/3D-Maps/fixed-glb-meshy-blender-pilot
```

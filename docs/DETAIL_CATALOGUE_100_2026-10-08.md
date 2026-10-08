# Standalone detail catalogue â€” 100 choices (2026-10-08)

## Scope

Extend the existing project detail editor from 10 to 100 choices using existing
metric park and street component GLBs. No building/park/street archetype assemblies
are changed, no generated replacement models are added, and embedded archetype
objects remain outside this editor. This is a local checkpoint, not a deployment.

## Catalogue

| Category | Choices |
|---|---:|
| Seating | 7 |
| Trees | 8 |
| Street furniture | 9 |
| Landscape | 3 |
| Sport & exercise | 17 |
| Garden & growing | 7 |
| Edges & gates | 6 |
| Shelters & markets | 10 |
| Play | 13 |
| Water & landmarks | 7 |
| Planting | 6 |
| Lighting | 7 |

The 90 additions are recorded in
`frontend/src/features/parks/detailCatalogueExtras.json`: stable ID, original URL,
source kit, SHA-256, original metric dimensions, source-space ground/centre offset,
triangle count and bytes. Original ten IDs and positions are preserved. New model
origins are centred horizontally and grounded without scaling. Category/search
options derive from the registry. Lights and water features are static geometry.

`backend/app/data/project_detail_models.json` is the server allowlist. Tests check
full parity with the frontend additions; arbitrary asset URLs remain rejected.
The existing ownership, revision-conflict, finite-coordinate, unique-ID and item
limits are retained. Old clients omitting trees/props preserve saved collections.

## Rendering

`GlobeProjectBenches` groups placements by asset. `DetailModelInstances` loads only
models actually placed, sharing the existing GLTF cache. One InstancedMesh per
source mesh shares geometry/materials across placements. Source hierarchy transforms,
Y-up conversion, yaw and terrain elevation are retained; a local ENU origin avoids
Earth-scale Float32 instance translations. Instance bounds are updated for culling.
Only instance buffers are disposed; shared geometry and materials stay cached.
All detail meshes have no-op raycasts, keeping editing exclusive to detail mode.
Existing prepared-ground/fallback terrain logic and two-probes-per-frame budget remain.

## Trial and evidence

Local project: `099fdc75-8eb1-4849-b602-8eebecef296e` (Bench detail editor Â· pilot).
Added cherry tree, contemporary path light, meadow grass, street planter and ivy
pergola in open ground through the UI. Verified movement, 15-degree rotation,
removal/undo, save and full reload. Final trial: 3 original benches, 4 trees,
10 independent objects, plus the original building, street and park.

All 100 choices were loaded across five visual-review pages. All 90 added URLs
returned HTTP 200 and the expected SHA-256 from the running Vite asset root.
Existing GLBs were hydrated from the local Git LFS cache into the ignored/external
runtime asset directory, without changing tracked binary content or issuing paid calls.

Controlled WebGL comparison at `/detail-catalogue-review.html`:
100 identical timber benches, same camera and geometry, no shadows in either case.
- Individual copies: 201 draw calls, 44,002 triangles.
- Instanced copies: 3 draw calls, 44,002 triangles.
- Ground accounts for one call/two triangles. Bench draw calls fall 200 to 2 (99%).

A pixel comparison of the scene below the changing review header was identical
(mean RGB difference 0); batching preserved the test scene appearance.

This measures draw-call reduction, not a 99% frame-rate improvement. Different
models still require their own batches; texture memory and triangle count are not
removed. Google tiles, existing archetype rendering and laptop hardware still matter.
A classroom laptop walking benchmark remains a separate test.

Evidence is external, not committed:
`C:/dev-artifacts/CityPrompt/bench-editor-2026-10-08/`
- catalogue-100-page-1.png through catalogue-100-page-5.png
- detail-individual-100.png and detail-batched-100.png
- catalogue-100-project-trial.png and catalogue-100-saved-editor.png
- catalogue-100-http-check.json, detail-inventory.json, detail-curation.json

## Verification and maintenance

Verified: 48 frontend tests across seven focused files, eight backend tests,
TypeScript type-check and focused ESLint. No browser error logs were recorded
in either the project trial or catalogue review.

Run the focused tests for detailCatalogue, detailInstances, BenchDetailEditor,
projectBenches, benchDetails, StudentWorkflow and neighborhoodParkLayout, then
frontend type-check and focused ESLint. Backend: `pytest tests/test_project_details.py`.
The local review HTML is not mounted in the student app or included as a production
entrypoint. Review previews normalize object sizes; the project always uses real sizes.

Regenerate `runtimeAssetManifest.json` after catalogue changes. Its refresh also
reconciles graph changes already present in the branch. Sparse checkout LFS pointers
are metadata evidence only; hydrate and validate the complete release asset set before
a future deployment. This task verified the additional models served by the local app.

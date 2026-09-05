# Rustic neighbourhood park candidate v5

Exact identity: `neighborhood_park / neighborhood_park_v0`. This is the
adaptive local pilot, not an approved release or a building-clay delivery.
The three source images, inferred dimensions and component hashes are in
`candidate-manifest.json`. Historical v2 evidence remains in
`docs/NEIGHBOURHOOD_PARK_PILOT_2026-09-05.md`.

Run a finite nine-asset build with Blender, supplying the hydrated original
checkout and a **new, empty** revision output directory:

```powershell
blender --background --python tools/neighborhood_park_pilot/build_assets.py -- --source-root '<hydrated-source-checkout>' --output-dir '<external>/public/landscape-pilots/neighborhood-rustic-v5' --dry-run
blender --background --python tools/neighborhood_park_pilot/build_assets.py -- --source-root '<hydrated-source-checkout>' --output-dir '<external>/public/landscape-pilots/neighborhood-rustic-v5'
python tools/neighborhood_park_pilot/verify_assets.py '<external>/public/landscape-pilots/neighborhood-rustic-v5'
```

The source checkout supplies the preserved historical park builder, exact
variant references, and the MIT-licensed ez-tree oak texture. The candidate
records their hashes. Python verification requires numpy and trimesh. It
measures exported vertices, checks all four individual boulder contacts,
declared dimensions, hashes, mesh counts and the tree crown/alpha contract.
Do not replace the tracked candidate manifest until the actual new exports
pass this check and visual review. Use `tools/catalogue_runtime/prepare_public.ps1`
and `serve.ps1` for the integrated app; candidate GLBs are copied deliberately
and common hydrated assets remain explicitly sourced through junctions.

v5 improves irregular, layered tree crowns and smaller instanced meadow
plants. Foliage uses alpha masking for depth/occlusion. Native tree crown
radius is at most 3 m; maximum uniform scale is 1.08 and the layout reserves
3.3 m from the boundary. Perspective overhang in an overhead image is not a
measurement of an object's ground footprint.

The exporter evaluates modifiers and actual vertices before normalizing
anchors. Each rock is grounded before the rock group is merged. This fixes
the old rotated-bounding-box calculation which left rocks 0.357923 m above
their declared anchor. The v4 output is retained as failed evidence; v5 passes.

The nine GLBs total 4,722,724 bytes, compared with 5,263,548 for v2. Tree
geometry uses two draw calls per shared variant, not one object per leaf.
Play equipment and furniture retain metre dimensions; the layout adapts
the paths, planting and amenity count, with explicit omissions when too small.

Local evidence: `C:/dev-artifacts/CityPrompt/catalogue-cycle-2026-09-05/park-v5/`.
Browser captures and verifier output are ignored under
`artifacts/catalogue-cycle/park-v5-*`. Nine lab cases cover 70 × 55 m aerial,
overhead, pedestrian and detail views; a 3% slope; 40 × 35 m, 105 × 75 m,
rotated-L and 8 × 80 m layouts. All were inspected. The narrow case omits
all amenities with a clear explanation. A fresh interaction error observer
reported no errors. The browser's older global error buffer includes failures
from changing asset roots during development and is not represented as empty.

In the existing Fort Calgary empty-field project, all nine v5 URLs returned
HTTP 200 with correct byte lengths and GLB headers. Aerial and 1.7 m ground
views were inspected. Ground sampling correctly became pending when local
tiles refined, then returned to ready with two passes and zero missing
samples. This is measured tile contact, not survey accuracy. Full route
integration and the novice release trial remain separate CAT-07/08 work.

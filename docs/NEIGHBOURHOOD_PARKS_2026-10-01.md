# Neighbourhood parks — local catalogue pilot

Two exact-reference native assemblies extend the local validation catalogue.
Both passed independent source, geometry and visual review. Publication and
human activation remain pending. Both also pass the local prepared-site runtime
matrix described below.

| Asset | Reviewed version | Native plot | Triangles |
| --- | --- | --- | --- |
| Community Allotment Garden | allotment-v006 | 36 × 46 m | See seed recipe |
| Forest Adventure Nature Play | nature-v006 | 34 × 46 m | 899,304 |

The allotment retains four growing rooms, eight coloured sheds, varied crops,
trellises, open gates and a shared orchard. Nature play retains the stream,
flat stepping stones, log crossings, rope play, tree deck and leafy tunnel,
with a separate continuous walking path and layered woodland planting.

Each complete assembly owns its ground on a prepared level platform. Plot
resizing preserves the native equipment and planting geometry. These are
static concept models. Detailed play-safety, construction and accessibility
certification are outside this asset review.

## Evidence and reproducibility

- Exact models, recipes, photographic thumbnails, geometry checks and
  independent decisions are retained under `seed/classroom-parks/` in
  `neighbourhood-allotment-v006` and `neighbourhood-nature-v006`.
- Model and image binaries use Git LFS.
- Full source images, authoring snapshots, six reimport renders and three
  1080 × 1920 boards per model are preserved externally at
  `C:/dev-artifacts/CityPrompt/neighbourhood-four-2026-10-01/`.
- Earlier failed candidates and review decisions remain intact there.
- `build_neighbourhood_parks.py` takes explicit kit, reference and output
  paths. It rejects an existing output directory and checks the exported GLB.
- `register_neighbourhood_parks.py` accepts only this finite exact-hash batch,
  validates the independent review and its evidence, and preserves prior
  registries before registration. Frontend/backend registries are mirrored.

## Checks

- Frontend native park and asset registry tests: 24 passed.
- Backend native park tests: 39 passed.
- Independent visual review: both pass, zero P0 and zero P1 findings.
- Local runtime: catalogue search/card selection, placement, moving, parcel
  resize/rotation, undo/redo and reload passed for both parks. Allotment saved
  at 48 × 56 m / 12 degrees; nature play at 42 × 54 m / 8 degrees.
- Complete assembly world scale remains 1:1 in all axes. Authored component
  scales are preserved. All 473 allotment and 662 nature-play meshes are visible.
- The prepared-site scene settles with no grounding issues and no browser
  errors. Exact assembly SHA-256 and content revisions survive reload.
- An undersized rotated allotment parcel was correctly rejected without
  changing the saved garden. Native layout geometry must fit inside the parcel.
- Runtime evidence: `parks-runtime-final.json`, `nature-runtime-framed.png`
  and browser screenshots in the external evidence root. The disposable
  project is `888a5b24-0ec2-4458-915d-757b6395d495` on localhost:5185.
- Public street connections, paid render generation and public deployment
  were not exercised. This is a static concept-model and local runtime pass.
- No public deployment, push or paid image generation.

Public files staged for the dev server are generated copies; only the
reviewed seed packages are source deliverables.

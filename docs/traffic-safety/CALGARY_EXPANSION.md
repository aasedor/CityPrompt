# Calgary safety additions — bounded authoring batch

Current release evidence: [RELEASE_VALIDATION.md](RELEASE_VALIDATION.md).
All ten candidates now pass actual application placement/save/reload and are
included in the release catalogue and selective hosted asset closure. Earlier
preview-only/Docker-blocked statements below are the preserved authoring record.

User approved the eight proposed families on 2026-10-15. This extends the current
traffic-safety initiative; it does not replace any of the 56 supplied GLBs.

Produce ten fixed native variants: speed cushion single/pair; in-street school
crossing sign; centreline-hardening assembly; high-visibility crossing sign;
green bike box/conflict strip; unlit bicycle signal; traffic-diverter assembly;
portable speed-display trailer. No paid generation. Procedural Blender recipes
reuse the existing static material-consolidation exporter and Add Details loader.

All are Calgary-inspired **concept visualization assets**, not certified replicas.
City references establish treatment type and visual intent. Unless individually
stated otherwise, dimensions, sign artwork and spacing are illustrative, not City
standard drawings. The left-turn post height is 0.9144 m (three feet), as described
on the City page. Road-marking geometry sits 4 mm above its root. Hardware remains
fixed size; position/yaw only. Lights and speed readings are static illustrations.

Sequence: dry-run → one cushion pilot → image inspection → bounded remaining
batch → GLB structural/hash/dimension audit → browser loading and roadway fixture
review → opt-in local catalogue. Actual project save/reload, terrain integration,
undo/redo and live promotion remain gated by the existing application checks and
the unavailable local Docker backend. No deployment is authorized by file QA.

Sources checked 2026-10-15:
- https://www.calgary.ca/roads/safety/speed-cushion-speed-hump.html
- https://www.calgary.ca/roads/safety/elementary-schools-traffic-study.html
- https://www.calgary.ca/roads/safety/left-turn-calming.html
- https://www.calgary.ca/roads/safety.html
- https://www.calgary.ca/roads/safety/bike-signage-signals.html
- https://www.calgary.ca/planning/transportation/neighbourhood-streets-elements.html
- https://www.calgary.ca/planning/transportation/neighbourhood-streets-policy.html

Originals, images and receipts: `D:/CityPrompt-traffic-safety-2026-10-15/expansion-*`.
Existing overlapping files were copied to `expansion-checkpoint` before edits.
Runtime acceptance and release status: **NOT TESTED / NOT DEPLOYED**.

## Creation receipt

Ten GLBs (834,544 bytes combined) and ten captured WebP previews are created.
The initial cushion pilot was inspected in Edge before the bounded full batch.
R2 fixes the school sign support spine and cushion chevron joins. Immutable R1
and R2 files remain outside the checkout. Current reviewed hashes, dimensions,
source links and thumbnail hashes are in `calgarySafetyCatalogue.json`.

All ten passed local HTTP loading, SHA-256 verification, GLTFLoader decoding,
metre-bounds and road-datum comparisons, and the production instanced draw path.
All ten also appeared together on a level synthetic roadway. The review uses
the existing SafetyVariantCards component: eight families, ten fixed variants.
Both multi-variant selectors were exercised. No captured browser errors.

Measured in Edge on this desktop, at 640 x 480 pixels and DPR 1:

| Variant | Triangles | Draws: one / 100 copies | Decoded geometry bytes |
|---|---:|---:|---:|
| Speed cushion | 124 | 2 / 2 | 6,504 |
| Cushion pair | 248 | 2 / 2 | 13,008 |
| School sign | 1,056 | 5 / 5 | 53,280 |
| Left-turn calming | 2,320 | 4 / 4 | 115,872 |
| High-visibility sign | 1,228 | 5 / 5 | 61,512 |
| Bike box | 122 | 2 / 2 | 6,588 |
| Conflict strip | 36 | 2 / 2 | 1,944 |
| Bicycle signal | 5,756 | 8 / 8 | 273,624 |
| Planter diverter | 2,856 | 6 / 6 | 143,280 |
| Speed trailer | 2,318 | 9 / 9 | 117,908 |

Zero GLB textures. Geometry bytes count attribute/index buffers, not total GPU or
process allocation. The repetition test draws 100 copies of one variant at a
time, without map tiles or shadow passes. CPU submission readings were at browser
timer resolution (0–0.1 ms); they do not establish GPU frame time or walking FPS.
Student-laptop and mobile hardware remain untested.

Checks passed: 26 frontend tests in seven focused suites; 45 detail API tests;
two hydrated GLB/thumbnail/hash checks; TypeScript and targeted ESLint. API tests
use mocked database sessions. They do not establish actual database persistence.

## Try the local candidates

Open `http://127.0.0.1:5174/calgary-safety-review.html` while Vite is running.
Choose an individual model or the roadway view, and orbit/zoom normally.
The family-card buttons select a review model; they do not write to a project.

After Docker recovers, start the existing local frontend with the process
environment `VITE_CALGARY_SAFETY_PREVIEW=true` to expose the actual Add Details
category **Calgary safety additions**. It is off by default and always excluded
from production. Backend model IDs are registered without a database migration.

Recipe: `tools/detail_catalogue/build_calgary_safety.py`.
Metadata and preview gate: `frontend/src/features/parks/calgarySafetyCatalogue.json`
and `detailCatalogue.ts`. Backend registry: `backend/app/data/project_detail_models.json`.
Browser fixture: `frontend/calgary-safety-review.html` and
`frontend/src/review/calgarySafetyReview.tsx`.

Binary copies and thumbnails remain ignored local output in
`frontend/public/street-kits/calgary-safety-concepts-v1`. Never stage that directory
wholesale. Browser captures and measurement JSON are saved in
`D:/CityPrompt-traffic-safety-2026-10-15/expansion-review`.

Actual app terrain placement, movement/rotation/deletion, undo/redo, persistent
save/reload, AI scene capture and production checks remain NOT TESTED for this
batch. Docker is blocked by the existing Windows socket failure pending reboot.
No live catalogue update, Git push or deployment occurred. These candidates are
not yet included in the hosted asset publication manifest.

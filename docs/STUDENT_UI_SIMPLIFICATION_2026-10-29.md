# Student UI simplification — local acceptance

Branch: `codex/student-ui-simplification-20261029`, based on `9075331cc`.
Local frontend: `http://127.0.0.1:5174`. Local backend: port 8000.
No deployment, push, catalogue publication or paid generation was performed.

## Results

| Request | Implementation and observed verification |
| --- | --- |
| Perpendicular street names | Labels rotate 90° from the projected source street segment. Browser checked overhead and oblique views; crowded labels may still be omitted. |
| Zoning after saving a boundary | Surrounding context is the default; **Only show zones within site boundary** clips cached geometry. Browser trial showed 57 surrounding districts and 10 clipped districts. |
| Remove AI landscaping | Removed Finish your site from object properties; retained saved landscape data and manual Add details. Source reachability review found no authoring entrypoint. |
| Beltline policy | Added official Part 1 and Part 2 ARP Land Use Concept maps. Both selectors and legends loaded; Part 2 matched the trial site and displayed geometry. See companion map-source document for editions and omissions. |
| Remove entrances and Connections | Removed reachable Connections/Review entrances entrypoints while preserving older saved data. Students can draw ordinary paths. |
| More tools cleanup | Removed the requested redundant boundary, master plan, street view, custom building/park, use-category and render controls. Browser checked remaining menu. Main catalogue, Walk and Render controls remain. |
| Details below ground | Preview and saved placement use a shared ground helper, respecting existing native datum lifts. Browser placed brick, zebra, diagonal-hatch and ladder markings; all four stayed visible and persisted after reopening. |
| Person actions | Corrected left/right targets and parent-space bone aiming. Actual hydrated catalogue rigs pass pose checks across 23 rigs, 10 articulated actions and three capture times. A close-up browser Walk check showed Eli waving with his arm clear of the chest. Offline source-geometry board includes three rigs and four actions; it is not an AI render. |
| Honest fixed-model controls | Removed unsupported plot and park outline editing. Browser checked Timber and Stone Square without width/depth fields or corner handles. Imported house retained Move/rotation with no corner handles. Adaptable controls retain validation tests. |
| Working tower heights | Preserved storey/height controls. Browser changed the disposable Brick Podium tower from 13 to 25 storeys (50.1 to 86.1 m), saved the detailed result and restored 13 storeys. |
| Flat ground polygons | Added 25 lightweight procedural finishes, including grass, snow, black pavers and concrete. Browser drew across house/park plots, changed finishes, used Undo/Redo, moved a corner and reopened the saved Snow polygon. Raised objects retain normal depth occlusion. Ground finishes are excluded from building compilation/counts. |
| Complex GLB imports | Removed arbitrary node/accessor/triangle/building-size caps while retaining structural checks, 50 MB upload and 128 MB decoded-geometry limits. The supplied 45.3 MiB Meshy GLB (1,269,266 triangles) passes actual backend inspection. New browser upload remains blocked by the extension's file-access permission. |
| Simple imported properties | Browser checked an intact 29.4 MB external House 1: Name / View Model / Delete zone only. Model preview rendered. Close clears both selections and removes handles; no automatic reopening. Rename/delete were verified through component tests rather than modifying this existing review project. |
| Quantitative report | Removed question/response authoring UI; compact Measure / Value / Status table includes buildings, floor area m²/ft², residential/retail counts and public-realm/detail quantities. Fresh browser report correctly counted one house, one residential unit, zero retail units, one park, three paths, one ground finish and four placed details. Floor area stayed explicitly unknown because no trusted floorplate exists for that exact bungalow. Earlier reports/responses remain archived. |

## Verification

- Broad affected frontend suite: **141 files / 1,439 tests passed**. Following the final imported handle/close correction: **6 files / 82 tests passed** (overlaps the broad suite).
- Backend/import/report/model-contract/ground compilation and Beltline extraction suite: **109 tests passed**. Four known warnings concern deliberately invalid geometry and the JWT library's deprecated UTC call.
- Final TypeScript check passed. `git diff --check` passed; Git emitted line-ending conversion notices only.
- Independent read-only review found no confirmed P1/P2 issues. React changes retain unconditional hooks, labelled controls, memoized/disposed textures and geometry, and lazy-loaded map data.
- Frontend, backend health and readiness endpoints returned HTTP 200. This is local QA, not a classroom release certification or live-site test.

## Evidence and test data

Main edited disposable project: `8ef6fab3-ad0b-4225-89ff-46e28921e317`.
Fresh report plan hash: `db7d35a452d9` (before adding Eli).
Imported-model review project: `79150c2b-1479-43f0-a9e1-3d28e5d801f4`; read-only panel/preview checks.
Tower trial: `5a0afdaf-2e87-4958-8ee4-31dc170aefb7`; restored original 13 storeys.

One older import trial (`22202017-d9dd-41d1-89ea-647eeef1edac`) contains previously deleted placement-building rows and explicit stale metadata. Its red massing is a pre-existing stale-data case; source GLBs remain available. No deleted objects were silently recreated.

Screenshots, source geometry previews, official map captures and review notes are in the existing private Drive parent's dated child:
[Student UI simplification and browser review](https://drive.google.com/drive/folders/17Rh9PYWrg5bhJ5-Bb5WIMudN_-aq4Rbk).

Local screenshots/logs/upload receipts are outside Git under
`C:/dev-artifacts/CityPrompt/student-ui-simplification-20261029`.
The pose review board is ignored under `artifacts/people-pose-review-20261029/`.
All delivered images are labelled screenshots or source previews. No new AI images or video originals were generated in this batch.

## Remaining browser-upload check

The browser extension rejected file selection with a requirement to enable
**Allow access to file URLs** in its Edge extension Details page. That gate was respected.
The exact user's Meshy file passes backend validation, but a new browser upload/place/render of that file is **not claimed passed**. Existing external models and their model viewer were checked successfully.

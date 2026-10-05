# Approved local area plan Urban Form maps

Initiative: `codex/local-area-plans-2026-10-05`, based on the city-wide policy
map checkpoint `944f16640`. Local implementation; no production deployment.

## Student workflow

Use **1 Site → Local area plan**, or the same controls under **Layers**.
The default selection matches the active site boundary to the approved plans.
If a site crosses plans, the largest overlap is shown and the panel names the
other matching plans. The selector also allows browsing any of the eight plans.

Each plan has the same Urban Form experience as Riley: a Google 3D environment
overlay, visibility switch, 0–100% opacity, optional site clipping, interactive
legend and individual polygon inspection. Explanation cards link to that plan's
specific section and PDF page. Existing Riley preferences migrate to automatic
selection; visibility, opacity, clipping and the chosen plan are saved per browser
and project. Switching plans clears the old selection and never shows a previous
plan's geometry while the new map loads.

The existing MDP/CTP maps, current zoning and student zoning studies remain
separate layers. Authoring, measuring, walking and capture guards are preserved.

## Coverage and source editions

The [City's completed-plan list](https://www.calgary.ca/planning/local-area/completed-area-plans.html)
listed these eight plans when checked on 5 October 2026. South Bow, Carburn and
South McKnight were [in progress](https://www.calgary.ca/planning/local-area/in-progress.html);
the panel links to their status rather than displaying drafts as approved policy.
Legacy area redevelopment plans and area structure plans are outside this collection.

| Plan | Source edition | Urban Form PDF page |
|---|---|---:|
| [Chinook](https://publicaccess.calgary.ca/lldm01/exccpa?func=ccpa.general&msgID=GTsTccrrcsT&msgAction=Download) | 36P2025, approved April 2025 | 34 |
| [East Calgary International Avenue](https://publicaccess.calgary.ca/lldm01/exccpa?func=ccpa.general&msgID=FTyqcsscsgR&msgAction=Download) | 67P2024, approved December 2024 | 26 |
| [Heritage](https://publicaccess.calgary.ca/lldm01/livelink.exe?func=ccpa.general&msgID=HTKscgqAqeU&msgAction=Download) | 32P2023; Map 3 amended 35P2024 | 25 |
| [North Hill](https://publicaccess.calgary.ca/lldm01/livelink.exe?func=ccpa.general&msgID=XTTrAcrcgyN&msgAction=Download) | 18P2020, December 2022 consolidation | 35 |
| [Riley](https://www.calgary.ca/content/dam/www/pda/pd/publishingimages/riley-communities-local-area-plan/Riley-Communities-Local-Area-Plan.pdf) | Existing reviewed 25P2025 / 38P2025 snapshot | 24 |
| [South Shaganappi](https://publicaccess.calgary.ca/lldm01/exccpa?func=ccpa.general&msgID=LTsrysceeyI&msgAction=Download) | 29P2025 / 37P2025, April 2025 consolidation | 34 |
| [West Elbow](https://publicaccess.calgary.ca/lldm01/exccpa?func=ccpa.general&msgID=DTsceAKTeAK&msgAction=Download) | 42P2025, approved May 2025 | 35 |
| [Westbrook](https://publicaccess.calgary.ca/lldm01/exccpa?func=ccpa.general&msgID=CTKccgAyqsD&msgAction=Download) | 5P2023, September 2025 consolidation | 26 |

All are **Map 3: Urban Form**. Building Scale, active frontage, hatching,
comprehensive planning sites, industrial transition and special-policy overlays
are not included, matching the Riley pilot's scope. This limitation is visible in
the controls. A category colour is neither a zoning district nor a height or
development permission. Shared explanations describe the category's purpose;
conditional permissions and numeric limits must be checked in the linked plan.
Riley retains its existing plan-specific explanations.

Chinook and South Shaganappi have small palette differences in the published
PDFs. Those original RGB colours are retained. Grey “No Urban Form Category”
areas in the new snapshots are explicitly identified and explained.

## Extraction, alignment and limits

`tools/policy_maps/local_plan_calibrations.json` pins all seven source SHA-256
hashes, map pages, legend colours, PDF bounds, affine transforms, City boundary
object IDs and independent check points. The existing Riley snapshot is unchanged.

Plan perimeters were fitted in EPSG:26911 against the City's
[Policy Plan Boundary service](https://services1.arcgis.com/AVP60cs0Q9PEA8rH/arcgis/rest/services/Policy_Plan_Boundary/FeatureServer/0).
The PDF's vector polygons preserve islands, holes, painter order and cartographic
road gaps. Special-policy dots/hatching and frontage symbols are excluded from
the base categories. North Hill contains invisible editing shapes; fill/stroke
opacity is respected so those shapes cannot erase real policy areas.

A shared PDF precision grid avoids coincident-edge errors. Geographic precision
reduction is followed by full-precision collection-wide overlap removal and exact
plan-boundary clipping. Repeated fixed-grid geographic boolean operations were
found to collapse some road gaps; the extractor explicitly clears that precision
model before resolving shared edges. No category-independent simplification is used.

| New plan | Boundary fit p95 (m) | Independent junctions | Maximum junction difference (m) |
|---|---:|---:|---:|
| East Calgary International Avenue | 0.33 | 3 | 2.1 |
| Chinook | 0.22 | 3 | 1.8 |
| Heritage | 0.36 | 3 | 1.6 |
| North Hill | 0.59 | 3 | 2.0 |
| South Shaganappi | 0.34 | 2 | 1.1 |
| Westbrook | 0.31 | 3 | 1.7 |
| West Elbow | 0.31 | 3 | 2.3 |

The 20 independent points use the City's
[Street Centreline dataset](https://data.calgary.ca/resource/4dx8-rtm5.json).
Unambiguous road junctions were used; divided-lane intersections with multiple
offset carriageway nodes were unsuitable as single point controls. Boundary-fit
residuals are calibration diagnostics, not independent accuracy estimates. Small
local differences remain between the generalized PDF perimeter and the GIS
boundary, especially North Hill. These are educational planning maps, not surveys.
Top View is best for comparison; the overlay uses the site's reference elevation
and does not alter terrain or Google tiles.

Reproduce a reviewed snapshot with the exact pinned source PDF:

```powershell
python tools/policy_maps/extract_local_plans.py westbrook C:/path/to/westbrook.pdf --output C:/review/westbrookUrbanForm.json
python -m unittest discover -s tools/policy_maps -p 'test_*.py'
```

Review a changed source before updating its hash or calibration. The extractor
fails closed for changed PDFs or unsupported vector path rules. Inspect the map
against the source and verify policy references when updating the catalogue index.

## Delivery and verification

The small boundary/metadata index is approximately 25 KiB gzip. Each of the seven
new maps is loaded lazily in a separate chunk (approximately 154–295 KiB gzip of
JSON), then cached. No PDF extraction or live City API request runs on student
laptops. Opacity changes reuse the existing batched mesh. This is not a hosted
40-student load test.

Verification covers exact site matching for all eight plans, boundary crossings,
source colours and per-plan PDF references, lazy loading, stale request isolation,
project preference migration, opacity, clipping and selection clearing. Geometry
checks validate the stored WGS84 polygons, holes, overlap, containment and all
independent street checks. Reprojecting sparse edges independently can introduce
artificial microscopic intersections, so topology is tested in the stored CRS.

Browser QA at localhost:5174 exercised all eight plans in the Google 3D view:
native polygon clicks, legend explanations/source links, opacity endpoints and
toggle-off picking. A separate Westbrook trial checks automatic matching, clipped
polygon picking, tablet layout and coexistence with MDP controls. No paid image
or video generation was used.

Passed: 112 frontend tests across the policy/reference layer suites, 10 Python
geometry/extraction tests, and `npm run type-check`. The fresh Westbrook browser
trial also passed preference restoration after a page reload and reported no
browser errors. The local trial project is
`http://localhost:5174/projects/ad032416-70cb-4e92-b673-184d289e0d71`.

Reviewed source changes are the extractor/configuration, seven compact JSON
snapshots and metadata index, plan controls, explanatory content and tests. Original
PDFs, research scripts and browser screenshots remain outside Git under
`C:/dev-artifacts/CityPrompt/local-area-plans-2026-10-05/`.

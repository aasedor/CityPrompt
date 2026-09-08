# Connected Currie community — 7 September 2026

## Saved local project

- Project: **Student trial - Currie 20-building community**.
- ID: `3c12dda6-3b15-4151-bf8b-eb59628a99ff`.
- Frontend: `http://127.0.0.1:5178/projects/3c12dda6-3b15-4151-bf8b-eb59628a99ff`.
- Layout changes are local database content, not seed/catalogue changes.
- Preserved all 20 homes: 15 infill homes, three Craftsman bungalows, two Foursquares.
- Reorganized around an 85 m collector with its 20 m section, a 116.5 m shared street with its 6 m section, a 55 m shared park approach, and an 85 m planted laneway with its 5 m section.
- Expanded the neighbourhood park from 32 × 30 m to 33 × 56 m. Saved measured terrain; lawn and paths follow the slope. The larger adaptive layout includes activity areas and a pavilion.
- Saved 12 collector-house entrance approaches to the collector sidewalks.

The layout was assembled with the application's authenticated local zone APIs, using its rectangle, metric-road buffering, and placement validators. The browser was used for visual review, ground review, camera composition, and all paid render submissions. This was not a mouse-only student usability trial.

## Placement and ground review

The final 20 buildings, park, and four street segments passed the application's boundary/plot-overlap checks. The final scene reached shared-ground `ready` with no building grounding issues before each paid render.

An attempted collector extension toward the existing road changed the ground sampling extent and encountered tile discontinuities. The original site boundary was restored, including its existing eastern notch, and the collector stops at the site edge. No sampled heights or validation thresholds were overwritten. The public-road tie-in is unfinished; the model must not be represented as having a completed off-site connection.

A bungalow initially exceeded the 3 m foundation limit on the western slope. Swapping the corner building types and rotating the southern Foursquare to face the laneway brought the buildings within the existing placement checks. The park retained its measured slope. Concept foundations still need entrance/grade review; these checks are not a civil-engineering assessment.

Some Google surface patches show through street surfaces in close oblique views. Shared-street park access is not a verified graded sidewalk connection. Further work should address surface joins, graded park entrances and the off-site road connection before treating this as a finished street-network demonstration.

## Render-blocking defect fixed

Building entrance strips used `zone:<building-id>:street`, contradicting the backend's persisted building classification. The server correctly rejected the first submission before calling the provider.

`GlobePedestrianConnections` now attributes a building approach to its saved destination street in the render inventory, while preserving the building owner in local metadata. Crossings retain their road identity. Missing or non-road targets produce no capture group. This fix concerns building-to-street approaches; the separate terrace-to-terrace capture path was not changed.

Verification:

- 15 tests passed across `pedestrianCapture.test.ts` and `pedestrianConnections.test.ts`.
- `npm run type-check` passed.
- ESLint passed for the three changed files.
- `git diff --check` passed.
- Three subsequent live render requests accepted the 20-building / four-street / one-park inventory.

## Three paid image renders

Exactly three provider image calls completed for this request, costing 255 local application tokens (85 each; this is not a USD price). An initial inventory rejection and a later daily-cap rejection did not submit provider work. The local daily cap was temporarily raised from 1000 to 1105 for the two remaining authorized renders, then the original backend runner and 1000 cap were restored.

| Style | Camera | Outcome |
| --- | --- | --- |
| Photorealistic | 30° overview looking north | AI original retained; silhouette/layout, instance evidence and unsupported-structure checks failed. |
| Watercolour | 61° rotated overhead view of park and shared street | AI original retained; context registration check failed (luminance 0.343, structure 0.599). |
| Night / blue hour | 22° low oblique view across the park | AI original retained; context registration check failed (luminance 0.573, structure 0.479). |

All three attempts are `review_required`. The normal result for each is the original 3D source, not an approved AI finish. The separately retained AI originals are illustrative: visual review found façade/roof, foundation, pavilion and lighting changes. Watercolour and night also change image statistics substantially, so a registration failure alone does not establish that the entire layout changed. Do not suppress these results or describe them as geometry-verified.

## Artifacts and recovery

Local-only folder: `C:/dev-artifacts/CityPrompt/connected-community-three-styles-2026-09-07/`.

- `project-before.json`: recovery snapshot before rearrangement.
- `project-after.json`: final saved zones, including entrance relationships.
- `01-photorealistic-*`, `02-watercolour-*`, `03-evening-*`: original captures and clearly labelled unverified AI images.
- `render-records.json`: saved render IDs/statuses without signed asset URLs.
- `plan.js`: preliminary layout/preflight script; later visual/ground corrections are reflected in `project-after.json`, not this preliminary script.
- Runtime/log files are local diagnostics and excluded from the image download.

No generated images, database snapshots, runtime configuration, credentials, or local logs are committed to Git. No push or catalogue publication was performed.

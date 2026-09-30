# Building contact placement audit — 2026-09-30

Initiative: `codex/building-edge-placement`, based on `b50671294` in the active house-flex-pilot checkout. No source models, heights, assets, user projects or catalogue publication statuses changed.

## Findings and policy

All 26 current building records were checked against their exact native dimensions and revisions. The padded editable plot was being treated as occupied architecture. Road snapping also reserved an additional 3 m outside the road polygon, and Community 3D rejected overlapping padded building plots even when the models themselves were separate.

The new contact envelope is separate from the saved plot. Seven reference-supported urban types allow near-zero contact on both sides. The Plateau duplex allows it only on the right; its left-side entrance space remains reserved. The other 18 retain their side space. Local left/right are viewed facing the authored front. All current exact native buildings may front the constructed street edge; sidewalks remain fully inside the protected street envelope. Rear plot space remains reserved.

Reference inspection covered buff-brick infill, SoHo, Streamline Moderne, timber-screen townhouse, Beltline, Montreal duplex, Grand Deco Cinema, Gilded Terracotta Tower, Machiya and Halifax clapboard. The latter two retain side clearance because their inspected sources show side glazing/eaves or a detached yard. Unreviewed side conditions retain their existing plot clearance. This is a concept-placement policy, not a fire-separation or zoning certification.

| Current building | Left side | Right side |
|---|---|---|
| Buff-brick infill | Near-zero | Near-zero |
| Crystal brewhouse | Retain plot space | Retain plot space |
| Earth-sheltered museum | Retain plot space | Retain plot space |
| Halifax clapboard house | Retain plot space | Retain plot space |
| Machiya cafe and gallery | Retain plot space | Retain plot space |
| SoHo cast-iron loft | Near-zero | Near-zero |
| Streamline Moderne corner | Near-zero | Near-zero |
| Terraced garden mid-rise | Retain plot space | Retain plot space |
| Timber community hall | Retain plot space | Retain plot space |
| Timber-screen townhouse | Near-zero | Near-zero |
| Beltline mixed-use mid-rise | Near-zero | Near-zero |
| Calgary Modern Infill | Retain plot space | Retain plot space |
| Side-by-side duplex | Retain plot space | Retain plot space |
| Plateau stacked duplex | Retain plot space | Near-zero |
| Brick courtyard entrance building | Retain plot space | Retain plot space |
| Post-war bungalow | Retain plot space | Retain plot space |
| Edwardian Foursquare | Retain plot space | Retain plot space |
| Rammed-earth timber infill | Retain plot space | Retain plot space |
| Blue glass office tower | Retain plot space | Retain plot space |
| Vancouver balcony and podium tower | Retain plot space | Retain plot space |
| Grand Iron & Glass Market | Retain plot space | Retain plot space |
| Living-Roof Aquatic Centre | Retain plot space | Retain plot space |
| Gilded Terracotta Tower | Near-zero | Near-zero |
| Nordic Roof-Garden Apartments | Retain plot space | Retain plot space |
| Tuscan Arcade Villa | Retain plot space | Retain plot space |
| Grand Deco Cinema | Near-zero | Near-zero |

## Runtime behavior

- A 1 m attraction radius closes small gaps to a 0.02 m numerical tolerance. Approved parallel side faces can align, and the authored front can align with the constructed outer street/sidewalk edge. Two bounded passes handle a side and street corner together.
- Complete mesh bounds include eaves, stairs, aprons and marquees. These are never cut off to make the facade meet a line. Recessed walls can therefore retain the source model's intentional gap behind a projection.
- Native geometry, orientation, plot coordinates and height programmes are not changed. House footprint scales use their bounded authored programme. Vancouver uses its plot-driven uniform horizontal fit (including compiler rounding), not its unscaled source dimensions.
- Neighbour placement, pedestrian route obstacles and the backend Community 3D overlap guard use the same reviewed policy. Existing connected building paths and park approaches remain reserved.
- Saved plots must still fit the site boundary, matching the server's existing boundary contract. No permission to extend across the site boundary was added.
- Unknown revisions, legacy repeated houses, unsupported height/scale edits, non-rectangular frames and custom models retain conservative source polygons. Existing saved buildings do not move automatically.
- Expanding a house footprint into a neighbour or street is rejected before saving. Height-only changes keep the existing height workflow.
- Native preview now applies the assembly's declared scale, matching saved model placement.

`frontend/src/data/buildingPlacementEdges.json` is the reviewed policy, with a packaged copy in `backend/app/data/buildingPlacementEdges.json`. Backend parity and frontend catalogue tests guard drift. Content revisions, measured dimensions, footprint programmes and storey programmes are pinned. Future asset revisions must be reviewed before receiving these contact rules.

## Verification

- PASS: 93 focused frontend tests across 10 suites: contact placement, original placement/geometry, automatic entrances, pedestrian connections, house/tower storeys, house footprints, street surface ownership, reshape controls and native park reservations.
- PASS: frontend TypeScript type-check.
- PASS: 28 backend tests for contact geometry, source-geometry fallback, packaged-policy parity and Community 3D scope/overlap guards.
- The automatic-entrance fixture was updated from retired `infill_home` to the current Post-war bungalow, preserving actual entrance/path assertions.
- Known unrelated test limitation: `reviewedEntrances.test.ts` cannot collect because it requests retired `clay_beltline_brick_midrise`. That suite was not counted as passing or rewritten to imply that retired asset remains in the current catalogue.

### Local browser pilot

Disposable project: `http://127.0.0.1:5183/projects/1d240496-b141-45e0-a2ae-0a3926408c7a` — **QA - Building edge placement**.

Used ordinary student controls to draw a cleared site, draw Neighbourhood Main Street, place two SoHo buildings and reopen the project. The first run exposed the backend padded-plot overlap rejection, which was fixed. After restarting the local backend, recompilation and reload show both detailed models and **3D saved**. Saved-data measurement reports a 0.0201 m side gap, zero intersection area, and a 0.0191 m first-building-to-street gap. The second building deliberately remains farther from the street (1.6662 m, outside the 1 m attraction radius). The two-axis corner behavior is covered by automated tests. This is a pilot, not browser acceptance of all 26 buildings.

A drag was exercised; no formal undo/redo acceptance is claimed because development hot reloads interrupted that session. No paid renders were submitted. During the backend restart, model requests briefly returned 500 and displayed placeholders; a fresh reload recovered both models. The reused browser error buffer also contained older park hash failures and elevation fallback warnings, so it is not presented as a clean whole-app console audit.

Evidence stays outside Git in `C:/dev-artifacts/CityPrompt/`: `building-edge-reloaded.png`, `building-edge-final.png`, `building-edge-saved-zones.json`, `building-edge-measurements.json`, console/error logs and the source metadata audit. No heavyweight generated assets were added to the source tree.

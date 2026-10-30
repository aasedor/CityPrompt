# Nine source-derived bridge routes — local review, 30 October 2026

This updates the remaining nine imported bridge styles. Original fixed source identities and GLBs remain readable. New local variants draw between two endpoints, preview in 3D, adapt only their declared structural span and retain bridge-owned materials, end structures and limited landscaping. Broad surrounding roads, buildings and river/bank scenery are excluded.

## Browser evidence

Disposable project: `fbdad5c0-a2e9-47e8-b229-0c5ead33a6e7`, on the QA frontend at port 5177 and PostgreSQL API at port 8004. All nine were selected, drawn, previewed, finished, edited using their endpoint handles, saved and reopened through the browser. Independent API readback confirmed the exact recipe, source and module locks. Original user projects were untouched. The site boundary was an API-created fixture, not a tested student boundary-drawing flow.

| Exact local variant | Drawn span (m) | Edited span (m) | Browser preview / save / edit / reopen |
| --- | ---: | ---: | --- |
| `brick_arch_viaduct_route_v1` | 143.717 | 154.064 | PASS |
| `rail_through_truss_route_v1` | 151.811 | 161.964 | PASS |
| `stone_arch_road_bridge_route_v1` | 121.348 | 133.305 | PASS |
| `steel_truss_road_bridge_route_v1` | 34.902 | 37.155 | PASS |
| `tied_arch_shared_bridge_route_v1` | 65.275 | 68.117 | PASS |
| `planted_green_bridge_route_v1` | 189.654 | 200.160 | PASS |
| `cable_stayed_cycle_ring_route_v1` | 177.292 | 184.150 | PASS |
| `swooping_cycle_flyover_route_v1` | 341.805 | 350.101 | PASS |
| `weathering_steel_v_footbridge_route_v1` | 57.198 | 60.193 | PASS |

Brick viaduct Undo/Redo restored and reapplied its endpoint change. Other exact variants' Undo/Redo have not individually been exercised. An undersized V bridge kept its two points, displayed range guidance, then saved after correction. Entering, moving in and exiting scene walking mode worked; this is not a pass for walking every complete bridge. The free 3D export produced an exact 1280×656 PNG. The automation's generic download event did not resolve the inline image; the unchanged PNG bytes were recovered from the displayed image. Screenshots and this source capture are labelled separately from offline rendering originals. The browser console returned zero error entries at the final check.

## Source and runtime checks

- 29 derived modules, 32,171,172 bytes, exact source provenance; immutable original source GLBs unchanged.
- 89 focused backend tests, 100 focused frontend tests, TypeScript and touched-file ESLint passed.
- Source extraction: 24 straight, 7 green, 15 topology tests passed; two interrupted-install recovery tests passed.
- Backend hydration: 81 explicit hash-locked fixtures verified, including the nine source originals; three inventory tests passed. The old limit of 80 was adjusted to this exact finite 81-file cohort.
- Production packing: 60 tests passed. Pending local starter rows and their exclusive dependencies stay outside the production roster; shared dependencies are retained. Production budgets remain unchanged: 466.6 KiB initial JS, 8445.2 KiB total JS (limit8448), 2440.4 KiB largest chunk, 190.2 KiB CSS.
- Independent follow-up review found no actionable issues. Verified temporary-file writes and atomic replacement resolve its prior interrupted-install finding.
- 59 offline full-resolution PNGs show actual TypeScript runtime geometry at minimum/native/maximum lengths, including low stair/support views. They are neither browser screenshots nor AI photographic outputs. Source contact/ray/traversal checks do not replace interactive walking acceptance.

## Open acceptance and publication scope

These are local development pilots. They are not published live. Original production discovery and publication guards remain intact. Full per-style walking traversals, all individual Undo/Redo sequences, hosted novice trials and paid image/video fidelity comparisons remain NOT TESTED. Vehicle/rail bridge endpoints remain elevated; automatic road/rail junctions and newly engineered at-grade ramps are unsupported. Source-specific span limits remain enforced. The ring, S and V retain their distinctive shape while adapting within their supported bounds. Ring corridor reservation conservatively encloses the whole ring, rather than representing pavement width. Existing saved fixed bridge scenes are not silently migrated.

The runtime inventory was regenerated from tracked metadata. This sparse worktree still contains historical missing/LFS-pointer assets; its inventory is not proof of a fully hydrated release package.

## Delivery

Private evidence folder: https://drive.google.com/drive/folders/1LkMzL7FZ8xDbsracJD8T7GmzjnHR4fJ0

Local delivery and API readback manifests are kept outside Git under the remaining-bridge-routes-20261030 QA batch. No paid image or video submissions occurred in this batch.

# Vacant Currie grounding continuation — 19 September 2026

**Batch A remains unaccepted.** Live testing reproduced a pedestrian entrance
discontinuity: the first western Craftsman bungalow's native stairs end on the
top of its generated foundation, leaving a further vertical drop to surrounding
ground. The building contact solver reports ready. Neither a settled aerial
view nor a successful exact capture establishes a usable entrance.

Worktree: `C:/dev/CityPrompt-grounding-edit-race`, branch
`codex/grounding-edit-race-hardening`, tested production source at `0a29ccf90`.
The tree started clean. Docker, frontend `/login`, and backend `/health` were
healthy; existing processes were reused. No production code, catalogue, RLASM
asset, dependency, or terrain threshold changed. This is a documentation and
local-fixture checkpoint. No push or paid AI generation occurred. Existing Maps
context was used; its actual billing remains unavailable and the earlier budget
ceiling is unchanged.

## Fixtures and final state

- Main vacant Currie fixture: `f5bffc94-def9-4c43-942e-9ae7411872e9`. The original
  eight-vertex boundary is unchanged. Seven houses, one park and one street
  remain. `Shared street west 2` was rotated through the UI from 90 to 95 degrees;
  the final saved fixture retains 95 degrees. Its original coordinates are in
  `currie-continuation-baseline.json`. No other main-fixture zone geometry changed.
- Further disposable copy: `bfcc05d2-b5b8-4447-8fe3-79f0f6e60a3d`, named
  `Vacant Currie — disposable boundary and cancellation QA`. It was created with
  the Currie boundary and one copied reviewed bungalow. A 0.40 m concave notch
  was imported into its boundary to cross the house; the imported boundary was
  checked as a subset of the original parcel. The house was then moved 22 m
  north through the ordinary zone API. The copy's boundary was restored before
  park cancellation testing. Its temporary park is deleted in the final state.
- Protected originals and the unpublished catalogue waves were not edited.
  No source fixture population scripts were rerun. The new edge helper refuses
  to create a second copy when its manifest exists.

Evidence root: `C:/dev-artifacts/CityPrompt/grounding-batch-a/`. The existing empty
context screenshots, broad-boundary failure evidence and original fixture
manifest remain preserved. Frozen camera poses are in
`currie-frozen-cameras.json`; some agent-browser JSON files contain a JSON string
and require a second parse. Helpers and binary evidence remain outside Git.

## Results

| Check | Result | Evidence and limits |
| --- | --- | --- |
| Existing runtime and main fixture baseline | PASS | `currie-continuation-baseline.json`, `currie-continuation-initial.png`. Ten zones and seven building records; shared ground ready after two stable passes, no building warnings. |
| Bungalow foundation and entrance, east and west | FAIL for entrance continuity | `currie-house-pedestrian-east-settled.png`, `currie-house-pedestrian-west.png`. The eastern stair approach has a visible drop beyond the native bottom step. Western contact is substantially closer. Do not flatten the parcel or stretch the model to conceal this. |
| Rendered foundation against shared measured surface | Bounded measurement | `currie-foundation-measurements.json`, collected after the 95-degree rotation and reload. First bungalow foundation top is about 0.040–2.136 m above the shared surface at sampled mesh vertices. Across seven foundation meshes, maximum absolute bottom-vertex discrepancy is about 0.027 m. This measures generated foundation vertices against the shared surface, not entrance tread height, a new raycast of every visible tile, or surveyed bare earth. |
| Park paths, trees and furniture | Bounded visual PASS | `currie-park-pedestrian-southwest-real.png`, `currie-free-capture.png`. Inspected visible tree bases, path/lawn surface and furniture from the southwest. All perimeter directions and individual contacts remain unverified. |
| Street surface | Partial | Visible in `currie-close-house-initial.png` and the house approach view. A complete longitudinal surface/contact and street-end connection measurement was not performed. |
| House rotate → Undo → Redo → reload | PASS | `currie-after-{rotate,undo,redo,reload}.json`, `currie-rotated.png`. Only the selected house's coordinates changed. Undo restored exact original coordinates; Redo matched the rotation exactly; reload matched Redo. Dimensions and counts persisted. |
| Live tile refinement display stability | PASS within sampled interval | `currie-refinement-a.json`: 392 samples over 39.559 s; `currie-refinement-b.json`: 151 samples over 15.170 s. Both observed sampling and ready states. Seven building groups remained present and visible; maximum sampled origin displacement was 0 m. Monitoring at 100 ms does not prove absence of every sub-frame flicker or vertex change. |
| Capture begun during refinement | PASS | `currie-refinement-b.json`: capture began in sampling state, completed in ready state after 6.819 s. Last safe houses remained visible. A separate settled free park capture succeeded in about 1.45 s. No image/video generation endpoint was invoked. |
| Narrow concave boundary crossing | PASS | `currie-edge-notch.json`, `currie-edge-notch-verified.png`, `currie-edge-notch-capture.json`. The 12-vertex domain produced `incomplete_footprint_ground` and rejected capture with the house-specific grounding message. |
| Recovery after moving fully inside | PASS via API edit and reload | `currie-edge-recover-building.json`, `currie-edge-recovered-close.png`, `currie-edge-recovered-close-capture.json`. House moved 22 m north; warning cleared; close capture succeeded with 15,380 proposal pixels. This is not a live pointer-drag recovery test. |
| Park navigation cancellation | PASS for observed persistence | `currie-edge-add-park.json`, `currie-park-cancel-before-navigation.png`, `currie-park-after-navigation.json`. Navigation occurred while park alignment was visible; subsequent API snapshot retained its pre-navigation revision. Returning restarted alignment. No deterministic late provider callback was injected. |
| Park deletion while alignment pending | PASS under interrupted context | `currie-park-delete-pending-confirmed.json` records `parkPending: true` immediately before the UI deletion. The park remained absent in `currie-park-deleted-reloaded.json` and `currie-park-deleted-after-settlement.json`. An earlier deletion attempt completed after alignment and is not cancellation evidence. |
| Context interruption and restoration | PASS for this bounded attempt | Google tile requests were temporarily aborted only in the QA browser. Capture rejected in 8.008 s with a tile-settlement retry message. The route was removed, the project reloaded, and ground returned ready without house warnings (`currie-context-restored-state.json`, `currie-context-restored.png`). The temporary park remained deleted. |
| Full retry ceiling; every pause/resume and archetype-change race; full mixed-object slope matrix; detached pads, enclosed-site and exact-edge live cases | NOT TESTED in this continuation | Existing automated tests remain relevant but do not replace these browser checks. |

The wide, single-house disposable view twice returned “No visible compiled 3D
proposal” despite a visible small house; a closer view captured successfully.
This is preserved in `currie-edge-recovered-capture.json`. It does not establish
a grounding failure. Check the proposal-pixel threshold and wording before
deciding whether the wide-view rejection needs a product change.

Fixture setup had two corrected helper errors (polygon roundoff and initially
assigning a non-persisted `coordinates` attribute rather than the PostGIS
`geometry`). The authoritative notch evidence is the API-readback 12-vertex
polygon and filenames containing `notch-verified` / `notch-capture`. Earlier
`currie-edge-notch-pending.png` and `currie-edge-notch-settled.png` precede the
persisted notch and must not be used as crossing evidence.

Page-error checks were empty after clean reloads. Intentional tile interruptions
are expected network failures. `currie-network-sanitized.json` contains only
method, host, query-free path, status and timestamp; it is cumulative and should
not be presented as a per-test request count. No raw authorization headers or
network dumps were saved as evidence.

Final return to the main Currie project used the frozen east pedestrian camera
(`currie-final-same-camera.png`); the entrance discontinuity persists at 95 degrees.
`currie-final-validation.json` confirms the unchanged site boundary, all nine
proposal polygons inside it, no positive-area overlaps, and unchanged building
heights/storeys/names when compared by ID. The final clean reload recorded 1,257
requests, no HTTP error statuses and one request without an HTTP status; do not
describe that as proof that every request completed. No page errors or paid
render POSTs were recorded. Ground was ready with two passes and no solver issues.

## Next bounded work

1. Reproduce the bungalow entrance drop at the frozen east camera, tracing native
   stair/entrance geometry and generated foundation contact. The solver currently
   checks footprint support and its existing 3 m foundation limit, not a continuous
   route from the lowest entrance tread to terrain. Define the connection behavior
   using the existing entrance/terrace systems before changing geometry or claiming
   accessibility. The optional terrace pilot is not automatic entrance repair.
2. Finish street-end/approach and multi-direction park contact inspection. Measure
   the actual rendered tread/approach against the current surface where possible.
3. Exercise remaining park context-setting, pause/resume, queued edit and rapid
   archetype-change cases on this vacant parcel; preserve bounded attempts and API
   write/revision evidence. Test the full retry ceiling separately from the single
   interrupted capture above.
4. Complete the missing live boundary shapes and mixed-object slope matrix. If a
   product defect requires source work, make one failing regression, a coherent
   fix, focused checks/typecheck/lint and a browser recheck. Existing 141-test
   verification was not rerun because production source was unchanged here.
5. Keep Batch B blocked on Batch A acceptance. Do not publish or claim full
   grounding/accessibility acceptance from this evidence.

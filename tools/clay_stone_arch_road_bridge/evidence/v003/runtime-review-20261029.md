# Runtime review — stone-arch-road-bridge v003

Date:29October2026. Agent student simulation on Edge,1681x1233,mouse/keyboard.

Exact source commit:`7f30f4852c461c289fe5d305a472f853337a24f1`. Original GLB SHA256:`5300077e633cecc901ef86bb0a78e0b7bd0dce0588c613becbb2195b92337d6d`. Ownership revision:`5aab6b165834398fbe0f2a7d154e0a65edd21bb112849235be65f3c953ad7337`. Fixed native metres; move/rotate only. Prepared level terrain only. Source bytes unchanged; retained original triangles:48576; original scene triangles:76684.

Project:`http://127.0.0.1:5176/projects/467025e9-4f3c-432c-ba76-066a52467eb2`. Disposable test project,234x147m approximate drawn boundary. Source assets use the deployment-version lineage; production publication is still gated.

Follow `docs/ARCHETYPE_RUNTIME_INTEGRATION.md` and `docs/ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md`. This is local integration evidence, not keeper or engineering approval.

| Gate | Status | Evidence / limits |
| --- | --- | --- |
| C1 Exact identity | PASS | Actual original-GLB SHA256 and per-material retained-face checks; same ownership in hover/placed model; frontend/backend identity pins. |
| C2 Dimensions / transforms | PASS | Compact component bounds, unit-scale renderer, locked dimensions;15degree UI rotation. |
| C3 Ground support | NOT TESTED | Level prepared parcel only; full terrain/edge matrix remains open. |
| C4 Late results | NOT TESTED | No pending-result race test. |
| C5 Pedestrian / public road access | NOT TESTED | Fixed authored crossing; automatic external approaches and surveyed grade are not supplied. |
| C6 Edit / Undo / save / reopen | NOT TESTED | Placement,15degree rotation,save tested; fullUndo/Redo/deletion matrix incomplete. |
| C7 Failure / recovery | NOT TESTED | Identity guards tested; complete live failure matrix open. |
| C8 Capture | NOT TESTED | Free exact source PNG content captured; multiple low/aerial views and actual browser Download action not fully tested. No paid AI image. |
| C9 Controls | PASS | Size disabled; unsupported corner handles removed; rotation allowed. |
| S1 Metric section | NOT TESTED | Exact source geometry measured; no civil/design compliance claim. |
| S2 Arbitrary routes / junctions | N/A | Fixed native architectural object, no bending/stretching/junction contract. |
| S3 Public connection / grade | NOT TESTED | Student placement on flat terrain alone does not prove public connection. |
| S4 Clearance / targets | NOT TESTED | No complete vehicle/access-clearance trial. |
| B1–B5 / P1–P4 | N/A | This delivery is a fixed street/crossing, not a building or park. |

## Bounded matrix

- Original source hash and retained architecture regression:PASS.
- Ordinary picker,drop,rotate,save:PASS.
- Save/reload: PASS for compact-r002; exact15degree control and actual complete model reselected after clean reload.
- Native low/detail view and source capture:PASS for compact-r002 source PNG content and separate close screenshot; old unsupported-bank diagnostic excluded.
- Unsupported sloped terrain,public-road approach,irregular-site exclusion,near-boundary snapping,delete/Undo/Redo/interrupted-save:NOT TESTED.
- Paid image/video:N/A,not authorized for this batch.
- Fresh-install DB/bucket seeding:N/A,hash-pathed public assets rather than building library. Backend manifest parity:PASS.

## Evidence and review

External evidence:`C:/dev-artifacts/CityPrompt/claude-crossings-practical-20261029`. Shared review folder:https://drive.google.com/drive/folders/1XWdPXl6pEhU_uojJXorA8_t-c2Gxv1BU . Delivery receipts are external in`delivery-manifest.json`.

Original independent clay review is preserved unchanged in`independent-review.md`. Fresh independent code/source-ownership review found two stone bridge defects (missingfootways,orphanvehicleglass); both were corrected and independently rechecked. A further independent visual/source diagnosis identified missingbankabutments. Only the stone bridge has an explicit finite runtime support adaptation; originals remain unchanged. No keeper approval is implied.

Compact-r002 adds two closed bank supports and two thin asphalt caps. Their footprints are bounded intersections of the original bank recipe; source recipe SHA256 and exactpolygons are in the ownership contract. Four solids,400 newtriangles; actual runtime total48976. Independent check:closedwithzero unpairededges,17.8m full-widthcontact at each outer springing. Clean browser reload,15degree controls and final exact source recapture passed.

Final bounded verification:64frontend tests passed,1unrelated hotelasset test skipped because its local GLB remains an LFS pointer;19backend tests passed;TypeScript passed. Independent runtime-completeness pixel review of allthree actual browser captures found no obvious extraction gaps; hiddenfaces,engineering,accessibility and fullkeeper review remain unassessed.

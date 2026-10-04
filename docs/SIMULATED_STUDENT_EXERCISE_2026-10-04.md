# Currie Commons — student tool trial

## Result

Created a new community through the normal signed-in CityPrompt editor on a vacant portion of the Currie field. The saved community contains an older Charcoal Gable Fourplex, the local-trial Three-Storey Brick Walk-Up, Buff-brick infill, a bent 16 m residential street and an irregular pocket park. Existing projects were preserved. This exercise found real runtime failures; it is a partial working-prototype result, not classroom acceptance or approval of every catalogue model.

- Project: `9638ee5a-f0cf-422d-a608-c35b378c23e3`
- Open: `http://127.0.0.1:5176/projects/9638ee5a-f0cf-422d-a608-c35b378c23e3`
- Source: `C:/Users/andre/.codex/worktrees/public-realm-recovery/CityPrompt`
- Branch: `codex/public-realm-recovery`
- Evidence: `C:/dev-artifacts/CityPrompt/student-community-trial-2026-10-04/`

All project geometry, settings, placements and report responses were created through visible UI controls and pointer/keyboard actions. No geometry was injected through an API or application store. Developer tools were used for diagnosis and source fixes. The local account balance remained 1,000 tokens. No paid image generation or model generation ran; the 20-building automation remains paused.

## Student workflow

Used New Project and the CFB Currie address autocomplete, drew a six-point boundary on vacant ground, and confirmed a roughly 1.1 ha site (138 × 87 m). Selected Clear site for redevelopment. The saved proposed level is approximately 1102.147 m WGS84 ellipsoid.

Selected Local residential · no parking from Streets and drew a bent route. Placed the three housing designs from Buildings. The native Teaching demonstration garden did not fit the remaining space: the editor showed an overlap warning, so the placement was cancelled. Used Flexible pocket park instead and drew a five-point outline, approximately 85 × 22 m, south of the street. Generated and applied the free Neighbourhood gardens site landscape.

Enabled Connect to a public road and dragged the street's eastern end toward the visible existing road edge. Present correctly calls this a **proposed** connection. This is a visual concept connection, not surveyed junction or vehicle-turning verification.

## Tool results

| Tool or flow | Result and evidence |
| --- | --- |
| Login and opening the editor | Initially failed on expired optimized dependency chunks; repaired cache isolation, restarted the owned frontend, then passed normal login/navigation/reload. |
| Boundary drawing and site setup | PASS. Irregular boundary, prepared level and saved site landscape survived reload. |
| Building, street and park pickers | Used all three pickers. Selected models rendered in the community after delivery recovery. This is not a visual review of every picker card. |
| Native park overlap rejection | PASS. Oversized garden was rejected and cancelled; no undersized fixed park was forced into the site. |
| Flexible park creation | Initially failed with a 503 for shared bike-rack geometry. Restored all five exact tracked equipment assets and added audit coverage. Park then rendered and survived reload. |
| Building rotation, Undo and Redo | PASS for Buff-brick infill, 0 → 5 degrees, Undo → 0, Redo → 5. |
| Fractional fixed-plot rotation | Initially blocked for the walk-up: exact 25.148 m depth displayed as 25.1 m and failed the minimum. Repaired validation and preserved exact saved dimensions. Normal UI rotation to 5 degrees saved and survived reload. Eight reshape tests pass, including exact fractional dimensions. |
| Recoverable deletion | PASS. Deleted the walk-up, restored it with Undo, then reloaded; its detailed model and 5-degree rotation returned. |
| Walking inside the brick walk-up | PASS for entering the open front doorway and moving into its lobby through normal walking controls. Return to entrance and Exit walk worked. Stairs, upper floors and every-room access were not tested. |
| Walking inside Buff-brick infill | FAIL. WALK INSIDE is offered, but reports “No walking route is available for this model.” See `03-infill-walk-inside-unavailable.jpg`. |
| Buff-brick entrance picking | FAIL. Picking the visible low entrance step was rejected with “Choose the lowest entrance step on the selected catalogue house.” Cancelled without saving an approximate entrance. |
| Review entrances | All three housing entries reported no selected entrance. Complete building-to-sidewalk routes remain unresolved. |
| Review ground | PASS for measured original heights (approximately 1097.5–1103.7 m), unchanged prepared level and saving retaining edges. After reload, Close gaps at site edges remained checked with “Using saved edge measurements.” The first accessibility-index attempt closed the dialog unexpectedly; retry through the semantic checkbox worked. Measured hillside park option remained unavailable (0 of 1 repeatable park measurements). |
| Site landscaping | PASS for Generate 3D Site Landscape, preview, Apply landscape and Save changes; models stayed clear and visible. |
| Layers | PASS for Calgary zoning and nearby existing streets/paths loading. One zoning area and a separate route reference layer appeared. Both overlays can be hidden. |
| Measure | PASS. Two visible street points produced an 87 m concept measurement; Clear removed it. |
| Version History | PASS for inspecting saved creation/property/position events. History restore commands were not exercised; toolbar Undo/Redo were. |
| Guide | Opened and advanced from Choose your site to Lay out a street; instructions matched the available controls. |
| Planning report and response | PASS. Free report generated with five proposal areas, quantities and limitations. Saved an “Adapt it to our vision” response explaining unverified access. It survived reload. After later edits, the report correctly warned that it describes the earlier plan. |
| Free exact 3D capture | PASS for producing and displaying the exact capture. Saved displayed PNG evidence as `exact-community-capture.png`. Normal download acknowledgement timed out in IAB, so the download flow remains NOT VERIFIED. |
| Paid AI image generation, video, team invitations and custom uploads | NOT TESTED. No image generation credits spent and no invitations or sharing sent. |

## Runtime repairs and prevention

The first failure came from multiple worktrees sharing `node_modules` and Vite's optimized dependency cache. The live preview and SSR catalogue audit now use separate ignored cache directories. Running the catalogue audit left the live preview cache metadata unchanged, and regular project navigation continued afterward. The external trial launcher also uses its own cache.

The previous delivery audit missed five shared park equipment GLBs because they were absent from the starter dependency list. They were still Git LFS pointers. Hydrated the existing exact files rather than regenerating them. The audit now reads the actual `SHARED_PARK_EQUIPMENT` registry, requires manifest SHA-256 locks and includes these runtime dependencies for procedural parks. A regression test exercises the real catalogue audit and checks all five locks for every procedural park choice. Missing/corrupt/pointer assets are already rejected by the delivery guard.

Prepared the external v003 delivery packet and restarted only the owned port-5176 frontend against it. The source catalogue audit passes **95 choices, 329 distinct image/model dependencies, zero failures**. The ten local fixtures retain their separate sealed launcher binding; this count does not mean the full historical archive or every live model placement was tested.

Validation: eight narrow ReshapePanel tests, seven delivery tests, TypeScript and lint for touched files pass. Generated screenshots, captures, audit receipts and packet bytes stay outside Git. The five equipment models are existing LFS assets; this repair introduces no new generated model geometry.

## Outstanding work

Buff-brick walking metadata and entrance-step picking need repair and a separate runtime trial. The three building-to-sidewalk connections remain unverified. Normal downloads, paid rendering, video and broad novice usability remain open. Retaining edges and the proposed public-road connection are concept geometry requiring physical/design review. A report or visible model does not certify accessibility, local policy conformance or classroom readiness.

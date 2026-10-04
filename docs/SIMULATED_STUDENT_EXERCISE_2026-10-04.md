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
| Walking inside Buff-brick infill | Initially failed with “No walking route is available for this model.” Walking metadata repair and the continuation trial now pass entry into its furnished ground floor after reload. Original failure: `03-infill-walk-inside-unavailable.jpg`. |
| Buff-brick entrance picking | Initially rejected the visible landing. The continuation repaired missing mesh-click forwarding in the local-review renderer; a real entrance paving pick now saves and survives reload. |
| Review entrances | Initially reported no selected entrances. All three buildings now have saved measured approaches to the residential sidewalk; see the continuation below. |
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

## Continued browser trial: entrance connections

Continued through the same disposable project's visible controls. Fixed two renderer omissions: local-review models did not forward real mesh hits to the entrance picker, and they did not render or report the shared entrance approach. Hits now use the unrotated foundation frame and preserve their ray for occlusion checks. Approaches use the existing ground and clearance checks; invalid or removed street targets retire the approach and its review. No model bytes, sealed fixture reviews or catalogue definitions changed.

Selected the outer authored entrance paving for Buff-brick infill and the brick walk-up, then the older fourplex's first entrance. The fourplex includes paving beyond its stairs; the picker correctly rejected the interior stair foot. Updated the instructions to describe the paving edge without relaxing physical checks.

| Building | Saved local anchor, metres | Reloaded review |
| --- | --- | --- |
| Buff-brick infill | x = -0.853, y = -8.725, height = 0 | Two generated steps; 0.20 m descent; 1.80 m clear width; support up to 0.06 m |
| Three-Storey Brick Walk-Up | x = -0.353, y = -12.574, height = 0 | Two generated steps; 0.20 m descent; 1.80 m clear width; support up to 0.06 m |
| Charcoal Gable Fourplex, primary entrance | x = -9.555, y = -8.675, height = 0 | Two generated steps; 0.20 m descent; 1.80 m clear width; support up to 0.06 m |

All anchors retain native dimensions (`scaleWithPlot: false`) and target the residential street. The walk-up connection's Undo removed it and Redo restored it. Reload retained all three detailed models and their measured approaches. Walk inside passed again for the infill and walk-up after reload; movement, Return to building entrance and Exit walk worked in the walk-up. The existing fourplex entry was tested in the preceding walking repair. These are ground-floor entry trials, not proof of every unit, room or upper floor.

Free Export current 3D view displayed the intact connected community. Saved its displayed PNG as `continuation-v002/exact-connected-community.png`; no paid generation ran. The editor was left visibly open on Currie Commons in Design mode. The account still showed 1,000 tokens and the generation automation remained paused.

Validation: **58 focused tests in six files**, TypeScript and touched-file lint pass. New tests check the actual rotated hit transform and approach lifecycle, including removal of an invalid target. The read-only delivery check passes **105 catalogue choices, 359 distinct image/model dependencies, zero failures**, including the ten sealed local fixtures. All **19 ModelLibrary assets** pass exact storage readback. These delivery counts establish availability and byte identity, not physical access certification for every model.

Evidence is outside Git in `C:/dev-artifacts/CityPrompt/student-community-trial-2026-10-04/continuation-v002/`. `all-three-reloaded-ready.png` is the completed reload proof; `all-three-after-reload.png` is an earlier loading frame and is not pass evidence. `continuation-results.json` records the outcomes and limits.

## Outstanding work

Every room, upper floors, all fourplex unit entrances and continuous walking along every possible sidewalk route remain unverified. Normal downloads, paid rendering, video and broad novice usability remain open. Retaining edges and the proposed public-road connection are concept geometry requiring physical/design review. A report or visible model does not certify accessibility, local policy conformance or classroom readiness.

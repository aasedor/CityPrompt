# Student beta trials — 6 September 2026

## Verdict

Pick, place and reshape is usable on the tested open site. Before expanding the catalogue, prioritize ground preparation, render fidelity and placing assets in constrained spaces. The five paid image trials produced attractive AI attempts, but none passed as an automatically accepted faithful finish: one retained a repaired candidate for review, and four returned the original 3D view as the safe final. This is a small exploratory sample, not a production failure-rate estimate.

No catalogue assets were added or published. Source changes are on `codex/student-beta-sites`, based on `f99e88cfb`. The original OneDrive checkout was left untouched.

## Test environment and method

- Frontend: `http://127.0.0.1:5178`; isolated backend: port 8002. Existing Studio Smoke Student account.
- Created three projects, boundaries and assets through the browser UI. Used API reads and renderer diagnostics to inspect saved results and ground failures, not to author fixtures.
- Desktop 1600×1000 and a short 1024×768 tablet check. This was browser automation, not a human touchscreen trial.
- Five image calls of the permitted ten: `gpt-image-2`, high quality, 1696×992 output. Each deducted 85 application credits, 425 total (10040 → 9615). Application credits are not dollars; provider dollar spend was not independently reconciled.
- An initial attempt failed locally because the isolated launcher disabled media credentials; it did not reach the provider. A separate external launcher enabled the existing OpenAI credential while preserving the isolated database and disabling other media providers.
- The CLI wheel action did not deliver observable wheel events. Close-up trials used DOM WheelEvents through the app's normal wheel handler. This is an automation limitation, not evidence of a broken student mouse wheel.
- Development hot reload reset a planned close-up before render 3. It is recorded as a wider repeat, not a close-up. Render 4 is the genuine cropped/occluded trial.
- This was a bounded exploratory test, not exhaustive certification of every control. No invitation emails, production writes or video generation were performed.

## Sites and student actions

### A — open field

Project: `4986a3f4-8653-4d71-b303-9c1724b46da0` — **Beta A - Empty lot and render fidelity**.

Selected the 750 9 Ave SE search result and panned onto an open field. Drew a roughly 70 m square boundary. Placed a Craftsman bungalow, widened it from 15 m to 30 m, and correctly obtained two homes instead of one oversized house. Added a rammed-earth/timber infill, neighbourhood park and local street. Backspace successfully removed an unwanted street point before completing the line.

The default 39 m Beltline mid-rise could not fit the remaining space. Rejection prevented an invalid placement, but the hidden boundary and lack of a pre-placement size adjustment made recovery confusing. Cancel worked; a smaller archetype could be placed.

Render, saved originals/finals, Report, saved responses to report suggestions, Team, Help and Guide controls were exercised. Team opened with required email validation; no invitations were sent. The report counted the repeated bungalows, but reported an unresolved detached recipe for the newer infill and incomplete/zero known footprint/floor-area quantities. Do not treat those totals as reliable grading evidence yet.

### B — hillside

Project: `7e314bbc-cebd-4d9c-a8fe-a67cf48e7622` — **Beta B - Sloped hillside**.

Selected 1204 Salisbury Ave SE and panned onto the open slope below the road. Drew a boundary and placed a 15×20 m post-war bungalow with Follow terrain. Ground sampling rejected a discontinuity (reported maximum slope 3.433 and local residual 3.213 m); the building stayed hidden and the free capture refused to proceed. No paid request was made on this site.

This does not prove that all sloped sites fail. Google photogrammetry includes roofs, trees and sharp mesh features, and the sample alone cannot distinguish those from natural terrain. The failure needs a ground-preview/recovery workflow, not relaxed validation. Revisited after the message fix: both the map badge and free capture showed the actionable discontinuity explanation.

### C — existing buildings / redevelopment

Project: `c4477d4b-f0dc-4e0a-9a3e-1730b75a161f` — **Beta C - Existing building redevelopment**.

Fictional software test around the existing visitor buildings near the 750 9 Ave SE result, not an actual redevelopment proposal. Placed a 39×39 m Beltline mid-rise and 32×40 m teaching garden over existing roofs. Follow terrain rejected the discontinuity (maximum slope 5.441; residual 11.191 m).

Selected the boundary, chose **Clear site for redevelopment**, and saved. Existing tiles inside the boundary were removed and the new models appeared on a common platform. Prepared elevation was 1024.552 m, distinct from original roof placement heights of approximately 1029.693 and 1028.781 m. This avoided simply placing everything on the old roof. It still produced abrupt platform edges and cut vegetation at the boundary; it is not a verified grading solution.

## Render trials

Times below are backend request durations, including generation and checking; they are not isolated provider latency measurements.

| Trial | Scene/style | Time | Saved result and observation |
|---|---|---:|---|
| 1 | A, wide photorealistic | 112 s | Repaired candidate retained with review required. Broad composition plausible; fine details too small for strong validation. Custom instructions had been lost when the panel was closed. |
| 2 | A, wide watercolour | 132 s | Source fallback. Original attractive but added dense planting and changed facade detail. Context registration failed; stylization itself can also affect this check. |
| 3 | A, wide photorealistic repeat | 111 s | Source fallback; validator reported a new unsupported structure. Not counted as the intended close-up because hot reload changed framing. |
| 4 | A, close photorealistic; park/pavilion partly cropped, buildings/tree occlusion | 106 s | Source fallback. Original mostly retained house positions and did not visibly relocate the cropped park facilities, but invented a foreground sidewalk/landscaping and changed facade/roof materials. |
| 5 | C, night; after prompt fix | 106 s | Source fallback. Original retained the main building/garden arrangement but invented an entrance path, trees and lights on undeveloped ground despite explicit instructions. Prompt changes alone did not resolve fidelity. |

All originals remain available for review. A fallback is not a successful styled render, even though it protects the authored geometry. The night example is particularly useful: the AI makes the site look more coherent by designing connections the student never drew.

Render identifiers (final / AI original):

1. `449b69f7-4438-4b78-ad70-fa2a924790e2` / `434d075d-f6b2-46de-80c4-ab5d451644c2`
2. `cb92f248-b0a6-4491-b29f-85b7cb6b9ecb` / `6ba31963-f04a-4843-9502-00890664749b`
3. `dbf629f0-c652-4fda-8e25-0875a5e56327` / `7f640aaf-ffe5-4168-86af-f111f3225d39`
4. `99d77fc4-b3ec-430a-8557-d35e43a0c3d1` / `1e52e08b-d933-4ac4-967a-61736f85b223`
5. `541223d1-014a-4415-a134-b3efee5927dd` / `972d1a46-59ba-497f-8657-bb27c5d921db`

## Fixes included

1. Keep render style and custom instructions in a per-project session draft. Closing the panel to move the camera, or reloading during the session, no longer discards them. Malformed or unavailable storage is handled; projects do not share drafts.
2. Show the site boundary while placing an asset or drawing a street, including in Clean 3D. Temporarily suppress that placement outline during direct, street and route captures so it cannot contaminate the image.
3. Carry the ground sampler's failure reason into the capture error and map badge. Explain abrupt height changes and intentional redevelopment rather than suggesting indefinite waiting. Ground thresholds remain unchanged.
4. Shorten the photorealistic prompt and preserve the existing material family instead of suggesting replacement materials. Add same-camera instructions against completing hidden objects, inventing connections or adding furniture/planting. Reprojection styles retain their separate behavior. Geometry validation remains enabled.

## Recommended next implementation order

1. **Ground preview and recovery:** display sampled ground and suspicious roof/tree hits before placement. Offer an explicit prepared platform/grade preview with boundary transitions. Keep legitimate slopes usable without silently accepting bad height samples.
2. **Fidelity pilot:** use a fixed source/camera and compare bounded rendering settings. Separate geometry failures from expected colour/light changes; night and watercolour need appropriate validation. Evaluate material-only masked finishing and deterministic 3D presentation as alternatives. Preserve unverified originals for review and never silently label invented geometry faithful.
3. **Pre-placement reshape:** size/rotate a ghost asset before placing it, show its footprint and boundary clearance, and explain which constraint prevented the drop. Students should not need a larger site just to place and then shrink an asset.
4. **Report completeness:** resolve quantity metadata for every published family, and distinguish unknown quantities from zero. Verify repeated-home totals, entrances and pathway recommendations against the actual scene.
5. **UI polish:** refresh the credit balance after a render, clarify that saved variants and gallery final counts differ, and coordinate gallery/render panel placement on short tablet screens. The tablet overlap was navigable but awkward.

## Verification and evidence

71 tests passed across `useRenderDraft`, `GlobeAIRenderPanel.direct3d`, `direct3dCapture`, `sharedGroundCapture`, `SharedSiteGroundProvider`, `renderZoneVisibility` and `useDirect3DRender`. TypeScript checking passed. Targeted lint of the new draft hook and touched render/ground helpers passed. No uncaught browser page errors were reported during the checks.

Final browser recheck: while a bungalow placement was active in Clean 3D, the boundary was visible in the map and absent from the successful free Beauty capture. Cancelled the unplaced asset afterward. The hillside free capture displayed the new discontinuity explanation. Render draft persistence was also checked by closing and reopening the panel.

Screenshots, downloaded originals/finals, sanitized render audits, ground diagnostics and isolated runtime logs are outside Git at `C:/dev-artifacts/CityPrompt/student-beta-2026-09-06/`. They are local evidence, not published catalogue deliverables. No heavyweight generated output is included in the source commit.

# Planner demonstration rehearsal — 8 October 2026

Project: `2ff7afd8-090a-4435-a604-c5d775235356`, **Kensington Courtyard · planner demonstration**.
Local URL: http://127.0.0.1:5183/projects/2ff7afd8-090a-4435-a604-c5d775235356
Generated evidence: `C:/dev-artifacts/CityPrompt/planner-demonstration-2026-10-08/` (outside source control).

## Changes found and verified during the rehearsal

- `7790c7493`: new site boundaries default to level redevelopment. Existing explicit terrain choices are retained. Browser-created boundary showed Clear site for redevelopment at 100% opacity.
- `dd8904d39`: automatic scene compilation preserves a generated Site landscape, including its preset and stale-refresh signal. Two regression cases failed before the fix; 221 relevant backend tests passed afterward.
- `6f9b8024f`: low route-video cameras use geographic vertical rather than inheriting the overhead map's north-up vector. The previous preview was sideways and correctly rejected before billing. The corrected 27.2 m route, at 6 m height, produced upright 1920×1080 / 24 fps / 8-second source video and passed provider preflight.

## Student workflow exercised

1. Create a project and inspect existing zoning and Riley policy before drawing a boundary.
2. Draw a roughly 1.1 ha site; verify default cleared, flat placement surface.
3. Inspect the site's Direct Control designation and the Riley Neighbourhood Commercial polygon with its policy explanation and sources.
4. Draw and save MU-2, M-H1 and S-SPR proposed districts. Click the proposed polygons and review catalogue matches. Change a district and save it.
5. Place six buildings: two Beltline mixed-use mid-rises, two SoHo cast-iron lofts, a Brick Corner Grocery and a Machiya cafe/gallery; one Rustic Pocket Garden; an Asphalt shared path and a Brick courtyard path.
6. Rotate a building and undo it. Repeatedly place three trees and a bench with the details picker remaining open. Select, move and rotate a tree, then save.
7. Enter walking mode along the central path, in the garden and by the shops; capture street images from those views. Enter the grocery directly with the ordinary Walk tool, move forward and turn inside; no separate entry button is needed.
8. Check MDP mapping, 5A network vectors, transit routes and stops. Click stop 8045 and verify its serving routes (4 and 104). Turn the layers off.
9. Retrieve the 2026 property assessment: two intersecting properties, $32,270,000, 79.37% mapped coverage. The saved report explicitly distinguishes this from acquisition cost or the value of the proposed buildings.
10. Generate the planning report, review Riley/proposed zoning comparisons, save a student response, and download the printable HTML. Reopen the project and verify persisted objects, four details, assessment and zoning. Reapply Urban landscape after the compilation fix, reload, and confirm that the generated preset, 4,616.22 m² treatment and flat preparation survive. Final report `bb17c186-1163-4e59-b8f2-e7a30b2e4da6`, plan hash `6a3cdd20ec40`, was generated after this verification; its downloaded HTML is in the evidence folder.

## Still-image results

Six paid Sunburst image calls; all saved and downloaded. Both AI originals and original 3D/source evidence remain available. Most outputs retain a review-required fidelity label: visually attractive AI images are not proof of exact geometry.

| View | Reviewed AI image ID | Local file |
| --- | --- | --- |
| Central path, eye level | ddad187f-285d-4e1a-ae92-de6a9dfcebc1 | street-1.png |
| Oblique aerial | 8b9ae22d-d2d4-4d2d-8b5a-15f84d8b4a7c | aerial-1.png |
| Photographic overhead plan | 2af49254-4756-4144-8739-ff7c36eb24e6 | aerial-2.png |
| Wider neighbourhood aerial | 26f43662-9570-4077-a370-66f7881b3f8b | aerial-3.png |
| Garden / pergola, eye level | b5dcdfb2-ed2f-4659-aa1f-79f87cfb770e | street-2.png |
| Grocery and cafe street frontage | 215641a4-4c40-44f8-ad61-e48d1fc66121 | street-3.png |

The overhead image and garden street view are especially useful for the planner discussion. AI finish adds small landscape/material details and can change signage; use the editable 3D scene for the authoritative design.

## Video status

Kling saved-render animation `3bb51f8d-6dcf-4f0b-8ec8-aa55fc23b496` completed: H.264, 2008×1028, 24 fps, 5.04 seconds, silent. Recovered from the persisted provider receipt after the panel had been closed and the backend restarted; no duplicate generation was submitted. Five sampled frames retained the main rooflines and facade divisions. This is a generated camera move from a still, not an exact-route claim.

Omni route attempt `6c2db640-b655-4922-92c3-f82cb736256c` was rejected with HTTP 403 because Google flagged the configured Gemini API key as leaked. No usable video was returned; replace that key before using Omni again. Do not retry it automatically.

Seedance route attempt `99e418ac-e9e2-498e-9e71-9ab3a3773d70` submitted once through the UI using the corrected high-quality preview and three views. Completed and saved. Actual output is H.264, 1280×720, 24 fps, 8.04 seconds, silent; 1080p describes the source capture, not the provider output. Browser playback reached readyState 4 without a media error. The MP4 was downloaded from persistent storage and sampled at one-second intervals. All eight samples show an upright forward journey through the intended corridor, with no obvious gross facade collapse. Its appearance remains close to the native 3D scene rather than photorealistic. The reported 79.8/100 image similarity is not geometry verification. Generation took approximately 10.7 minutes. No job remains pending; the failed Omni attempt stays visible in history.

## Verification and practical limits

- 87 default-boundary / properties / prepared-ground frontend tests passed.
- 20 camera, video controls and quality tests passed after the route fix.
- TypeScript passed after both frontend changes.
- 221 backend assembly and landscape tests passed.
- Kling focused verification: 8 passed, 11 skipped (do not count skips as passes).
- Git LFS pointer-only style examples and policy-map assets restored from the existing local cache; no source change or new generated assets were staged.
- Production build passed, including catalogue contract, render-style examples and 12 citywide policy maps / 724 hydrated images. Bundle budgets passed: initial JS 471.1/600 KiB; total JS 7199.7/8448 KiB; CSS 171.6/175 KiB. Vite retains advisory large-chunk warnings. Final browser checks confirmed landscape persistence, ordinary interior walking, report export and completed video playback. Stills and videos were captured before the final landscape treatment was reapplied; the editable project and latest report include that treatment.

Planning questions are retained rather than hidden: the MU-2 designation needs a height modifier; one placement plot is partly outside its proposed study district; the fixed park layout raises an access-path question; floor area and dwelling counts are unknown for some catalogue entries. This is a conceptual student exercise, not a permit or valuation assessment.

## Review package

Open `review.html` in the evidence folder for all six stills, both videos, the downloaded planning report and the editable-project link. `community-browser.png` and `walking-interior.png` document the final app workflow. `route-video-browser.png` records the completed provider result. Generated media and local logs remain outside Git. Source fixes and this QA record are committed locally only; no deployment or push was performed.

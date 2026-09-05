# Student render review — 5 September 2026

## Outcome

All four authorized provider requests completed through the student UI: two image renders, one street-view image, and one eight-second video. No generation retries or additional paid image/video calls were made. The images are attractive but fail visual design-fidelity review. The video is the strongest result, retaining the principal building, street and park arrangement with modest finish improvement.

Project: `9535da89-4b5c-4839-aa7f-ccde56f1eded`, **Catalogue acceptance — build a community**, on the Fort Calgary field. Four individual houses across three building plots, one neighbourhood park and one local street. No new catalogue families were activated.

## Evidence and review

Ignored local evidence lives in `artifacts/catalogue-cycle/media-review/`. `review.html` is a standalone visual comparison, including source and AI video players. `provider-ledger.json` records three OpenAI image-edit requests and one Gemini Omni interaction, all HTTP 200, with returned usage. `project-media.json` and the provenance files preserve the saved project results. The temporary media backend was stopped afterward; the normal local backend again has image/video provider keys disabled.

| Output | Student framing | Visual finding | Delivered behavior |
| --- | --- | --- | --- |
| Image 1 | Close oblique park and community | Swaps pavilion/play-area positions; adds houses and roads; changes infill appearance | Existing aerial checks returned the original 3D capture; AI original retained |
| Image 2 | Tighter homes/street view | Adds a planted traffic island and new paths; changes public realm despite clarified prompts | Original 3D fallback; both saved results immediately appear after the gallery fix |
| Street view | Pin on the park-side sidewalk, looking north across the street | Moves park equipment behind the houses; changes building materials/details | The old street branch returned an unverified AI image, exposing a verification bypass now fixed |
| Video | Two route vertices through the park toward the street; low-flight mode, 6 m | Main placement and facility sides remain consistent; materials and minor facade details still change | Eight-second, 24 fps, 1280 × 720 AI video, saved and playable |

The deterministic video source was rendered at 2560 × 1440 and downsampled to 1920 × 1080. Its route starts between the play area and pavilion and approaches the street trees and homes. The provider's output is 720p despite the 1080p input. The app reported a similarity score of 81.5/100 (`stable`); this is not certification of geometric accuracy. At close range, the older street trees show conspicuous foliage planes and stylized bases in the original 3D scene. These should be improved in the asset initiative rather than hidden by invented AI scenery.

Both image views and street view demonstrate that words and reference images do not guarantee exact building identity or occlusion. The second image used the clarified prompts and a different camera; it is not a controlled measurement of prompt improvement. The stricter street verification was implemented after its one allowed paid image and validated with provider-free regression tests, not another purchased image.

Audit files: `audit-1-source.png` through `audit-3-source.png` are actual server-recorded input captures. `image-1-provider.png` through `image-3-provider.png` are untouched provider responses. `audit-*-returned.png` record what the service returned. `video-source-0.mp4` and `video-provider.mp4` hold the source and generated videos; extracted frames support inspection.

## Implemented fixes

1. Default the globe street-view panel to a single Direct 3D request. Keep the legacy comparison explicit and label its two-image behavior.
2. Add **Preview 3D view**, a free eye-level capture before generation. Hide a previous preview when pin position or heading changes. Rendering remains disabled while its preview capture is in progress.
3. Forward the street panel's people/vehicle choices to the Direct request; hide its unused Google Street View context checkbox in Direct mode.
4. Retain and expose the saved provider-original response in the Direct adapter, aerial review button, street previews, and project gallery callbacks. Mark server-saved street previews as saved to avoid duplicate manual saves.
5. Remove contradictory capacity/layout freedom from park/street render references and backend prompt assembly. Scene-context prompts identify existing interfaces and leave missing paths to the planning report and editable model.
6. Remove the street-view content-sanity-only bypass. The input is already an eye-level capture, so its finish uses the same registered, masked checks and RLASM source protection as other same-camera renders. Unverifiable geometry returns the source; the original AI image remains separately reviewable. Sparse context may cause conservative fallbacks.

These changes improve the workflow and protect returned imagery. They do not solve the general problem of unconstrained full-scene AI hallucination, and they do not retroactively alter the saved street attempt.

## Verification

- Five focused frontend suites: **32 tests passed** (street panel, Direct adapter, reference collection, public-realm context, Direct render panel).
- `npm run type-check`: passed.
- Street/presentation backend suites: **19 tests passed**. Added regression coverage for invented facilities in street-view context; checks require unchanged exterior pixels and retained provider originals.
- Two focused backend prompt tests: passed.
- Browser: performed all paid submissions from the UI; inspected free street preview, immediate AI-attempt access, image gallery persistence, video preflight, playable generated clip and its saved record. A development page reload occurred during the street request; the server completed and preserved its result, recovered through the project gallery without a second submission.
- React review: new preview work is user-triggered; no new global listeners or polling in production components; controls are labelled and keyboard-accessible; async capture state prevents overlapping preview/render work.
- `git diff --check`: passed before checkpoint.

## Recommended next initiatives

1. Improve native 3D materials, contact shadows and park-edge transitions, and replace the older street-tree kit. Faithful native exports should be presentation-worthy without depending on AI reconstruction.
2. Add explicit house-entrance-to-sidewalk connections in the editor and a missing-access finding in the planning report. Let students approve and edit paths in 3D.
3. Prioritize deterministic route video with optional enhancement. Keep native/AI comparison visible. Pilot object-masked finishing on one building before scaling to complete scenes.

This is local-only work on `codex/student-render-review`. Generated media remains ignored. No push or deployment.

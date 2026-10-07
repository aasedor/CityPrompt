# Drone and bicycle route preview — 2026-10-05

Local initiative: `codex/drone-bicycle-route-preview-2026-10-05`. Builds on the separate [classroom performance](CLASSROOM_PERFORMANCE_REHEARSAL_2026-10-05.md) and [flexible park](FLEXIBLE_PARK_SERIES_2026-10-05.md) checkpoints. Cityprompt.ca is the owner's older Render deployment; this work has not been pushed or deployed.

## Student behavior

Present offers **Video preview · free** even when classroom services defer finished video generation. A student captures the current scene, chooses a camera, clicks route vertices and prepares an exact local 3D journey. Draft 720p is the starting quality for basic devices; High Quality remains an explicit 1440p-to-1080p choice. Both preserve the existing eight-second, 24 fps, 192-frame timeline and download control.

**Drone fly-through** retains its conservative aerial offset and eased beginning/end. Dense pointer samples are reduced by travelled distance so they do not concentrate route controls where the pointer moved slowly.

**Bicycle ride** uses a forward, level camera 1.6 m above the resolved route surface, the existing 35 mm street projection and constant travelled distance over time. An unusable route or a route exceeding 56 m in eight seconds is rejected before lens/renderer changes and expensive capture. The preview reports route distance, average speed and camera height. Route resolution retains the existing prepared-site ground logic and capture guards. These controls do not establish collision-free cycling or solve route clearance on every natural slope.

Free local previews can show a simple park without pretending it has architectural detail. The architectural source-quality check remains part of finished enhancement admission. Scene revision, model identity and ground-readiness guards still apply to capture. Changing the scene or route invalidates the previous guide; overlapping capture remains deduplicated.

When server capabilities are absent or fail to load, finished generation stays disabled and video history is not requested. Provider buttons are disabled and the action says **Finished generation unavailable**, rather than incorrectly reporting an exhausted quota. API schemas and prompts recognize bicycle motion; existing motion IDs remain compatible. No paid provider test was performed.

## Verification ledger

- Forty-six focused frontend tests pass across nine files: panel, workflow, route sampling/speed/terrain, eye-height/heading, fixed-frame encoding, render quality and preview ownership. The panel tests use mocked image/canvas/capture data to check free-preview behavior without provider calls; they do not certify real media pixels.
- Thirty-seven backend tests pass across Omni, Seedance and internal enhancement regressions, including bicycle request acceptance and source timing.
- TypeScript, touched-file ESLint, production build and bundle budgets pass. Current clean build: initial JS 460.0 KiB, total JS 6,767.7 KiB, largest chunk 1,795.6 KiB, CSS 168.5 KiB. Vite still warns about large 3D/map chunks; passing the project budget is not device performance acceptance.
- Ordinary Edge controls in the isolated Currie project `45e678b9-4898-4ef5-a611-bec132511a3a` rejected an overlong bicycle route of 154 m before capture. The existing scene view remained intact. No shared database or user project is edited.
- A Draft drone guide completed in the browser, reporting 21.7 m and 9.8 km/h average. The browser connection was lost before its offered file could be reviewed; no drone download or media-pixel acceptance is claimed.
- A short bicycle guide completed, reporting 16.3 m, 7.3 km/h average and 1.6 m eye height. The ordinary **Download preview** control saved an MP4 in Downloads. Its 13,899,064 bytes match the offered guide, SHA-256 `bd926b506241b7caa5ccbe249f5dffc8cb50e43fe90814c0439a8e7ec29df44e`. FFprobe and independent decoding confirm H.264, 1280 × 720, 24 fps, all 192 frames and exactly eight seconds. First/middle/last frames show a level forward journey over the prepared ground; adjacent decoded frames change throughout. This is a short, clear-ground integrity pilot, not collision or cinematic-fidelity acceptance.
- Actual bicycle media remains visually sparse, with obvious distortion in the surrounding ground-level Google photogrammetry. Those limits are preserved in the external contact sheet. No finished presentation-quality claim is made. The browser reported no captured console errors; project renders remained zero and displayed tokens remained 1,000.
- The dedicated trial backend runs with `CLASSROOM_RELEASE=true`; all provider credentials are empty and an additional local middleware rejects video/image POSTs. The browser visibly offers the free preview with finished generation unavailable. Generated packets, recordings, screenshots and the private fixture database are outside source control.

## Remaining acceptance

The automated browser produces slow frames, including Draft route preparation lasting minutes. The UI now describes Draft as lighter capture and warns that exact-route rendering can take several minutes; Draft guides are labelled Draft source. Actual class laptops, iPad Safari, the hosted Render instance and the classroom network still need testing. High Quality capture, browser/codec fallbacks, mixed building/street scenes, sharp turns, clearance and varying terrain need bounded visual review. Finished AI video remains experimental and is not a classroom release claim. Stills remain the first presentation target; this initiative does not certify the separately unreviewed park still export.

External local evidence: `C:/dev-artifacts/CityPrompt/overnight-2026-10-04/bicycle-draft-guide.mp4`, its `.review.json` and `.contact-sheet.png`, and `bicycle-preview-browser.png`. These files, private fixtures and generated build/delivery directories are deliberately absent from the source commit.

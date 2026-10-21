# Omni 1.1 bicycle-speed people pilot — 2026-10-21

## Scope and result

One additional user-authorized LOCAL paid generation completed. No push, deployment, provider change, purchase, subscription change, or production data/credit change. Existing native test scene reused; six buildings on both sides of a 175.298 m CityPrompt street. Source and reference binaries remain outside Git.

User requested a 25 km/h bicycle camera, cinematic/hyper-real people on sidewalks, and only the base video plus a simple prompt. The free route capture measured approximately 55.5 m / 8 s, displayed 25.0 km/h, at 1.6 m eye height. The source is 1280×720, 192 decoded frames at 24 fps. Forward corridor inspected at 0/2/4/6/7.9 s with no solid-object collision observed. Generated-world speed cannot be independently measured.

Exact provider text (21 words):

> Make this a hyper-realistic movie scene with people walking naturally on the sidewalks. Keep the camera movement from the base video.

The Omni payload contains only the video and this text. Internal scene contracts and capture validation remain local/server-side. The new opt-in **Use only my prompt** setting defaults off, requires nonempty text and Omni preview-video mode, invalidates free preflight when changed, persists in the attempt, and preserves old request-ID replays. Default prompt behavior remains available.

## Durable receipt

- Local project: `c4864790-f468-505a-9148-96f7b48022e4`.
- Attempt: `11d43d42-1b85-4556-8b3f-6a4a33228126`.
- Request: `e0c86722-f256-423a-a666-1316f3edea1a`.
- Provider/model: Gemini / `gemini-omni-1.1-flash`, draft 720p.
- Started: 2026-10-21 02:20:08 UTC; completed 02:21:12 UTC.
- Output: 1280×720, 192 decoded frames, 24 fps, 8.0 s; 7,201,017 bytes.
- Submitted source SHA-256: `e85377033695373e45fb602ea80fbbb446794aad83fa002f34bfacb1f586a4c7`.
- Output SHA-256: `1d0a58cd6306bfcc57e4dee4c985e29191017c9b36b6fa3c7de1c41f246a8f59`.
- Exactly one admission/provider call in this batch. Prior batch receipt/allowance archived before installing a fresh one-call local test allowance; previous attempt retained.
- 50 internal LOCAL test tokens allocated/consumed. No production balance changed.
- Usage: 44,714 input tokens (44,688 video + 26 text), 46,336 video output tokens, 314 thought tokens. Approximate usage-based provider cost US$0.8808 at the official rates recorded in the preceding research note; invoice not verified. UI output allowance estimate US$1.0136 plus inputs is an estimate, not a billing cap.

## Visual assessment and limitations

Cinematic appearance improved: photographic pedestrians, fuller trees, softer natural lighting, textured paving and shopfront detail. Sampled framing remains a forward street journey. Both source and output played to their eight-second end in the comparison browser with readyState 4, no media errors, and 1280×720 decoded dimensions. Saved output reopened from the actual CityPrompt project gallery after page reload, its media URL matched the new attempt, and playback reached the end.

This is NOT an exact architectural preservation pass. Omni changes facade openings/materials, replaces distinctive curved glass roofs with flat glazed forms, invents a distant skybridge/context, changes planting beds/road markings, and adds crossing geometry. Some pedestrians enter the roadway despite the sidewalk request. People appear photographic at this scale, but fine faces, anatomy and frame-by-frame gait are not independently validated. No claim of film-production quality or exact generated speed. The automatic image-similarity score ~48/100 is not a realism or acceptance metric.

## Verification

- Red: exact-prompt backend regression failed because the option did not exist; UI test failed because the checkbox did not exist.
- Green: 63 backend tests across `test_omni_video.py`, `test_video_recovery.py`, `test_video_media.py`, `test_video_fidelity.py` passed. Mock provider assertion checks exactly two inputs (one base video + exact text) and one call/replay.
- Four `VideoGeneratePanel.test.tsx` tests passed, including prompt-mode change invalidation and exact prepared request field.
- Frontend type-check and scoped ESLint passed.
- Vite production build passed using the configured hydrated public root, with output outside the source tree and no public asset copying. Existing chunk-size warnings remain.
- Independent scoped review found no blocker. Its minor non-Omni API flag-validation inconsistency was fixed before the paid trial.
- Free browser preview, free API preflight, ONE paid submission, decoded source/output media inspection, sample-frame comparison, comparison playback, actual app save/reload and output identity checked.
- Scoped diff check passed. Existing unrelated hydrated LFS changes preserved.

## Evidence and local viewing

`C:/dev-artifacts/CityPrompt/omni-bicycle-people-2026-10-21/`

- `CityPrompt-Omni-Bicycle-People.mp4`, `submitted-source.mp4`, `bicycle-source.mp4`.
- `submitted-prompt.txt`, `trial-ledger.json`, `saved-attempts.json`, `prior-batch-receipt.json`.
- `source-result-comparison.jpg`, `source-contact-sheet.jpg`, sampled full-resolution JPGs.
- `preflight-ready.jpg`, `saved-after-reload.jpg`, `comparison-viewer.jpg`.
- `index.html`, local operator/reconciliation scripts, build and local service logs.

Comparison: http://127.0.0.1:18118/index.html (local-only server).
Actual project: http://127.0.0.1:5184/projects/c4864790-f468-505a-9148-96f7b48022e4 → Project Renders → newest bicycle ride.

Source checkpoint includes only implementation, narrow tests and this note. Generated binaries/QA and operational test data are excluded. No live release implied.

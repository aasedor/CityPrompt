# Local video preview checkpoint

Video now offers **Preview route · free** and **Download preview** before paid
preflight. It reuses the existing deterministic capture, not a second pipeline.
The guide cache includes project, captured view, route, quality and scene
revision. Concurrent requests share one capture; a late result from a changed
scene is rejected. Capture failure permits a manual retry without an automatic
provider call. Route editing and panel closure are disabled during capture.

The capture reports loading/checking/rendering progress. The route image keeps
its aspect ratio when a result appears, with a scrollable panel on laptops.
Video history loading is independent of capture callback changes, removing
repeated history requests observed during the pilot.

## Evidence

- 18 narrow preview-cache, route, deterministic-clock and render-quality tests;
  TypeScript and changed-file ESLint pass.
- Live Gold Standard local preview: 8 seconds, 192 frames, 24 fps, 1920×1080
  H.264, 18,943,377 bytes. No preflight/generate API request or external video
  provider call occurred. Camera position, quaternion, FOV and aspect restored
  exactly; no new browser errors or failed requests.
- Beginning, 25%, 50%, 75% and final frames visually inspected. The authored
  buildings, parks and streets remain stable along the short overhead journey.
  This is a guide-capture pilot, not a professional cinematic output.
- Preview/results UI inspected at desktop; final scroll/aspect layout inspected
  at 1366×768. The latest progress-label and duplicate-history-request corrections
  pass source checks but have not received a second complete capture run.

External evidence: `PHASE12-LOCAL-GUIDE.mp4`, `PHASE12-GUIDE-FRAME-*.png`,
`PHASE12-LOCAL-GUIDE-UI.png`, `PHASE12-PREVIEW-LAPTOP.png` and
`phase12-local-guide.json` in
`C:/dev-artifacts/CityPrompt/student-design-transformation/`.

## Still open

The existing drawn-route controls remain. Exact Start→End saved-camera UX,
Orbit/Reveal presets, semantic Community Tour and provider simplification are
not implemented. No paid video finishing or temporal AI fidelity acceptance is
claimed. Existing prepared-site grounding defects remain visible.

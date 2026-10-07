# Classroom performance checkpoint — 2026-10-05

Scope: lighter device working views and a finite authenticated API-read rehearsal for the planned 40-person class. The instructor identifies Cityprompt.ca on Render as an older deployment. No deployment or hosted load test was performed.

## Device working view

The globe now defaults to Balanced (pixel ratio capped at 1.5), with Economy (1) and High (2). The preference survives reload and remains usable when browser storage is unavailable. Geometry, placement and terrain rules are unchanged. On a device with pixel ratio 2, Balanced draws 56.25% and Economy 25% of the previous maximum screen pixels; this is a pixel budget, not a measured frame-rate improvement. Devices already at ratio 1 have no resolution reduction.

An optional local diagnostics dialog samples frame rate, frame time, screen-buffer dimensions, draw calls and triangles. It runs only while open and sends no telemetry. Slow foreground frames remain in the sample; hidden tabs reset it. The automated Edge session produced a very slow sample (1 frame/s, 250 draw calls, 762,556 triangles in one view). That is a real observation under this automation/session load, not acceptance on a student's laptop. Physical-device moving-scene testing remains necessary.

Current-view stills inherit screen resolution: select High for a sharper still. Video keeps its own Draft/High Quality buffers. Existing/proposed map editing and saved geometry retain their exact coordinates.

## Local 40-account rehearsal

The provisioner refuses ordinary/nonlocal databases and writes private test tokens outside Git. It created 40 distinct disposable zero-credit accounts, each owning one private project with 16 simple saved zones, in `cityprompt_repairs_20261004`. The runner synchronizes 40 clients, performs three rounds of four authenticated GETs and checks each account cannot read another account's project. It never follows redirects, submits writes or invokes providers.

Result: **520 requests, zero failures, 3.98 seconds**. Each read endpoint received 120 requests; all 40 private-project denial checks returned an expected 403/404.

| Endpoint | Median ms | 95th percentile ms | Maximum ms |
| --- | ---: | ---: | ---: |
| Project list | 288.8 | 757.8 | 789.6 |
| Project detail | 215.6 | 508.0 | 541.6 |
| Saved zones | 151.0 | 271.6 | 351.9 |
| Reference layers | 113.0 | 180.2 | 492.0 |
| Other student's project denied | 19.7 | 350.9 | 378.6 |

The local development database pool is 20 plus 10 overflow; production defaults are 5 plus 3. This test does **not** establish Render capacity. Login bursts, writes, compiled mixed scenes, browser asset downloads, classroom Wi-Fi, render queues and 40 physical devices remain outside its scope.

Reproduce with `backend/scripts/prepare_classroom_rehearsal.py` after loading the explicitly isolated local environment, then `tools/classroom_read_rehearsal.py --fixtures <external-private-file> --output <external-report> --clients 40 --rounds 3`. Keep private tokens out of source, screenshots and logs.

## Verification and next hosted gate

Three focused Vitest checks pass, TypeScript and touched-file ESLint pass, and the production build/bundle budget pass (initial JS 460.0 KiB, total JS about 8,082 KiB, CSS 168.5 KiB). Edge verified Economy selection/reload persistence, High/Balanced selection, live statistics, saved project reopening and no captured console errors. Production source remains local; ignored builds and private/generated evidence are outside the committed unit.

Before a classroom rollout, put this reviewed version on an authorized Render staging target, record its actual instance size/worker and database limits, and run a bounded 40-account trial covering sign-in, mixed-scene save/reload and queued presentation. Check at least one basic Windows laptop and iPad Safari with a moving representative scene. Start with still presentations; the new selector is a working-view control, not a promise that hosting can remove client-side WebGL cost.

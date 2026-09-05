# First catalogue cycle: implementation evidence

## CAT-01 / CAT-02 — asset and environment foundation

Implemented locally on `codex/catalogue-runtime-foundation` after the approved next-step plan. No new asset approval or production deployment is implied.

- All ten existing architectural-clay GLBs passed the canonical loader's hashes, media counts and measured native-bounds checks. All thirty catalogue reference hashes and all ten actual independent-review JSON hashes matched the manifest.
- The infill's complete bounds are 8.45 × 11.75 × 6.98001 m. The Craftsman bungalow's complete bounds are 11.84718 × 20.69 × 8.72 m; its declared native occupied floor count is one. Plot defaults must account for complete model bounds, not copy the infill's defaults.
- `tools/catalogue_runtime/prepare_public.ps1` now validates all nine park GLBs against the tracked candidate manifest, carries the manifest/licence, verifies copies, and rejects conflicting output before writes. Hydrated common assets remain explicit read-only directory junctions to the supplied source root. This does not duplicate the whole reference catalogue or conceal that source dependency.
- The reviewed local park bundle is copied into a versioned external runtime folder. Restarting the app no longer requires the `CityPrompt-park` worktree's public overlay. That worktree was only the explicit import source for this first preparation.
- `tools/catalogue_runtime/serve.ps1` rechecks prepared asset hashes before starting Vite. It requires explicit prepared-public and source roots and uses the isolated backend on port 8002 by default. It does not start, reset or migrate a database.

Reproduce preparation with explicit paths:

```powershell
./tools/catalogue_runtime/prepare_public.ps1 -SourceRoot '<hydrated-source-checkout>' -ParkPublicRoot '<candidate-public-root>' -OutputRoot '<external-runtime>/public' -DryRun
./tools/catalogue_runtime/prepare_public.ps1 -SourceRoot '<hydrated-source-checkout>' -ParkPublicRoot '<candidate-public-root>' -OutputRoot '<external-runtime>/public'
./tools/catalogue_runtime/serve.ps1 -PreparedPublicRoot '<external-runtime>/public' -SourceRoot '<hydrated-source-checkout>'
```

The local prepared root is `C:/dev-artifacts/CityPrompt/catalogue-cycle-2026-09-05/runtime-v1/public`. The existing isolated backend/storage/database remains in use. A portable fresh-machine database/bootstrap package is outside this preparation change and is not claimed complete.

Browser verification used the existing empty-field project `de492723-417b-4729-a76c-f797cc8528d6` through login and reload. The app displayed both current picker cards and returned HTTP 200 with the expected bytes for the prepared pavilion and bungalow reference. No browser errors were recorded. Shared ground reached ready with two passes. This baseline contains the previous four infill instances and one park; it is not the planned five-choice completion trial.

A three-second warmed stationary observation recorded 170 frames, mean 17.74 ms and p95 18.10 ms, with approximately 224 MB used JavaScript heap. It is not an orbit benchmark, total GPU/browser memory measurement or validation of the larger stress fixture. The source of browser resource timing did not report prior GLB downloads, so no cold download-time result is claimed.

Source changes are the two runtime preparation/start scripts and this progress record. Audit JSON, timing/camera data and screenshots are ignored under `artifacts/catalogue-cycle/`; copied model assets remain external. No paid image/video calls were made.

## CAT-03 — site-bounded ground continuity

Implemented on `codex/catalogue-ground-continuity`. A fixed, site-sized orthographic selection camera now requests terrain coverage for the entire sampling grid while the student views the site from ground level. It selects tiles but does not create a second rendered viewport or supply substitute elevations. Its resolution is capped at 1024 pixels per dimension and it is removed when its provider/site unmounts. Real tile changes intersecting the site still invalidate sampling and capture; off-site events no longer clear an already measured surface.

Before the fix, the recorded 1.7 m pedestrian-camera test became unavailable after four passes, with 102 missing samples. The equivalent post-fix test remained ready with zero missing samples. A fresh renderer reload with the test harness holding the camera at 1.7 m progressed from sampling to ready, also with zero missing samples; browser network caches were retained. The harness held the view because normal startup restores an aerial camera. Final evidence records 1,190 samples, two stable passes, zero maximum between-pass delta and approximately 0.165 m local residual. These are visible-tile stability/contact measurements, not survey accuracy or validation of arbitrary terrain.

Twenty-six targeted tests passed across provider lifecycle, selection coverage, sample quality, triangulation and capture guards; TypeScript checking and scoped ESLint passed. Tests include off-site event retention, selection-camera cleanup and source-geometry invalidation. Browser errors were empty. The stricter capture guards remain unchanged: actual relevant terrain refinements require a fresh, complete two-pass surface.

Before/after observations and images are ignored under `artifacts/catalogue-cycle/`, including `pedestrian-before.json`, `pedestrian-after.json` and `cold-pedestrian.json`. The initial broad warmed orbit/scene benchmark still needs a final comparison after all five choices are integrated.

## Remaining work

CAT-04 detached-home pair integration, CAT-05 new duplex, CAT-06 park refinement, CAT-07 sourced street placement and CAT-08 full novice trial remain pending. The accepted scope and exact candidates are unchanged.

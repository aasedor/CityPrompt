# Street preview recovery — 2026-10-02

## Findings

The normal catalogue drawing code had not reverted relative to the recent reference-fourplex checkout. The local previews on ports 5195 and 5196 used a public asset directory containing Git LFS pointer files and missing native street modules. That caused broken catalogue images and unavailable detailed geometry.

The raised-road terrain rehearsal is a separate development preview. It is not yet connected to ordinary catalogue route drawing. Native streets that require prepared level ground still require that preparation; this change does not bypass their ground or route validation.

A separate rendering defect affected live Amsterdam canal drafts: the prepared site surface covered the below-grade water. Saved canals already had a ground opening, but drafts did not.

## Source changes

- Show the preparation requirement immediately when a native street is selected, before drawing points.
- Provide a Review ground action, retain draft points during review and on closing it with Escape, and disable completion until the preparation requirement is satisfied.
- Avoid repeated validation toasts on repeated completion attempts.
- Try distinct catalogue image fallbacks and display a readable placeholder if all fail.
- Open the prepared surface beneath valid canal drafts, clear the opening on cancellation or invalid geometry, and prevent exporting an unsaved draft opening.
- Label the terrain rehearsal as a temporary preview with separate catalogue ground requirements.

## Local asset recovery

Exact assets were recovered from local LFS objects and existing approved asset outputs. Native module hashes were checked against their locked hashes. No models or images were regenerated or substituted.

Recovered assets, scripts, and browser evidence remain outside Git:

`C:/dev-artifacts/CityPrompt/road-trial-ui-recovery-2026-10-02/`

The corrected public asset root is that directory's `public/` subdirectory. The source tree's original asset pointer files were preserved. This source commit therefore does not itself hydrate another checkout or deployment.

Run the corrected preview from this worktree's `frontend` directory in PowerShell:

```powershell
$env:API_PROXY_TARGET='http://127.0.0.1:8018'
$env:VITE_ENV_DIR='C:/Users/andre/OneDrive/Documents/CityPrompt/frontend'
$env:CITYPROMPT_PUBLIC_DIR='C:/dev-artifacts/CityPrompt/road-trial-ui-recovery-2026-10-02/public'
$env:CITYPROMPT_TERRAIN_TRIAL_DIR='C:/dev-artifacts/CityPrompt/fresh-road-trial-2026-10-02'
node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 5197 --strictPort
```

Restart Vite after adding assets to this external public directory; its public-file inventory is built at startup.

## Verification

- 58 Vitest tests passed across pickerHeroImages, GlobeStreetDrawingPreview, nativeStreetProgram, elevatedRailProgram, elevatedRailStations, roadTerrainTrialController, and streetGroundCapture.
- `npm run type-check` passed.
- All 31 street catalogue images decoded successfully in the browser.
- Ordinary BRT card selection and pointer drawing: early ground guidance, disabled completion, retained three-point route across ground review and Escape, explicit preparation, detailed draft, save, and reload passed. Draft contained 12 meshes and 62 instances.
- Amsterdam canal: detailed draft with visible water, 31 meshes and 34 instances; draft cutout and capture guard verified.
- Planted Shared Lane: detailed draft with 20 meshes and 340 instances.
- No page errors or relevant asset response failures were recorded in the successful browser runs.

Browser setup created disposable QA projects. It did not modify the user's existing project or draft. The latest BRT test project is `b80bf184-5f80-46ec-8a69-f801f05e8425`.

Evidence includes `ui-result.json`, `more-drafts-result.json`, `catalogue-restored-final.png`, `brt-saved-reloaded-final.png`, `canal-live-3d.png`, and `planted-live-3d.png` in the external directory above.

## Remaining work

Integrating the raised-road ground reconstruction into normal catalogue drawing remains a separate implementation task. These checks establish the supported prepared-site workflow; they do not establish seamless placement of all native streets directly on untouched Google tiles.

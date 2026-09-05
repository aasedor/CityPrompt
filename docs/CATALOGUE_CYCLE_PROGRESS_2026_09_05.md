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

## CAT-04 — detached-home pair integration

The picker now includes the reviewed `vancouver_craftsman_bungalow / craftsman_classic`. Its 15 × 24 m plot minimum contains the complete 11.84718 × 20.69 m delivered envelope with at least 1.5 m conceptual clearance per edge; these are placement clearances, not legal setbacks. The infill retains its existing dimensions. Preview requests and their cache identities now include the exact selected variant, authored floor count and native-plot policy. Loading/error previews use a wireframe of that asset's native envelope. Reshape instructions are asset-specific, and the card list scrolls independently of status/actions.

Browser testing placed, rotated and duplicated the bungalow on the existing empty-field fixture, rejected a 5 m plot width, and reloaded the exact saved variant. Live local planner requests returned one native assembly at each default size; at 36 m width, three infills or two bungalows, all at scale `[1,1,1]`. Seventeen targeted tests, TypeScript checking and scoped ESLint passed. No new building model was promoted in this step.

One rapid rotate/duplicate sequence displayed an update error and lost selection; a reload recovered the persisted models. The error response was not captured in that initial run. Subsequent instrumented rotation and duplicate trials returned no failing API responses and retained the reshape panel. This intermittent finding remains open for CAT-08; the collection is not marked release-complete. Large repeated bungalow placement through the UI, move/undo/redo, narrow-screen verification and integrated ground-contact review remain part of that trial. Evidence and scripts are ignored under `artifacts/catalogue-cycle/`.

## CAT-05 — exact duplex clay candidate

Implemented on `codex/catalogue-duplex-clay-pilot`. The new source-specific
`calgary_modern_infill_house / infill_duplex` is constructed from its three
locked catalogue views. Those pixels show two visible storeys with dark brick,
cedar entry recesses, paired front glazing and two flat roofs; conflicting
three-storey/stucco catalogue prose is recorded, not used to change the model.

Four finite local candidates are preserved externally. Version 004 passes
the complete separate architectural-clay review with zero unresolved P0/P1.
The review closed overlapping entrance/slab surfaces, missing near-grade
glazing and an unsupported central roof cap. All 13 views came from the actual
GLB reimport. Source/script hashes, texture-free export, finite/nondegenerate
geometry, physical carrier apertures, framing and unchanged roundtrip bounds
pass deterministic checks. This does not grant textured-keeper status.

The GLB is 3,110,128 bytes with complete dimensions 13.34 × 21.472 × 9.0 m.
It represents one fixed two-home assembly. A proposed 17 × 25 m plot leaves
conceptual clearance, but native placement and terrain contact remain to be
verified. No runtime seed or catalogue activation has occurred. The concrete
candidate, exact source/model/review hashes, replay instructions and independent
review are recorded under `tools/catalogue_duplex_pilot/`. Heavy sources,
Blender files, GLBs and review images remain outside Git at
`C:/dev-artifacts/CityPrompt/catalogue-cycle-2026-09-05/duplex/`.

## CAT-06 — adaptive park planting and export contact

Implemented on `codex/catalogue-park-planting-pilot`. The v5 candidate improves
the tree crowns, branching and meadow scale while preserving the exact rustic
park's lawn, loop and metric equipment programme. Actual-vertex export
verification discovered and fixed a 0.357923 m boulder grounding error in the
inherited kit. All four rocks now contact their declared plane. Nine GLBs total
4,722,724 bytes; rejected v3/v4 output is retained externally.

Ten targeted geometry/layout tests, TypeScript and scoped ESLint passed.
Actual exported bounds, hashes, ground contacts and alpha-mask contracts pass.
Nine browser lab cases were visually inspected: standard aerial/overhead/
pedestrian/detail, 3% slope, compact, large, rotated-L and too-narrow. An 8 × 80 m
site explicitly omits equipment instead of stretching it. The 40 × 35 m case
retains two equipment modules; standard and large retain four. Fresh interaction
errors were empty; the historical global browser error buffer is not cleared
evidence. See `tools/neighborhood_park_pilot/README.md` for reproduction and limits.

The integrated empty-field scene loaded all nine v5 assets with correct sizes
and GLB signatures. Aerial and 1.7 m views were inspected. Relevant Google tile
refinement briefly returned shared ground to sampling, then ready with two
passes and zero missing samples. Final street connections, performance and
student interaction checks remain in CAT-07/08. Candidate assets are external
under `C:/dev-artifacts/CityPrompt/catalogue-cycle-2026-09-05/park-v5/`; the current
prepared runtime is `runtime-v4/public`. No production activation is implied.

## Remaining work

CAT-05 authoring/review is complete; exact-candidate activation and integration
remain. CAT-06 refinement is implemented; CAT-07 sourced street placement and CAT-08 full
novice trial remain pending. CAT-04 is implemented with the above release checks
still open. The accepted scope and exact candidates are unchanged.

## CAT-07 — Calgary local route pilot

Implemented on `codex/catalogue-calgary-local-street`. The primary street button
now selects the existing `calgary_local / calgary_local_v0`, with its 16 m width
and draft Street Manual source visible. The native section is chosen before
buffering the first line. Its route points are persisted before compilation;
the drawing exits to Select after completion. Rejected routes retain their
points and give an explanation. A compact street panel exposes route handles,
an Add bend point action and the existing advanced catalogue. Width remains
16 m while this exact pilot is selected.

Metric normal/miter calculations fix diagonal route widths. Coordinate saves,
undo and redo update the buffer and persisted centreline atomically, preventing
a compiled street from remaining at its previous location. The access solver
can cross the section's 0.3 m outer sidewalk margin; carriageways, cycle bands,
parking and planted bands still block an approach. This is geometric connection
logic, not construction or parcel permission. Tight switchbacks and segments
under 16 m produce an explicit pilot limitation.

The real UI created a straight 68 m street on the empty-field fixture, added a
bend point and moved its end north. Its exact variant and 16 m section compiled
successfully. Undo restored the straight route; redo and reload restored the
same bent centreline and polygon. A rejected 8 m attempt kept its drawing and
showed the minimum-length message. The older test road was deleted through the
keyboard. UI tooling dismissed its native delete confirmation, so that button
path is not claimed verified. Source edits during Vite HMR temporarily left
stale canvas listeners; the recorded drawing/edit trial used a full reload.

126 targeted tests across nine files passed, including metric diagonal/bend
widths, atomic undo, near-side access, unsafe crossings, section contracts and
shared ground. TypeScript and scoped ESLint passed. The asset-integrity suite
requires `CITYPROMPT_PUBLIC_DIR` pointing to the explicit prepared runtime;
the first run without it failed on absent local public assets, and the correctly
configured run checked the actual sources successfully.

Current street ID: `97f304f2-adbd-4d69-af30-a8361b8893f8`. UI images and saved
route/undo evidence are ignored under `artifacts/catalogue-cycle/street-*`.
Full pedestrian park/street contact remains part of the integrated CAT-08
trial. That trial also found a 40 × 30 m park returning an unexplained empty
lawn; this is recorded for correction before release. No paid calls or
production publication occurred.

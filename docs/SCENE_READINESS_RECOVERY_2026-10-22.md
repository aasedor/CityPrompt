# Scene readiness recovery — 2026-10-22

Local implementation and verification on `codex/scene-readiness-recovery`, based
on `origin/deployment-version` at `6fb1a885e93d431322cf58d7548ea5671aa0fa6b`.
This report does not establish production deployment of these changes.

## Confirmed causes and fixes

- A native constant-width street with a small bend was measured using its
  enclosing rectangle. A real 18 m section could therefore fail its fixed-width
  contract and fall back to a representation the native renderer cannot execute.
  The planner now attests the complete footprint against its validated metric
  centreline ribbon in both directions. Falsified widths still fail. The existing
  longitudinal target calculation and valid saved recipe identities are retained.
- An automatic update failure could survive Undo restoring an already compiled
  scene, or deletion of the last failed object. Completed-scene restoration now
  clears the obsolete error; empty scenes clear error/busy state, including when
  an obsolete request finishes afterward. Genuine asset-load errors still apply
  to the affected current object and revision.
- A details-only scene inside a new default-off parcel never runs physical-zone
  compilation, so it never receives that compiler's explicit no-landscape marker.
  Workflow, browser capture and server admission now agree that an absent recipe
  and absent/placed-objects-only mode need no residual landscape. An explicit
  automatic-tree request, generated/automatic mode, non-null stale or malformed
  recipe, or a supplied residual claim still requires normal validation. Saved
  detail revisions, instance ownership, physical source/representation hashes
  and duplicate-boundary checks remain enforced.
- A genuine incomplete object now gets a named, actionable explanation instead
  of the generic post-compilation error. This is additional diagnosis, not an
  exemption from capture admission.

## Verification actually run

Failing regressions were observed before each behavioral fix.

- Backend: `python -m pytest tests/test_public_realm_lego.py
  tests/test_community_3d_scope.py tests/test_lego_assembly.py
  tests/test_building_community_freshness.py tests/test_direct_3d_render.py -q
  --tb=short` — **543 passed**. Existing dependency/Pillow deprecation warnings.
- Frontend: focused pickPlace, community3d, legoAssembly and workflow directories,
  plus streetLegoContract, nativeStreetReadiness and residualLandscape tests,
  with `--maxWorkers=2` — **1,132 passed, 95 files**. After the final effect
  dependency adjustment, the touched hook/workflow files were rerun: **45 passed**.
- `npm run type-check` — passed. `npm run build` — passed on the final source,
  using the existing hydrated public directory and production catalogue packet.
  Existing bundle-size and mixed dynamic/static-import warnings remain.
- Targeted ESLint — no errors; existing visibility dependency warning in the
  automatic-update hook remains. `git diff --check` — passed.
- Independent read-only code review found an initial cross-layer details gate
  mismatch; it was corrected and re-reviewed with no remaining confirmed blocker.

The interrupted pre-restart broad test run is not counted as a pass. Its worker
timeouts were replaced by the complete successful rerun above. An initial build
without the checkout's hydrated asset directory failed correctly; no asset guard
was disabled to obtain the subsequent passing builds.

## Actual local browser trial

Disposable project: `http://127.0.0.1:5184/projects/f2aa488c-4fd3-4f52-9a10-d79d32d1f61a`.
Location: a downtown Calgary parking lot near 600 3 Street SE.

1. Drew and saved a new parcel through the UI; automatic site trees remained off.
2. Placed one independent timber bench. The details-only site enabled Image and
   free video preparation. Exact image export completed without an AI call.
3. Opened the saved project in a fresh tab: one placed detail persisted. Repeated
   exact image capture successfully after reload.
4. Drew a gently bent Quiet Residential Street through the UI. It compiled and
   displayed its native pavement, sidewalks, planting and furniture as `3D saved`.
5. Undo removed the street and returned to the details scene without a stuck
   readiness failure. Redo restored the street and reached `3D saved`.
6. Selected the street, confirmed the 18 m section, and applied it unchanged.
   Read-only local database inspection confirmed `state=compiled`, target width
   18 m and target length 112.938 m after editing; the stored route has 8 stations.
7. Reloaded again: `3D saved` and `Drawings saved`. Exact image capture completed.
8. Recorded a free four-second aerial route preview. Video preflight returned
   `Ready · 1280×720 · route-video edit · gemini-omni-1.1-flash` and HTTP 200.
   Saved preview: H.264, 24 fps, 96 frames, exactly 4 seconds; full FFmpeg decode
   passed. This is a readiness trial, not a paid video fidelity assessment.

No browser console errors were captured at the final check. Optional public-road
suggestions returned an OSM context 503 during the trial; manual street drawing
and subsequent compilation/capture still worked. No paid image/video generations
or additional provider credits were used. Existing live projects were untouched.

## Evidence and limits

Screenshots, exact captures, preview MP4, sanitized preflight DOM and read-only
persisted scene evidence are outside Git in:
`C:/dev-artifacts/CityPrompt/downtown-new-user-trial-2026-10-22/readiness-*`.
The minimal anonymized original failing street footprint is an intentional test
fixture at `backend/tests/fixtures/downtown_bent_street.json`.

Failures caused by missing model bytes, unsupported geometry, unsaved changes,
stale generated landscapes or unavailable terrain remain real blockers. They
are not waived by this fix. Forced failed-request races were regression-tested
automatically; the browser trial exercised normal placement/edit/undo/reload.
This is not an exhaustive audit of every archetype, device or network failure.
Hosted verification and publication of this fix have not been performed.

Pre-existing hydrated LFS changes and all unrelated work were preserved; no model
binaries, catalogue activations, database migrations or LFS policy were changed.

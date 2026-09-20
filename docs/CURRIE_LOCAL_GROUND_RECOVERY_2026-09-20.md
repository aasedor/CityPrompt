# Local natural-ground recovery — 20 September 2026

## Result and practical limit

A repeatable rough patch no longer disables all natural-ground authoring.
The shared provider retains measured heights and marks unsupported grid cells.
Buildings and draped surfaces can use the remaining coverage. Objects crossing
holes remain unresolved; their saved geometry is preserved. This is interactive
recovery, not a whole-site ground pass or a completed classroom presentation gate.

Both complete passes must still be physically plausible and agree within 0.08 m
at every vertex. Existing slope (0.45) and local residual (0.6 m) limits remain.
The union of either pass's rejected cells is excluded. Residuals exclude all four
cells using the suspect vertex; steep triangles exclude their cell. Sampling
returns null within holes and on their shared edges, preventing a large footprint
or draped face from bridging a hole with valid distant corners. No heights are
smoothed, replaced, flattened or inferred. Missing/unstable/implausible passes
still fail globally. If every supported cell is rejected, recovery fails.

`SharedSiteGroundSnapshot.excludedCells` uses cell indices with columns-minus-one
stride and participates in the signature. `contains` continues to mean site
ownership; consumers must use `heightAt` for support. This prevents unsupported
objects from falling back to legacy ground because they appear outside the site.
The strict snapshot factory, survey pipeline and prepared-ground inspection
remain strict. Street extensions cannot independently resample/reclassify a
rejected anchor region. Generated residual trees omit unknown contacts instead
of substituting the frame height. Existing revision/capture freshness guards stay.

Review ground outlines excluded cells and offers boundary recovery. A persistent
message explains partial coverage. Exact export and other guarded captures reject
partial snapshots at entry and completion, so hidden proposal pieces cannot become
an apparently successful render. This conservative restriction includes rough
patches unused by any object; per-proposal export coverage remains follow-up work.

## Bounded live pilot

- Worktree: `C:/dev/CityPrompt-grounding-edit-race`; branch
  `codex/grounding-edit-race-hardening`; local frontend port 5174.
- Disposable student project: `0320bb4f-395c-41c6-a6c0-ad28bb1572ef`.
- Protected original: `f5bffc94-def9-4c43-942e-9ae7411872e9`; unchanged against
  both this turn's baseline and the previous student-project baseline.
- Saved a pre-test backup, then used Review ground → Follow existing terrain.
  No API-authored object geometry, numerical correction or threshold change.
- Reproduced the exact earlier residual: 0.62321911505137 m; maximum slope
  0.4339875386676033; 1,155 samples; two passes; maximum delta 0 m.
- Eight excluded cells: 605, 606, 637, 638, 998, 999, 1030, 1031. The native house
  and street remain visible, including after reload. Inspected screenshots and
  native mesh presence. This does not certify the park's full natural-ground
  rendering; the rough patch near the park still needs recovery.
- Review map outlines both rejected areas and names eight unavailable cells.
- Ordinary free-export action shows the explicit partial-ground error; no
  Download render link. No paid generation was attempted.
- Reload preserved every non-boundary zone record and boundary coordinates.
  Only the explicitly requested ground-mode change persists. The fixture now
  remains in **natural mode**, superseding the previous prepared-mode handoff.
- House contact is supported, but the previous approximate entrance still reports
  `entrance_anchor_not_at_edge`. This is a separate unresolved authoring issue.
- No browser page errors during export/reload verification. Viewport 1440×900,
  headless Chrome/SwiftShader, normal Focus plan view. Not a low-view visual pass.

## Verification and evidence

76 tests in 10 narrow suites passed: partialSharedSiteGround, sharedSiteGround,
sharedGroundCapture, sharedGroundGeometry, buildingGroundContact, GroundReviewPanel,
groundReview, streetGroundExtension, AutomaticParkGround and parkTerrain.
TypeScript checking and lint of changed files passed. Tests include a numerical
Currie-sized residual, missing/root/unstable passes, all-rejected terrain, both-pass
coverage identity, building interiors and thin crossings, draped park/street faces,
UI recovery and capture entry/completion rejection. React changes keep hooks
unconditional, reuse existing disposal/revision logic and preserve accessible
recovery controls. No asset or backend changes.

External evidence root: `C:/dev-artifacts/CityPrompt/grounding-batch-a/`.
`local-ground-evidence-sha256.json` records hashes for raw state, before/reload
readback, export rejection and inspected images. Raw failed baseline remains in
`student-residual-blocker.json`. Evidence is local, outside Git; no publishing.

## Next checkpoint

1. Fix entrance authoring/readiness for both natural and prepared sites and test
   the complete connection through ordinary controls on this fresh project.
2. Complete usable park/partial-ground recovery and capture coverage. Avoid making
   a tiny unused patch a permanent export blocker, but require current complete
   evidence for every actual proposal surface before relaxing the capture guard.
3. Continue the control, presentation and catalogue-entry pilots in
   `CLASSROOM_READINESS_PLAN_2026-09-20.md`. Do not restart detail perfection work.

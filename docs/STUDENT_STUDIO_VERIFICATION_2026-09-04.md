# City Prompt student studio — implementation and verification

This is a local implementation on `codex/student-studio-2027`, based on `679b76a35`. It is isolated from the owner's pending RLASM/ground work. No deployment or push is part of this checkpoint.

The [implementation plan](STUDENT_STUDIO_IMPLEMENTATION_PLAN.md) records the full product vision, January teaching schedule and work still needed. The [browser record](STUDENT_STUDIO_BROWSER_VERIFICATION_2026-09-04.md) and [media record](STUDENT_STUDIO_MEDIA_FIDELITY_2026-09-04.md) give detailed evidence and practical limits.

## What changed

- Students enter through Building, Park and Road, with a compact Layers / Report / Team / Help area. The map no longer covers the application header. Extra controls remain available without occupying the first-use toolbar.
- Zoning and other reference data have their own persisted records and import route. Geometry and attributes can be inspected, hidden and reopened without creating proposal buildings. Elevation is optional, sourced and explicitly approximate; provider failure never becomes a purported zero-height measurement.
- The planning report stores the proposal it assessed, measured quantities, advisory findings, source context, unanswered questions and student decisions. Students can adopt, adapt or decline advice with their own rationale and export a printable plan/report. The report does not block design. Switching projects immediately clears the previous report panel; late saves, report requests and exports cannot replace the new project's report, clear its busy state or trigger an old download.
- Failed new drawings retain a stable request ID and a recoverable draft. Repeated submissions cannot duplicate a saved drawing. Definitively rejected drawings can be explicitly discarded; uncertain saves remain recoverable. Failed existing edits stay visibly unsaved until that drawing saves or the saved version is explicitly reloaded. Updates/deletes and undo use revision checks; changing projects clears the previous project's undo scope. Saving feedback includes geometry moves and distinguishes persistent drafts from memory-only drafts.
- Invited users explicitly accept membership. Accepted viewers see a read-only plan/report/media experience. Public presentation links are revocable and do not grant editing access. Protected images and GLBs use short-lived project or exact-file tickets, without putting account login tokens in their URLs. Tickets renew during long sessions and on return to the tab.
- The unused legacy WebSocket relay no longer accepts anonymous project connections or relays self-identified edits. Optional live presence/edit broadcasting is paused; authenticated project sharing and revision-checked saves remain available.
- Render credit admission/refunds are transactional. Viewers cannot create or change project media. Images/videos and project/file access use the corresponding read or edit permission rather than inconsistent owner-only or unrestricted paths.
- Known detached-house archetypes repeat separate native houses inside the actual drawn plot, including concave plots. Family floor bounds remain enforced. The report counts compiled dwellings without treating the surrounding plot and yards as floor area.
- Concave tile masking retains the actual notch. Depth/normal capture respects the same masking; depth survives PNG conversion. Capture waits for stable visible tiles rather than unrelated background refinement. Same-camera presentation checks preserve source geometry conservatively and save original AI attempts separately. Every generated presentation still needs review.
- Contained buildings, street sections, park props and residual planting use the prepared boundary's shared elevation. They no longer independently seat themselves on Google roofs that the proposal has removed. Whole-edge containment preserves terrain for objects outside the site or across a concave notch; the replacement ground sits just below authored surfaces so it cannot cover the road.
- The server records the rendered plan/camera snapshot and fingerprints. Saved Direct3D responses retain that provenance through the frontend instead of being saved again as anonymous image copies.
- The 3D editor and staff pages load on demand. The main application entry chunk changed from approximately 5.89 MB to 0.31 MB before compression in local builds; shared/vendor and editor chunks still exist. This is a bundle observation, not a measured page-load or classroom performance claim.

## Checks

| Check | Result and scope |
| --- | --- |
| Combined frontend regressions | Final checkpoint: 366 passed across 32 files, including drawing/form recovery, undo, ticket rotation, detached placement, references, report, sharing, guide, toolbar, street/park contracts and capture/ground masks. This replaces the earlier 342-case run and includes saved-presentation labels, the closed collaboration adapter, seven outside-site draft recovery cases and nine report lifecycle cases |
| Additional focused LEGO frontend checks | 71 passed across five files during integration; overlaps some combined cases, so do not add totals |
| Tile capture readiness | 15 tests passed, including visible-set stability while off-view work continues and rejection of empty/continually changing coverage |
| TypeScript / lint | Final integrated `npm run type-check` passed. Final scoped ESLint passed across all 86 changed TypeScript source/test files |
| Production frontend | Vite production build passed. Large editor/vendor chunk warnings remain. Large public assets were reused for local testing and deliberately not copied into the generated bundle artifact |
| Backend regressions | 535 distinct cases passed across the asset-backed LEGO, trust, render, reference, report, viewer-media and closed-collaboration suites. The final source-strategy persistence fix passed 156 render/prompt/provenance cases (overlapping the earlier suite); exact commands belong in the detailed records |
| Unused live collaboration relay | Seven backend handshake/ASGI cases and five frontend adapter cases passed. The route refuses connections before accepting or reading data, and the client opens no socket or reconnect timer. Existing authenticated sharing/save checks also passed |
| Database behavior | Real isolated PostgreSQL probes cover simultaneous credit admission, daily cap, once-only refunds, duplicate save IDs, conflicting request IDs, stale updates/deletes, invitation acceptance and revocation |
| Migrations | Both new migrations upgraded/downgraded/upgraded in a separate disposable database; indexes and deletion relationships verified without touching browser test data |
| Browser | Real UI → API → database → reload checks passed for reference import, report decisions/export, invitation/login/acceptance, read-only access, anonymous/expired-login public access, revocation and optional elevation. Final actual toolbar/map clicks created a boundary, building, park and road; a building property edit saved, and all four complete records matched exactly after reload. A report generated successfully from that nonempty plan |
| Real WebGL capture | Explicit L-shaped cut geometry agrees with the actual clipping shader/depth/normal passes apart from boundary rasterization pixels; decoded depth and normal samples match expected camera values |
| Paid image lifecycle and recorded replay | One real image request completed; the drift checks returned the source. Local replay of that saved AI attempt verified stable source-fallback labels, a separate artifact from the earlier mock, credit audit, gallery, PNG/sidecar provenance and scoped downloads |

## Local runtime and evidence

- Frontend: `http://127.0.0.1:5175`; isolated backend: `http://127.0.0.1:8001`.
- Example account: `studio-smoke@example.com`, password `Studio-local-2027!`. This is an isolated test account, not a production login.
- Review project **Studio drawing and reload acceptance — local QA** (`32b52157-4f5c-4b87-866f-87b9ca8e1405`) contains the actual UI-drawn four-zone plan and its report. **Studio 3D source fidelity — local QA** (`2e9d03e2-d212-48c7-8937-1e2c25226276`) contains the separate approved-bungalow media pilot and its saved source/AI attempts.
- PostgreSQL: port 55432; Redis: 56379; MinIO: 59002, all bound to loopback. The local harness overrides production database/storage settings. Image/video provider credentials remain disabled in the running browser backend.
- The isolated backend was restarted after the browser exercise. Its health check returned `healthy`; an actual anonymous WebSocket upgrade request to the legacy relay returned HTTP 403 before connection acceptance. Evidence: `backend-checkpoint-health.json`.
- The example project and visual pilot are synthetic local fixtures. The approved bungalow GLB used in the visual pilot was copied unchanged into isolated storage after its source hash was checked. No asset family was generated or promoted to the original runtime catalogue.
- Scripts, screenshots, capture PNGs, provider-test ledgers, database probes and production bundles live under ignored `artifacts/student-studio/`. None are source deliverables or intended for staging.
- Final frontend logs are `frontend-checkpoint-tests.log` (366/32), `frontend-checkpoint-types.log`, `frontend-checkpoint-lint.log` (86 files) and `bundle-checkpoint.log`. Actual drawing/report screenshots and complete save/reload snapshots are in `media-fidelity/drawing-ui/`. The drawn plan's report measures a 13,052.63 m² site, 118.25 m² park, 59.78 m² street/path area and 359.37 m² known building footprint; these are conceptual drawn geometry quantities, not a surveyed design.

## Image/video spending and visual pilot

The user authorized **US$10 total** for live image/video tests. The finite pilot permits one square 1024 image request, with bounded inputs and no retries. Its separate process uses the existing OpenAI key with the isolated application/database/storage and records provider usage; the normal local backend remains disabled for image/video spending.

A complete **$0 mocked-provider rehearsal passed** through the actual API, credit audit, PostgreSQL, MinIO, gallery listing, protected downloads and embedded/sidecar provenance. Both the original AI attempt and returned presentation were saved. Downloaded bytes matched storage, anonymous access was denied, exact-file tickets could not read another file, and saved plan/camera hashes matched their snapshots. This verifies the lifecycle; the echoed mock image is not visual-quality evidence.

**One paid image request completed, with an estimated US$0.280668 cost at the published uncached rates**, based on the provider's returned usage: 7,936 image-input tokens, 1,292 text-input tokens and 7,024 image-output tokens. This is a usage-based estimate rather than a settled billing statement. No video or retry was submitted; the remainder of the authorized US$10 was not spent on image/video tests. The usage ledger is `artifacts/student-studio/live-generation-ledger.json`.

The provider returned a more finished image but enlarged/redesigned the bungalow and changed park/road details. The generic silhouette, instance and unsupported-structure checks failed, so the returned presentation kept the clean 3D source. Independent visual review agreed. **This is a successful conservative fallback, not an approved polished render or proof of solved generative consistency.** The fixture is an unchanged approved bungalow assembled through LEGO, without the additional server-certified RLASM pixel-restoration claim.

The paid result exposed a saved-image deduplication/label bug: identical source pixels could reuse a prior mock's different presentation treatment, and a compound outcome string hid the review badge. The fix separates stable outcome from `presentation_strategy`, normalizes historical labels on read, and includes treatment/provenance/settings in deduplication. A local replay of the stored AI attempt verified the corrected behavior without another provider call. Paid and replay evidence are in `media-fidelity/live/` and `media-fidelity/replay-live/`.

Automatic approval review initially stopped submission on a possible sensitive-upload concern. A local interception audit recorded the exact outgoing form/images and established that the scene was newly created synthetic QA content over public map context, with no student/production project data. Re-review allowed the single bounded call. The initial rejection sent nothing externally.

## Limits and next review

This is a substantial first implementation, not a finished January release or a claim of perfect generative fidelity. It still needs an observed novice exercise, a 60-account classroom rehearsal, real laptop/network testing, and review of the original branch's pending 3D changes before integration. Runtime assets and generated media are separate from the source checkpoint.

Before production rollout, complete the inherited authentication and operational review, including OAuth state validation, video reservation/accounting and worker configuration. The closed legacy collaboration channel needs a fully authenticated implementation before live presence or edit broadcasting can return. These are explicit release work, not assurances supplied by passing the local studio tests.

The interactive walkthrough, guided sketch/custom-model import refinements and complete video provenance extension remain in the implementation roadmap. Existing image/video features are retained, but local unit tests cannot certify their visual fidelity. Missing approved building families still need truthful massing or the established human visual-review process. Dense boundaries beyond the current GPU masking capacity retain context instead of silently erasing it.

The shared prepared grade is a conceptual flat site surface, not a terrain-engineering model. Roads that straddle the boundary still use the existing draping path; transitions to the prepared grade need further work. An approximate elevation API datum can differ from the visible Google mesh. Actual drawing records clicked surface heights, while scripted/imported sites may need grade calibration. Roof clicks and steep sites require additional terrain review before a classroom release.

For local rollback, retain this branch/worktree and return to the original checkout. Before a deployed release, back up the database, rehearse the documented migrations and test the final merged state; no deployed data has been migrated here.
